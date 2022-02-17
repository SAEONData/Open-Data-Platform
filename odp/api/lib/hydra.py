from odp.config import config
from odp.lib.hydra import HydraAdminAPI

admin_api = HydraAdminAPI(config.HYDRA.ADMIN.URL)
public_url = config.HYDRA.PUBLIC.URL
