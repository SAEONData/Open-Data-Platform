from odp.config import config
from odp.lib.datacite import DataciteClient


def get_datacite_client() -> DataciteClient:
    """
    DataCite API dependency.
    """
    return DataciteClient(
        api_url=config.DATACITE.API_URL,
        doi_prefix=config.DATACITE.DOI_PREFIX,
        username=config.DATACITE.USERNAME,
        password=config.DATACITE.PASSWORD,
    )
