from odp.config.base import BaseConfig
from odp.config.datacite import DataciteConfig
from odp.config.google import GoogleConfig
from odp.config.hydra import HydraConfig
from odp.config.odp import ODPConfig
from odp.config.redis import RedisConfig


class Config(BaseConfig):
    """ root configuration """

    _subconfig = {
        'ODP': ODPConfig,
        'HYDRA': HydraConfig,
        'DATACITE': DataciteConfig,
        'REDIS': RedisConfig,
        'GOOGLE': GoogleConfig,
    }


config: Config = Config()
