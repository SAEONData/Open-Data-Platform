from odp.config import config
from odp.lib.elastic import ElasticClient


def get_elastic_client() -> ElasticClient:
    """
    Elasticsearch dependency.
    """
    return ElasticClient(
        server_url=config.ELASTIC.URL,
        indices=config.ELASTIC.INDICES,
    )
