from urllib.parse import urljoin

from fastapi import Request

from odp.lib.elastic import ElasticClient


def get_elastic_client(request: Request) -> ElasticClient:
    """
    Elasticsearch dependency.
    """
    config = request.app.extra['config']
    return ElasticClient(
        server_url=config.CATALOGUE.ES_URL,
        indices=config.CATALOGUE.ES_INDICES,
    )


def get_metadata_landing_page_url(record_id: str, request: Request) -> str:
    """
    Gets the redirect target for a metadata record in the catalogue.
    """
    config = request.app.extra['config']
    return urljoin(config.CATALOGUE.METADATA_LANDING_PAGE_BASE_URL, record_id)
