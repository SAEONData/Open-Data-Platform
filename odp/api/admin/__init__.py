from fastapi import Request

from odp.lib.hydra import HydraAdminClient


def get_hydra_admin(request: Request) -> HydraAdminClient:
    """
    Hydra Admin dependency.
    """
    config = request.app.extra['config']
    return HydraAdminClient(
        server_url=config.HYDRA_ADMIN_URL,
        verify_tls=config.SERVER_ENV != 'development',
    )
