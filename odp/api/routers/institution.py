import os
from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND

from odp.api.dependencies.auth import Authorizer
from odp.api.models.auth import Role, Scope
from odp.api.models.institution import Institution
from odp.lib import exceptions as x
from odp.lib import institutions

router = APIRouter()


@router.post(
    '/',
    response_model=Institution,
    dependencies=[Depends(Authorizer(
        Scope.ADMIN,
        Role.ADMIN,
        institution_key=os.environ['ADMIN_INSTITUTION']))],
)
async def create_or_update_institution(institution: Institution):
    try:
        return institutions.create_or_update_institution(institution)
    except x.ODPParentInstitutionNotFound as e:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Parent institution not found.") from e
    except x.ODPInstitutionNameConflict as e:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "The institution name is already in use.") from e


@router.get(
    '/',
    response_model=List[Institution],
    dependencies=[Depends(Authorizer(
        Scope.ADMIN,
        *Role.all(),
        institution_key=os.environ['ADMIN_INSTITUTION']))],
)
async def list_institutions():
    return institutions.list_institutions()


@router.get(
    '/{institution_key}',
    response_model=Institution,
    dependencies=[Depends(Authorizer(
        Scope.ADMIN,
        *Role.all(),
        institution_key=os.environ['ADMIN_INSTITUTION']))],
)
async def get_institution(institution_key: str):
    try:
        return institutions.get_institution(institution_key)
    except x.ODPInstitutionNotFound as e:
        raise HTTPException(HTTP_404_NOT_FOUND) from e
