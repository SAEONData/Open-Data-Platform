import pkg_resources
from fastapi import FastAPI

from odp.api.routers import authorization, institution, datacite, project
from odp.config import config

app = FastAPI(
    title="ODP Admin API",
    description="The SAEON Open Data Platform Administrative API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    root_path=config.ODP.API.PATH_PREFIX,
)

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
    datacite.router,
    prefix='/datacite',
    tags=['DataCite'],
)
