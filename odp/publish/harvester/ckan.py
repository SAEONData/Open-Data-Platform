import json
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.sql import text

from odp.api.models.catalogue import CatalogueRecord
from odp.publish.harvester import Harvester


class CKANHarvester(Harvester):
    def __init__(
            self,
            db_url: str,
            db_echo: bool,
            batch_size: int,
            harvest_check_interval_minutes: int,
    ):
        self.engine = create_engine(db_url, echo=db_echo)

        # runtime type checks to safeguard against SQL injection
        if not isinstance(batch_size, int):
            raise TypeError
        if not isinstance(harvest_check_interval_minutes, int):
            raise TypeError

        self.select_records = text(f"""
            SELECT p.id, p.private, p.state, p_doi.value doi, p_sid.value sid, p_json.value metadata,
                   g_inst.name institution_key, g_coll.name collection_key, g_coll.id collection_id,
                   ms.name schema_key
            FROM package p JOIN package_extra p_doi ON p.id = p_doi.package_id AND p_doi.key = 'doi'
                           JOIN package_extra p_sid ON p.id = p_sid.package_id AND p_sid.key = 'sid'
                           JOIN package_extra p_json ON p.id = p_json.package_id AND p_json.key = 'metadata_json'
                           JOIN package_extra p_coll ON p.id = p_coll.package_id AND p_coll.key = 'metadata_collection_id'
                           JOIN package_extra p_schema ON p.id = p_schema.package_id AND p_schema.key = 'metadata_standard_id'
                           JOIN "group" g_inst ON p.owner_org = g_inst.id
                           JOIN "group" g_coll ON p_coll.value = g_coll.id
                           JOIN metadata_standard ms ON p_schema.value = ms.id
            WHERE p.last_publish_check IS NULL
               OR current_timestamp - p.last_publish_check > interval '{harvest_check_interval_minutes} minutes'
            LIMIT {batch_size}
        """)

        self.select_projects = text("""
            SELECT g.name project_key
            FROM "group" g JOIN member m ON g.id = m.group_id
            WHERE g.type = 'infrastructure'
              AND g.state = 'active'
              AND m.table_name = 'group'
              AND m.table_id = :collection_id
              AND m.state = 'active'
        """)

        self.stamp_record = text("""
            UPDATE package
            SET last_publish_check = :timestamp
            WHERE id = :record_id
        """)

    def getrecords(self) -> Iterator[CatalogueRecord]:
        conn = self.engine.connect()
        records = conn.execute(self.select_records)
        for record in records:
            projects = conn.execute(self.select_projects, collection_id=record['collection_id'])
            yield CatalogueRecord(
                id=record['id'],
                doi=record['doi'] or None,
                sid=record['sid'] or None,
                institution_key=record['institution_key'],
                collection_key=record['collection_key'],
                project_keys=[project['project_key'] for project in projects],
                schema_key=record['schema_key'],
                metadata=json.loads(record['metadata']),
                published=not record['private'] and record['state'] == 'active',
            )

    def setchecked(self, record_id: str) -> None:
        conn = self.engine.connect()
        conn.execute(self.stamp_record, record_id=record_id, timestamp=datetime.now(timezone.utc))
