from flask_mail import Mail

from odp.lib.hydra import HydraAdminClient

mail = Mail()

hydra_admin = HydraAdminClient('')
