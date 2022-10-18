from odp.lib.datacite import DataciteClient
from odplib.config import config
from odplib.const import DOI_PREFIX


async def get_datacite_client() -> DataciteClient:
    return DataciteClient(
        api_url=config.DATACITE.API_URL,
        username=config.DATACITE.USERNAME,
        password=config.DATACITE.PASSWORD,
        doi_prefix=DOI_PREFIX,
    )
