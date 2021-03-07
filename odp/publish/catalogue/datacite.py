import logging
from datetime import datetime, timezone
from typing import Tuple

import pydantic
from sqlalchemy import or_, and_, not_

from odp.api.models.datacite import DataciteRecordIn
from odp.db import session, transaction
from odp.db.models import CatalogueRecord, DataciteRecord
from odp.lib.datacite import DataciteClient
from odp.lib.exceptions import DataciteError
from odp.publish.catalogue import Catalogue

logger = logging.getLogger(__name__)


class DataciteCatalogue(Catalogue):
    def __init__(
            self,
            datacite_api_url: str,
            datacite_username: str,
            datacite_password: str,
            doi_prefix: str,
            doi_landing_page_base_url: str,
            batch_size: int,
            max_retries: int,
    ):
        self.datacite = DataciteClient(
            api_url=datacite_api_url,
            username=datacite_username,
            password=datacite_password,
            doi_prefix=doi_prefix,
        )
        self.doi_landing_page_base_url = doi_landing_page_base_url
        self.batch_size = batch_size
        self.max_retries = max_retries

    def synchronize(self) -> None:
        published = 0
        unpublished = 0
        unchanged = 0
        errors = 0
        try:
            check_records = session.query(CatalogueRecord, DataciteRecord). \
                outerjoin(DataciteRecord). \
                filter(not_(  # exclude records without DOIs
                    CatalogueRecord.catalogue_record.comparator.contains({'doi': None})
                )). \
                filter(or_(
                    DataciteRecord.metadata_id == None,
                    DataciteRecord.checked < CatalogueRecord.updated,
                    # check if the DOI resolution URL that we publish to DataCite must
                    # be updated; unlike a change in metadata, this might result from
                    # a config (or code) change, but not from a catalogue record update
                    DataciteRecord.url != self.doi_landing_page_base_url + '/' + DataciteRecord.doi,
                )). \
                limit(self.batch_size).all()

            # clear errors and retries for records that we have selected to check
            for catrec, dcrec in check_records:
                if dcrec is not None and dcrec.error is not None:
                    dcrec.error = None
                    dcrec.retries = None
                    dcrec.save()

            failed_ids = session.query(CatalogueRecord.metadata_id).join(DataciteRecord).filter(
                and_(
                    DataciteRecord.error != None,
                    DataciteRecord.retries < self.max_retries,
                ),
            ).limit(self.batch_size).all()

            syncable_ids = [catrec.metadata_id for catrec, dcrec in check_records] + \
                           [record_id for record_id, in failed_ids]
            logger.info(f"Selected {len(syncable_ids)} records to synchronize with DataCite")
            for record_id in syncable_ids:
                pub, unpub, unchg, err = self._syncrecord(record_id)
                published += pub
                unpublished += unpub
                unchanged += unchg
                errors += err

        except Exception as e:
            logger.critical(str(e))
        finally:
            session.remove()
            logger.info(f"{published} published; "
                        f"{unpublished} un-published; "
                        f"{unchanged} unchanged; "
                        f"{errors} errors")

    def _syncrecord(self, record_id: str) -> Tuple[bool, bool, bool, bool]:
        logger.debug(f"Syncing record {record_id}")
        published = False
        unpublished = False
        unchanged = False
        error = False

        with transaction():
            catrec, dcrec = session.query(CatalogueRecord, DataciteRecord).outerjoin(DataciteRecord). \
                filter(CatalogueRecord.metadata_id == record_id). \
                one()

            doi = catrec.catalogue_record['doi']
            if dcrec is None:
                dcrec = DataciteRecord(metadata_id=record_id, doi=doi, published=False)

            try:
                datacite_record = DataciteRecordIn(
                    doi=doi,
                    url=f'{self.doi_landing_page_base_url}/{doi}',
                    metadata=catrec.catalogue_record['metadata'],
                )
                datacite_record_dict = datacite_record.dict()
            except pydantic.ValidationError:
                datacite_record = None
                datacite_record_dict = None

            publish = catrec.published and doi is not None and datacite_record is not None
            try:
                if dcrec.published and (not publish or dcrec.doi.lower() != doi.lower()):
                    # the record is currently published and should be unpublished;
                    # if the DOI has changed, we must also first unpublish the record
                    logger.info(f"Unpublishing record {record_id} with DOI {dcrec.doi}")
                    self.datacite.unpublish_doi(
                        dcrec.doi,
                    )
                    dcrec.published = False
                    dcrec.updated = datetime.now(timezone.utc)
                    unpublished = True

                if publish and (not dcrec.published or datacite_record_dict != {
                    'doi': dcrec.doi,
                    'url': dcrec.url,
                    'metadata': dcrec.metadata_,
                }):
                    # the record should be published; it is either not currently published,
                    # or it is published but one or more properties has changed
                    logger.info(f"Publishing record {record_id} with DOI {doi}")
                    self.datacite.publish_doi(
                        datacite_record,
                    )
                    dcrec.doi = doi
                    dcrec.url = datacite_record.url
                    dcrec.metadata_ = datacite_record.metadata
                    dcrec.published = True
                    dcrec.updated = datetime.now(timezone.utc)
                    published = True

                if not (published or unpublished):
                    logger.debug(f"No change for record {record_id}")
                    unchanged = True

                dcrec.error = None
                dcrec.retries = None

            except DataciteError as e:
                dcrec.error = f'{e.status_code}: {e.error_detail}'
                dcrec.retries = dcrec.retries + 1 if dcrec.retries is not None else 0
                logger.error(f"Error syncing record {record_id} with DataCite: {dcrec.error}")
                error = True

            dcrec.checked = datetime.now(timezone.utc)
            dcrec.save()

        return published, unpublished, unchanged, error
