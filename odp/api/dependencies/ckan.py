from fastapi import Request

from odp.lib.ckan import CKANClient


def get_ckan_client(request: Request) -> CKANClient:
    """
    CKAN dependency.
    """
    config = request.app.extra['config']
    return CKANClient(
        server_url=config.CKAN_URL,
        verify_tls=config.SERVER_ENV != 'development',
    )
