import logging
from datetime import datetime, timezone
from typing import Type, List

from odp.db import transactional_session
from odp.db.models import ElasticsearchStatus, MetadataStatus
from odp.db.models.metadata_status import CatalogueStatusMixin
from odp.lib.exceptions import ElasticsearchError
from odp.publish.catalogue import Catalogue
from odp.lib.elastic import ElasticClient

logger = logging.getLogger(__name__)


class ElasticsearchCatalogue(Catalogue):
    def __init__(
            self,
            es_url: str,
            es_indices: List[str],
    ):
        self.elasticsearch = ElasticClient(
            server_url=es_url,
            indices=es_indices,
        )

    @property
    def model(self) -> Type[CatalogueStatusMixin]:
        return ElasticsearchStatus

    def syncrecord(self, record_id: str) -> bool:
        logger.debug(f"Syncing record {record_id}")

        updated = False
        with transactional_session() as session:
            mdstatus, esstatus = session.query(MetadataStatus, ElasticsearchStatus).outerjoin(ElasticsearchStatus). \
                filter(MetadataStatus.metadata_id == record_id). \
                one()

            if esstatus is None:
                esstatus = ElasticsearchStatus(metadata_id=record_id, published=False)

            try:
                if esstatus.published and not mdstatus.published:
                    # the record is currently published and should be unpublished
                    logger.info(f"Unpublishing record {record_id}")
                    self.elasticsearch.unpublish(
                        esstatus.metadata_id,
                    )
                    esstatus.published = False
                    esstatus.updated = datetime.now(timezone.utc)
                    updated = True

                elif not esstatus.published and mdstatus.published:
                    # the record is not currently published and should be published
                    logger.info(f"Publishing record {record_id}")
                    esstatus.index = self.elasticsearch.publish(
                        mdstatus.catalogue_record,
                    )
                    esstatus.published = True
                    esstatus.updated = datetime.now(timezone.utc)
                    updated = True

                else:
                    logger.debug(f"No change for record {record_id}")

                esstatus.error = None
                esstatus.retries = None

            except ElasticsearchError as e:
                esstatus.error = f'{e.status_code}: {e.error_detail}'
                esstatus.retries = esstatus.retries + 1 if esstatus.retries is not None else 0
                logger.error(f"Error syncing record {record_id} with Elasticsearch: {esstatus.error}")

            esstatus.checked = datetime.now(timezone.utc)
            session.add(esstatus)

        return updated
