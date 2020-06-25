import os
import pkg_resources

from fastapi import FastAPI

from odp.api.routers import authorization, institution
from .config import Config

app = FastAPI(
    title="ODP Admin API",
    description="The SAEON Open Data Platform Administrative API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    openapi_prefix=os.getenv('PATH_PREFIX'),
    config=Config(),
)

app.include_router(
    authorization.router,
    prefix='/authorization',
    tags=['Authorization'],
)

app.include_router(
    institution.router,
    prefix='/institution',
    tags=['Institution'],
)
