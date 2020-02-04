import pkg_resources

from fastapi import FastAPI, Depends
import uvicorn
from dotenv import load_dotenv

from odpapi import config, routers, adapters
from odpapi.routers import metadata

load_dotenv()

app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    config=config.AppConfig(),
)

adapters.load_adapters(app)
routers.load_configs(app, metadata.__name__)

app.include_router(
    metadata.router,
    prefix='/{institution_key}/metadata',
    tags=['Metadata'],
    dependencies=[
        Depends(routers.set_config),
        Depends(routers.set_adapter),
    ],
)


if __name__ == '__main__':
    uvicorn.run(app, host=app.extra['config'].SERVER_HOST, port=app.extra['config'].SERVER_PORT)
