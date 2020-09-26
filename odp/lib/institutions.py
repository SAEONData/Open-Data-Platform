from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from odp.api.models.institution import Institution
from odp.db import session as db_session
from odp.db.models.institution import Institution as InstitutionORM
from odp.lib import exceptions as x


def create_or_update_institution(institution: Institution) -> Institution:
    """ Create an institution record in the ODP database, or update an
    existing record if a matching key is found.

    :raise ODPParentInstitutionNotFound: if the given parent key does not exist
    :raise ODPInstitutionNameConflict: if the given name is already in use
    """
    try:
        institution_orm = db_session.query(InstitutionORM).filter_by(key=institution.key).one()
        institution_orm.name = institution.name
    except NoResultFound:
        institution_orm = InstitutionORM(
            key=institution.key,
            name=institution.name,
        )

    try:
        institution_orm.parent = db_session.query(InstitutionORM).filter_by(
            key=institution.parent_key).one() if institution.parent_key else None
    except NoResultFound as e:
        raise x.ODPParentInstitutionNotFound from e

    db_session.add(institution_orm)
    try:
        db_session.commit()
    except IntegrityError as e:
        # unique key violation; must be on 'name', since we're handling 'key' with an update
        db_session.rollback()
        raise x.ODPInstitutionNameConflict from e

    return institution


def list_institutions() -> List[Institution]:
    """ Return a list of all institutions. """
    return [
        Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
        ) for institution_orm in db_session.query(InstitutionORM).all()
    ]


def get_institution(institution_key: str) -> Institution:
    """ Return the institution matching the given key.

    :raise ODPInstitutionNotFound: if the given key does not exist
    """
    try:
        institution_orm = db_session.query(InstitutionORM).filter_by(key=institution_key).one()
        return Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
        )
    except NoResultFound as e:
        raise x.ODPInstitutionNotFound from e
