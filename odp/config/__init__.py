from odp.config.base import BaseConfig
from odp.config.catalogue import CatalogueConfig
from odp.config.ckan import CKANConfig
from odp.config.datacite import DataciteConfig
from odp.config.hydra import HydraConfig
from odp.config.odp import ODPConfig
from odp.config.redis import RedisConfig
from odp.config.media import MediaConfig


class Config(BaseConfig):
    """ root configuration """

    _subconfig = {
        'ODP': ODPConfig,
        'HYDRA': HydraConfig,
        'CKAN': CKANConfig,
        'CATALOGUE': CatalogueConfig,
        'DATACITE': DataciteConfig,
        'REDIS': RedisConfig,
        'MEDIA':MediaConfig,
    }


config: Config = Config()
