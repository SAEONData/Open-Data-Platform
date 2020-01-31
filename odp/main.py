import pkg_resources

from fastapi import FastAPI, Depends
import uvicorn
from dotenv import load_dotenv

from odp.routers import load_configs, set_config, set_adapter, authorize, metadata
from odp.config import AppConfig
from odp.lib import adapters

load_dotenv()

app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    config=AppConfig(),
)

adapters.load_adapters(app)
load_configs(app, metadata.__name__)

app.include_router(
    metadata.router,
    prefix='/metadata',
    tags=['Metadata'],
    dependencies=[Depends(set_config), Depends(set_adapter), Depends(authorize)],
)


if __name__ == '__main__':
    uvicorn.run(app, host=app.extra['config'].SERVER_HOST, port=app.extra['config'].SERVER_PORT)
