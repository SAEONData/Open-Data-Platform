import os
from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odp.api.dependencies.auth import Authorizer, AuthData
from odp.api.dependencies.ckan import get_ckan_client
from odp.api.dependencies.db import get_db_session
from odp.api.models.auth import Role, Scope
from odp.api.models.institution import Institution
from odp.db.models.institution import Institution as InstitutionORM
from odp.lib.ckan import CKANClient

router = APIRouter()


@router.post('/', response_model=Institution)
async def create_or_update_institution(
        institution: Institution,
        session: Session = Depends(get_db_session),
        ckan: CKANClient = Depends(get_ckan_client),
        auth_data: AuthData = Depends(Authorizer(
            Scope.ADMIN,
            Role.ADMIN,
            institution_key=os.environ['ADMIN_INSTITUTION'])),
):
    try:
        institution_orm = session.query(InstitutionORM).filter_by(key=institution.key).one()
        institution_orm.name = institution.name
    except NoResultFound:
        institution_orm = InstitutionORM(
            key=institution.key,
            name=institution.name,
        )

    try:
        institution_orm.parent = session.query(InstitutionORM).filter_by(
            key=institution.parent_key).one() if institution.parent_key else None
    except NoResultFound:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Parent institution not found.")

    session.add(institution_orm)
    try:
        session.commit()
    except IntegrityError as e:
        # catch unique key violations
        session.rollback()
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    # If the CKAN operation fails, we bail out; we need to inform the caller
    # so that action wrt CKAN can be taken. There's no harm in re-running the
    # ODP operation as it's idempotent.
    # N.B. do not use the return value from CKAN
    ckan.create_or_update_institution(institution, auth_data.access_token)

    return institution


@router.get(
    '/',
    response_model=List[Institution],
    dependencies=[Depends(Authorizer(
        Scope.ADMIN,
        *Role.all(),
        institution_key=os.environ['ADMIN_INSTITUTION']))],
)
async def list_institutions(
        session: Session = Depends(get_db_session),
):
    return [
        Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
        ) for institution_orm in session.query(InstitutionORM).all()
    ]
