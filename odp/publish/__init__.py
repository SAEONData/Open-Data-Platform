import logging
import os

from dotenv import load_dotenv
from pydantic import BaseSettings, AnyHttpUrl


class Config(BaseSettings):
    CKAN_DB_HOST: str
    CKAN_DB_PASSWORD: str
    DATABASE_ECHO: bool = False
    DATACITE_API_URL: AnyHttpUrl
    DATACITE_USERNAME: str
    DATACITE_PASSWORD: str
    DOI_PREFIX: str
    DOI_LANDING_BASE_URL: AnyHttpUrl
    LOG_LEVEL: str = 'INFO'
    PUBLISH_MAX_RETIRES: int = 3


load_dotenv(f'{os.getcwd()}/.env')
config = Config()

rootlogger = logging.getLogger()
rootlogger.setLevel(config.LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formatter)
rootlogger.addHandler(consolehandler)
