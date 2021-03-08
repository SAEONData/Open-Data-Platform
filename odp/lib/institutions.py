from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from odp.api.models.institution import Institution
from odp.db import transaction
from odp.db.models import Institution as InstitutionORM, Domain
from odp.lib import exceptions as x


def create_or_update_institution(institution: Institution) -> Institution:
    """ Create an institution record in the ODP database, or update an
    existing record if a matching key is found.

    :raise ODPParentInstitutionNotFound: if the given parent key does not exist
    :raise ODPInstitutionNameConflict: if the given name is already in use
    """
    with transaction():
        try:
            institution_orm = InstitutionORM.query.filter_by(key=institution.key).one()
            institution_orm.name = institution.name
        except NoResultFound:
            institution_orm = InstitutionORM(
                key=institution.key,
                name=institution.name,
            )

        try:
            institution_orm.parent = InstitutionORM.query.filter_by(
                key=institution.parent_key).one() if institution.parent_key else None
        except NoResultFound as e:
            raise x.ODPParentInstitutionNotFound from e

        # the domains to be linked with the institution
        ref_domain_names = institution.domain_names.copy()

        # delete no-longer-referenced domains
        for domain in Domain.query.filter_by(institution_id=institution_orm.id).all():
            if domain.name in ref_domain_names:
                ref_domain_names.remove(domain.name)  # no change
            else:
                institution_orm.domains.remove(domain)

        # create newly referenced domains
        try:
            for domain_name in ref_domain_names:
                domain = Domain(
                    name=domain_name,
                    institution=institution_orm,
                )
                domain.save()
        except IntegrityError as e:
            # domain name already taken
            raise x.ODPDomainNameConflict from e

        try:
            institution_orm.save()
        except IntegrityError as e:
            # unique key violation; must be on 'name', since we're handling 'key' with an update
            raise x.ODPInstitutionNameConflict from e

    return institution


def list_institutions() -> List[Institution]:
    """ Return a list of all institutions. """
    return [
        Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
            domain_names=[domain.name for domain in institution_orm.domains],
        ) for institution_orm in InstitutionORM.query.all()
    ]


def get_institution(institution_key: str) -> Institution:
    """ Return the institution matching the given key.

    :raise ODPInstitutionNotFound: if the given key does not exist
    """
    try:
        institution_orm = InstitutionORM.query.filter_by(key=institution_key).one()
        return Institution(
            key=institution_orm.key,
            name=institution_orm.name,
            parent_key=institution_orm.parent.key if institution_orm.parent else None,
            domain_names=[domain.name for domain in institution_orm.domains],
        )
    except NoResultFound as e:
        raise x.ODPInstitutionNotFound from e
