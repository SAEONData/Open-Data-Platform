import pkg_resources
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odp.api.routers import metadata, catalogue, collection
from odp.config import config

app = FastAPI(
    title="ODP API",
    description="The SAEON Open Data Platform API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    root_path=config.ODP.API.PATH_PREFIX,
)

app.include_router(
    catalogue.router,
    prefix='/catalogue',
    tags=['Catalogue'],
)

app.include_router(
    collection.router,
    prefix='/{institution_key}/collection',
    tags=['Collections'],
)

app.include_router(
    metadata.router,
    prefix='/{institution_key}/metadata',
    tags=['Metadata'],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ODP.API.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
