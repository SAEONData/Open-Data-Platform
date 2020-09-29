import json
import logging
from datetime import datetime
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.sql import text

from odp.api.models.catalogue import CatalogueRecord
from odp.publish.harvester import Harvester

logger = logging.getLogger(__name__)


class CKANHarvester(Harvester):
    def __init__(
            self,
            db_url: str,
            db_echo: bool,
            harvest_check_interval_hrs: int,
    ):
        self.engine = create_engine(db_url, echo=db_echo)

        # runtime typecheck as a safeguard against SQL injection
        if not isinstance(harvest_check_interval_hrs, int):
            raise TypeError

        self.select_records = text(f"""
            SELECT p.id, p.private, p.state, p_doi.value doi, p_json.value metadata,
                   g_inst.title institution, g_coll.title collection, g_coll.id collection_id
            FROM package p JOIN package_extra p_doi ON p.id = p_doi.package_id AND p_doi.key = 'doi'
                           JOIN package_extra p_json ON p.id = p_json.package_id AND p_json.key = 'metadata_json'
                           JOIN package_extra p_coll ON p.id = p_coll.package_id AND p_coll.key = 'metadata_collection_id'
                           JOIN "group" g_inst ON p.owner_org = g_inst.id
                           JOIN "group" g_coll ON p_coll.value = g_coll.id
            WHERE p.last_publish_check IS NULL
               OR localtimestamp - p.last_publish_check > interval '{harvest_check_interval_hrs} hours'
            LIMIT 1000
        """)

        self.select_projects = text("""
            SELECT g.title project
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
        logger.info(f"Harvested {records.rowcount} records from CKAN")
        for record in records:
            projects = conn.execute(self.select_projects, collection_id=record['collection_id'])
            yield CatalogueRecord(
                id=record['id'],
                doi=record['doi'] or None,
                institution=record['institution'],
                collection=record['collection'],
                projects=[project['project'] for project in projects],
                published=not record['private'] and record['state'] == 'active',
                metadata=json.loads(record['metadata']),
            )

    def setchecked(self, record_id: str, timestamp: datetime) -> None:
        conn = self.engine.connect()
        conn.execute(self.stamp_record, record_id=record_id, timestamp=timestamp)
