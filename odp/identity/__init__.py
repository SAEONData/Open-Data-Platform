from flask_mail import Mail

from odp.config import config
from odp.lib.hydra import HydraAdminClient

mail = Mail()

hydra_admin = HydraAdminClient(
    server_url=config.HYDRA.ADMIN.URL,
    verify_tls=config.ODP.ENV != 'development',
    remember_login_for=config.ODP.IDENTITY.LOGIN_EXPIRY,
)
