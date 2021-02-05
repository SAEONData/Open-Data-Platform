import redis
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail

from odp.config import config
from odp.lib.hydra_admin import HydraAdminClient

mail = Mail()

hydra_admin = HydraAdminClient(
    server_url=config.HYDRA.ADMIN.URL,
    verify_tls=config.ODP.ENV != 'development',
    remember_login_for=config.ODP.IDENTITY.LOGIN_EXPIRY,
)

redis_cache = redis.Redis(
    host=config.REDIS.HOST,
    port=config.REDIS.PORT,
    db=config.REDIS.DB,
    decode_responses=True,
)

google_oauth2 = OAuth(cache=redis_cache)
google_oauth2.register(
    name='google',
    authorize_url=config.GOOGLE.AUTH_URI,
    access_token_url=config.GOOGLE.TOKEN_URI,
    server_metadata_url=config.GOOGLE.OPENID_URI,
    client_id=config.GOOGLE.CLIENT_ID,
    client_secret=config.GOOGLE.CLIENT_SECRET,
    client_kwargs={'scope': ' '.join(config.GOOGLE.SCOPE)},
)
