from pydantic import constr

from odplib.config import config
from odplib.formats import DOI_REGEX


async def get_catalog_ui_url(doi: constr(regex=DOI_REGEX)) -> str:
    return f'{config.ODP.API.CATALOG_UI_URL}/{doi}'
