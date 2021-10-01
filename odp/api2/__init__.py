from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import odp
from odp.api2.routers import project, collection, status
from odp.config import config
from odp.db import Session

app = FastAPI(
    title="ODP API",
    description="SAEON | Open Data Platform API",
    version=odp.__version__,
    root_path=config.ODP.API.PATH_PREFIX,
    docs_url='/interactive',
    redoc_url='/docs',
)

app.include_router(project.router, prefix='/project', tags=['Project'])
app.include_router(collection.router, prefix='/collection', tags=['Collection'])
app.include_router(status.router, prefix='/status', tags=['Status'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ODP.API.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def release_db_resources(request, call_next):
    """Release DB transaction/connection resources at the end of a request."""
    response = await call_next(request)
    Session.remove()
    return response
