import os
import pkg_resources
from dotenv import load_dotenv
from fastapi import FastAPI

from accountsapi.config import Config
from accountsapi.routers import authorization, institution

load_dotenv()

app = FastAPI(
    title="ODP Accounts API",
    description="The ODP Accounts API",
    version=pkg_resources.require('odp-accountsapi')[0].version,
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
