#!/usr/bin/env python

import logging

from odp.config import config
from odp.publish.catalogue.datacite import DataciteCatalogue
from odp.publish.catalogue.elasticsearch import ElasticsearchCatalogue
from odp.publish.harvester.ckan import CKANHarvester
from odp.publish.publisher import Publisher

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting publishing run")
    harvester = CKANHarvester(
        db_url=config.CKAN.DB.URL,
        db_echo=config.CKAN.DB.ECHO,
    )
    elastic_cat = ElasticsearchCatalogue(
        # stub for now
    )
    datacite_cat = DataciteCatalogue(
        datacite_api_url=config.DATACITE.API_URL,
        datacite_username=config.DATACITE.USERNAME,
        datacite_password=config.DATACITE.PASSWORD,
        doi_prefix=config.DATACITE.DOI_PREFIX,
        doi_landing_page_base_url=config.DATACITE.DOI_LANDING_PAGE_BASE_URL,
    )
    publisher = Publisher(
        harvester,
        elastic_cat,
        datacite_cat,
        max_retries=3,
    )
    publisher.run()
    logger.info("Finished publishing run")
