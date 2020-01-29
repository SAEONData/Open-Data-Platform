from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odpaccounts.models.institution import Institution as InstitutionORM
from odpaccounts.models.institution_registry import InstitutionRegistry as RegistryORM

from .. import db_session
from ..models.institution import Institution

router = APIRouter()


@router.post('/', response_model=Institution)
async def create_or_update_institution(
        institution: Institution,
        session: Session = Depends(db_session),
):
    institution_orm = session.query(InstitutionORM).filter_by(key=institution.key).one_or_none()
    if not institution_orm:
        institution_orm = InstitutionORM(key=institution.key)

    institution_orm.name = institution.name
    try:
        institution_orm.parent = session.query(InstitutionORM).filter_by(key=institution.parent_key).one() if institution.parent_key else None
        institution_orm.registry = session.query(RegistryORM).filter_by(key=institution.registry_key).one()
    except NoResultFound:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Referenced entity not found.")

    session.add(institution_orm)
    session.commit()

    return institution
