from fastapi import Request

from odp.lib.elastic import ElasticClient


def get_elastic_client(request: Request) -> ElasticClient:
    """
    Elasticsearch dependency.
    """
    config = request.app.extra['config']
    return ElasticClient(
        server_url=config.ES_URL,
        indices=config.ES_INDICES,
    )
