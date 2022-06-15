#!/usr/bin/env python

import logging

from sqlalchemy import select

from odp import ODPCatalog
from odp.db import Session
from odp.db.models import Catalog
from odp.job.publish.saeon import SAEONPublisher
from odp.lib.logging import init_logging

init_logging()

logger = logging.getLogger(__name__)

publishers = {
    ODPCatalog.SAEON: SAEONPublisher,
}


def main():
    logger.info('PUBLISHING STARTED')
    try:
        for catalog_id in Session.execute(select(Catalog.id)).scalars():
            publisher = publishers[catalog_id]
            publisher(catalog_id).run()

        logger.info('PUBLISHING FINISHED')

    except Exception as e:
        logger.critical(f'PUBLISHING ABORTED: {str(e)}')


if __name__ == '__main__':
    main()
