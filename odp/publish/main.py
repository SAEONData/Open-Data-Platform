#!/usr/bin/env python

import logging

from odp.config import config
from odp.publish.catalogue.odp import ODPCatalogue
from odp.publish.harvester.ckan import CKANHarvester

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting ODP publishing run")
    catalogue = ODPCatalogue(
        harvester=CKANHarvester(
            db_url=config.CKAN.DB.URL,
            db_echo=config.CKAN.DB.ECHO,
            batch_size=config.ODP.PUBLISH.BATCH_SIZE,
            harvest_check_interval_minutes=config.ODP.PUBLISH.HARVEST_CHECK_INTERVAL,
        )
    )
    catalogue.synchronize()
    logger.info("Finished ODP publishing run")
