import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from odp.api.public import config, load_adapters, load_configs, set_adapter, set_config
from odp.api.routers import metadata, search, project, collection

load_dotenv()

app_config = config.PublicAPIConfig()
app = FastAPI(
    title="ODP API",
    description="The SAEON Open Data Platform API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    root_path=app_config.PATH_PREFIX,
    config=app_config,
)

load_adapters(app)
load_configs(
    app,
    metadata.__name__,
    collection.__name__,
    project.__name__,
    search.__name__,
)

app.include_router(
    metadata.router,
    prefix='/{institution_key}/metadata',
    tags=['Metadata Records'],
    dependencies=[Depends(set_config), Depends(set_adapter)],
)

app.include_router(
    collection.router,
    prefix='/{institution_key}/collection',
    tags=['Metadata Collections'],
    dependencies=[Depends(set_config), Depends(set_adapter)],
)

app.include_router(
    project.router,
    prefix='/project',
    tags=['Projects'],
    dependencies=[Depends(set_config), Depends(set_adapter)]
)

app.include_router(
    search.router,
    prefix='/search',
    tags=['Search'],
    dependencies=[Depends(set_config), Depends(set_adapter)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
