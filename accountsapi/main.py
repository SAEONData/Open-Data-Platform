import pkg_resources
import uvicorn
from accountsapi.routers import authorization, institution
from dotenv import load_dotenv
from fastapi import FastAPI

from accountsapi.config import Config

load_dotenv()

app = FastAPI(
    title="ODP Accounts API",
    description="The ODP Accounts API",
    version=pkg_resources.require('odp-accountsapi')[0].version,
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


if __name__ == '__main__':
    uvicorn.run(app, host=app.extra['config'].SERVER_HOST, port=app.extra['config'].SERVER_PORT)
