#!/usr/bin/env python

import logging

from odp.config import config
from odp.publish.catalogue.datacite import DataciteCatalogue

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting DataCite publishing run")
    catalogue = DataciteCatalogue(
        datacite_api_url=config.DATACITE.API_URL,
        datacite_username=config.DATACITE.USERNAME,
        datacite_password=config.DATACITE.PASSWORD,
        doi_prefix=config.DATACITE.DOI_PREFIX,
        doi_landing_page_base_url=config.DATACITE.DOI_LANDING_PAGE_BASE_URL,
        batch_size=config.ODP.PUBLISH.BATCH_SIZE,
        max_retries=config.ODP.PUBLISH.MAX_RETRIES,
    )
    catalogue.synchronize()
    logger.info("Finished DataCite publishing run")
