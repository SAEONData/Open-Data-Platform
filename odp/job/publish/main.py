#!/usr/bin/env python

import logging
import pathlib
import sys

from sqlalchemy import select

rootdir = pathlib.Path(__file__).parent.parent.parent.parent
sys.path.append(str(rootdir))

from odp.db import Session
from odp.db.models import Catalog
from odp.job.publish.datacite import DataCitePublisher
from odp.job.publish.saeon import SAEONPublisher
from odplib.const import ODPCatalog
from odplib.logging import init_logging

init_logging()

logger = logging.getLogger(__name__)

publishers = {
    ODPCatalog.SAEON: SAEONPublisher,
    ODPCatalog.DATACITE: DataCitePublisher,
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
