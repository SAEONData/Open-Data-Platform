from pydantic import AnyHttpUrl

from odpapi.adapters import ODPAPIAdapter, ODPAPIAdapterConfig


class ElasticAdapterConfig(ODPAPIAdapterConfig):
    """
    Config for the Elastic adapter, populated from the environment.
    """
    ES_AGENT_URL: AnyHttpUrl

    class Config:
        env_prefix = 'ELASTIC_ADAPTER.'


class ElasticAdapter(ODPAPIAdapter):

    pass
