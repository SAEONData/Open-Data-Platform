import os
import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from odpapi import config, routers, adapters
from odpapi.routers import metadata, search

load_dotenv()

app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    openapi_prefix=os.getenv('PATH_PREFIX'),
    config=config.AppConfig(),
)

adapters.load_adapters(app)
routers.load_configs(app, metadata.__name__, search.__name__)

app.include_router(
    metadata.router,
    prefix='/{institution_key}/metadata',
    tags=['Manage Metadata'],
    dependencies=[
        Depends(routers.set_config),
        Depends(routers.set_adapter),
    ],
)

app.include_router(
    search.router,
    prefix='/metadata/search',
    tags=['Search Metadata'],
    dependencies=[
        Depends(routers.set_config),
        Depends(routers.set_adapter),
    ],
)
