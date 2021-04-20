import pkg_resources
from fastapi import FastAPI

from odp.api import init_db_middleware
from odp.api.routers import (
    authorization,
    institution,
    datacite,
    project,
    schema,
    workflow,
    status,
)
from odp.config import config

app = FastAPI(
    title="ODP Admin API",
    description="The SAEON Open Data Platform Administrative API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    root_path=config.ODP.API.PATH_PREFIX,
    docs_url='/interactive',
    redoc_url='/docs',
)

init_db_middleware(app)

app.include_router(
    authorization.router,
    prefix='/auth',
    tags=['Authorization'],
)

app.include_router(
    institution.router,
    prefix='/institution',
    tags=['Institutions'],
)

app.include_router(
    project.router,
    prefix='/project',
    tags=['Projects'],
)

app.include_router(
    schema.router,
    prefix='/schema',
    tags=['Schemas'],
)

app.include_router(
    workflow.router,
    prefix='/workflow',
    tags=['Workflows'],
)

app.include_router(
    datacite.router,
    prefix='/datacite',
    tags=['DataCite'],
)

app.include_router(
    status.router,
    prefix='/status',
    tags=['Status'],
)
