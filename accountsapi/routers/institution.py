from fastapi import APIRouter

from odpaccounts.db import session as db_session
from odpaccounts.models.institution import Institution as SQLInstitution
from odpaccounts.models.institution_registry import InstitutionRegistry as SQLRegistry

from ..models.institution import Institution

router = APIRouter()


@router.post('/', response_model=Institution)
async def create_or_update_institution(
        institution: Institution,
):
    sqlinstitution = db_session.query(SQLInstitution).filter_by(key=institution.key).one_or_none()
    if not sqlinstitution:
        sqlinstitution = SQLInstitution(key=institution.key)
    sqlinstitution.name = institution.name
    sqlinstitution.parent = db_session.query(SQLInstitution).filter_by(key=institution.parent_key).one() if institution.parent_key else None
    sqlinstitution.registry = db_session.query(SQLRegistry).filter_by(key=institution.registry_key).one()
    db_session.add(sqlinstitution)
    db_session.commit()
    return institution
