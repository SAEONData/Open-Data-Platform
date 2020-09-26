import logging

from odp.config import config

rootlogger = logging.getLogger()
rootlogger.setLevel(config.ODP.LOG_LEVEL.name)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)
rootlogger.addHandler(consolehandler)
