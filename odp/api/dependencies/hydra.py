from odp.config import config
from odp.lib.hydra import HydraAdminClient


def get_hydra_admin() -> HydraAdminClient:
    """
    Hydra Admin dependency.
    """
    return HydraAdminClient(
        server_url=config.HYDRA.ADMIN.URL,
        verify_tls=config.ODP.ENV != 'development',
    )
