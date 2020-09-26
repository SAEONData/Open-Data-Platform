from urllib.parse import urljoin

from odp.config import config


def get_metadata_landing_page_url(record_id: str) -> str:
    """
    Gets the redirect target for a metadata record in the catalogue.
    """
    return urljoin(config.CATALOGUE.METADATA_LANDING_PAGE_BASE_URL, record_id)
