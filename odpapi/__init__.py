import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from odpapi import config, routers, adapters
from odpapi.routers import metadata, search

load_dotenv()

app_config = config.AppConfig()
app = FastAPI(
    title="ODP API",
    description="The Open Data Platform API",
    version=pkg_resources.require('odp-api')[0].version,
    openapi_prefix=app_config.PATH_PREFIX,
    config=app_config,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
