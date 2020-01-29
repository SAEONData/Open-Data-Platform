from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odpaccounts.models.institution import Institution as SQLInstitution
from odpaccounts.models.institution_registry import InstitutionRegistry as SQLRegistry

from .. import db_session
from ..models.institution import Institution

router = APIRouter()


@router.post('/', response_model=Institution)
async def create_or_update_institution(
        institution: Institution,
        session: Session = Depends(db_session),
):
    sqlinstitution = session.query(SQLInstitution).filter_by(key=institution.key).one_or_none()
    if not sqlinstitution:
        sqlinstitution = SQLInstitution(key=institution.key)

    sqlinstitution.name = institution.name
    try:
        sqlinstitution.parent = session.query(SQLInstitution).filter_by(key=institution.parent_key).one() if institution.parent_key else None
        sqlinstitution.registry = session.query(SQLRegistry).filter_by(key=institution.registry_key).one()
    except NoResultFound:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Referenced entity not found.")

    session.add(sqlinstitution)
    session.commit()

    return institution
