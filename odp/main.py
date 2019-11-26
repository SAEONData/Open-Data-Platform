import pkg_resources

from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

from odp.routers import metadata, institution
from odp.config import Config
from odp.lib import adapters

load_dotenv()

app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    config=Config(),
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
    uvicorn.run(app, host=app.extra['config'].SERVER_HOST, port=app.extra['config'].SERVER_PORT)
