from typing import Union

from pydantic import UUID4, constr

from odp.api_old.models.metadata import DOI_REGEX
from odp.config import config


def get_metadata_landing_page_url(record_id_or_doi: Union[UUID4, constr(regex=DOI_REGEX)]) -> str:
    """
    Gets the redirect target for a metadata record in the catalogue.
    The record may be identified either by ID or by DOI.
    """
    return f'{config.CATALOGUE.METADATA_LANDING_PAGE_BASE_URL}/{record_id_or_doi}'
