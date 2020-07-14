import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI

from odp.api.admin import config
from odp.api.routers import authorization, institution

load_dotenv()

app_config = config.Config()
app = FastAPI(
    title="ODP Admin API",
    description="The SAEON Open Data Platform Administrative API",
    version=pkg_resources.require('Open-Data-Platform')[0].version,
    openapi_prefix=app_config.PATH_PREFIX,
    config=app_config,
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
