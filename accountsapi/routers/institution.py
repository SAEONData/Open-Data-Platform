from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from odpaccounts.models.institution import Institution as InstitutionORM

from ..db import db_session
from ..models.institution import Institution

router = APIRouter()


@router.post('/', response_model=Institution)
async def create_institution(
        institution: Institution,
        session: Session = Depends(db_session),
):
    institution_orm = InstitutionORM(
        key=institution.key,
        name=institution.name,
    )
    try:
        institution_orm.parent = session.query(InstitutionORM).filter_by(key=institution.parent_key).one() if institution.parent_key else None
    except NoResultFound:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, "Parent institution not found.")

    session.add(institution_orm)
    try:
        session.commit()
    except IntegrityError as e:
        # catch unique key violations
        session.rollback()
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    return institution


@router.get('/', response_model=List[Institution])
async def list_institutions(
        session: Session = Depends(db_session),
):
    return [
        Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
        ) for institution_orm in session.query(InstitutionORM).all()
    ]
