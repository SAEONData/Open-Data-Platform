from odp.config import config
from odp.lib.hydra import HydraAdminAPI

hydra_admin_api = HydraAdminAPI(config.HYDRA.ADMIN.URL)
hydra_public_url = config.HYDRA.PUBLIC.URL
