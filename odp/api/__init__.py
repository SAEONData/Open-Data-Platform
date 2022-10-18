from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import odplib
from odp.api.routers import catalog, client, collection, provider, record, role, schema, scope, status, tag, token, user, vocabulary
from odp.db import Session
from odplib.config import config

app = FastAPI(
    title="ODP API",
    description="SAEON | Open Data Platform API",
    version=odplib.__version__,
    root_path=config.ODP.API.PATH_PREFIX,
    docs_url='/interactive',
    redoc_url='/docs',
)

app.include_router(catalog.router, prefix='/catalog', tags=['Catalog'])
app.include_router(client.router, prefix='/client', tags=['Client'])
app.include_router(collection.router, prefix='/collection', tags=['Collection'])
app.include_router(provider.router, prefix='/provider', tags=['Provider'])
app.include_router(record.router, prefix='/record', tags=['Record'])
app.include_router(role.router, prefix='/role', tags=['Role'])
app.include_router(schema.router, prefix='/schema', tags=['Schema'])
app.include_router(scope.router, prefix='/scope', tags=['Scope'])
app.include_router(status.router, prefix='/status', tags=['Status'])
app.include_router(tag.router, prefix='/tag', tags=['Tag'])
app.include_router(token.router, prefix='/token', tags=['Token'])
app.include_router(user.router, prefix='/user', tags=['User'])
app.include_router(vocabulary.router, prefix='/vocabulary', tags=['Vocabulary'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ODP.API.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def db_middleware(request: Request, call_next):
    try:
        response: Response = await call_next(request)
        if 200 <= response.status_code < 400:
            Session.commit()
        else:
            Session.rollback()
    finally:
        Session.remove()

    return response
