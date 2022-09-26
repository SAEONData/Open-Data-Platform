from odplib.config.base import BaseConfig
from odplib.config.datacite import DataciteConfig
from odplib.config.google import GoogleConfig
from odplib.config.hydra import HydraConfig
from odplib.config.odp import ODPConfig
from odplib.config.redis import RedisConfig


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
