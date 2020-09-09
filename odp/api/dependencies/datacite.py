from fastapi import Request

from odp.lib.datacite import DataCiteClient


def get_datacite_client(request: Request) -> DataCiteClient:
    """
    DataCite API dependency.
    """
    config = request.app.extra['config']
    api_url = config.DATACITE.API_URL \
        if config.SERVER_ENV in ('production', 'staging') \
        else config.DATACITE.API_TEST_URL

    return DataCiteClient(
        api_url=api_url,
        doi_prefix=config.DATACITE.DOI_PREFIX,
        username=config.DATACITE.USERNAME,
        password=config.DATACITE.PASSWORD,
    )
