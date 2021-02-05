from odp.config.base import BaseConfig
from odp.config.catalogue import CatalogueConfig
from odp.config.ckan import CKANConfig
from odp.config.datacite import DataciteConfig
from odp.config.google import GoogleConfig
from odp.config.hydra import HydraConfig
from odp.config.media import MediaConfig
from odp.config.odp import ODPConfig
from odp.config.redis import RedisConfig


class Config(BaseConfig):
    """ root configuration """

    _subconfig = {
        'ODP': ODPConfig,
        'HYDRA': HydraConfig,
        'CKAN': CKANConfig,
        'CATALOGUE': CatalogueConfig,
        'DATACITE': DataciteConfig,
        'REDIS': RedisConfig,
        'MEDIA': MediaConfig,
        'GOOGLE': GoogleConfig,
    }


config: Config = Config()
