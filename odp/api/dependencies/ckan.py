from odp.config import config
from odp.lib.ckan import CKANClient


def get_ckan_client() -> CKANClient:
    """
    CKAN dependency.
    """
    return CKANClient(
        server_url=config.CKAN.URL,
        verify_tls=config.ODP.ENV != 'development',
    )
