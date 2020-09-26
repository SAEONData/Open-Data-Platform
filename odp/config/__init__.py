from odp.config.base import BaseConfig
from odp.config.catalogue import CatalogueConfig
from odp.config.ckan import CKANConfig
from odp.config.datacite import DataciteConfig
from odp.config.elastic import ElasticConfig
from odp.config.hydra import HydraConfig
from odp.config.odp import ODPConfig


class Config(BaseConfig):
    """ root configuration """

    _subconfig = {
        'ODP': ODPConfig,
        'HYDRA': HydraConfig,
        'CKAN': CKANConfig,
        'CATALOGUE': CatalogueConfig,
        'ELASTIC': ElasticConfig,
        'DATACITE': DataciteConfig,
    }


config: Config = Config()
