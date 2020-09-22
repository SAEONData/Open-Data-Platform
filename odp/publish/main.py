#!/usr/bin/env python

import logging

from odp.publish import config
from odp.publish.catalogue.datacite import DataciteCatalogue
from odp.publish.catalogue.elasticsearch import ElasticsearchCatalogue
from odp.publish.harvester.ckan import CKANHarvester
from odp.publish.publisher import Publisher

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting publishing run")
    harvester = CKANHarvester(
        db_url=f'postgresql://ckan_default:{config.CKAN_DB_PASSWORD}@{config.CKAN_DB_HOST}/ckan_default',
        db_echo=config.DATABASE_ECHO,
    )
    elastic_cat = ElasticsearchCatalogue()  # stub for now
    datacite_cat = DataciteCatalogue(
        datacite_api_url=config.DATACITE_API_URL,
        datacite_username=config.DATACITE_USERNAME,
        datacite_password=config.DATACITE_PASSWORD,
        doi_prefix=config.DOI_PREFIX,
        doi_landing_base_url=config.DOI_LANDING_BASE_URL,
    )
    publisher = Publisher(harvester, elastic_cat, datacite_cat, max_retries=config.PUBLISH_MAX_RETIRES)
    publisher.run()
    logger.info("Finished publishing run")
