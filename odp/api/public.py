import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odp.api.config import Config
from odp.api.routers import metadata, catalogue, project, collection

load_dotenv()
config = Config()

app = FastAPI(
    title="ODP API",
    description="The SAEON Open Data Platform API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    root_path=config.PATH_PREFIX,
    config=config,
)

app.include_router(
    metadata.router,
    prefix='/{institution_key}/metadata',
    tags=['Metadata Records'],
)

app.include_router(
    collection.router,
    prefix='/{institution_key}/collection',
    tags=['Metadata Collections'],
)

app.include_router(
    project.router,
    prefix='/project',
    tags=['Projects'],
)

app.include_router(
    catalogue.router,
    prefix='/catalogue',
    tags=['Catalogue'],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
