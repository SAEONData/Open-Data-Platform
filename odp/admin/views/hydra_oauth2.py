from odp.config import config
from odp.lib.hydra_oauth2 import HydraOAuth2Blueprint

bp = HydraOAuth2Blueprint(
    'hydra', __name__,
    server_url=config.HYDRA.PUBLIC.URL,
    client_id=config.ODP.ADMIN.UI.CLIENT_ID,
    client_secret=config.ODP.ADMIN.UI.CLIENT_SECRET,
    scope=config.ODP.ADMIN.UI.SCOPE,
    verify_tls=config.ODP.ENV != 'development',
    redirect_to='admin.index',
    redis_host=config.REDIS.HOST,
    redis_port=config.REDIS.PORT,
    redis_db=config.REDIS.DB,
)
