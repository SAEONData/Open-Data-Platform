import pkg_resources

from fastapi import FastAPI
import uvicorn

from odp.routers import metadata, institution
from odp.config import read_config
from odp.lib import adapters


config = read_config()

app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    config=config,
)

adapters.load_adapters(app)

app.include_router(
    institution.router,
    prefix='/institutions',
    tags=['Institutions'],
)

app.include_router(
    metadata.router,
    prefix='/metadata',
    tags=['Metadata'],
)


if __name__ == '__main__':
    uvicorn.run(app, host=str(config.server.host), port=config.server.port)
