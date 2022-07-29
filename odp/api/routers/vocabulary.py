from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from jschon import JSON, JSONSchema, URI
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY

from odp import ODPScope
from odp.api.lib.auth import Authorize, Authorized, VocabularyAuthorize
from odp.api.lib.paging import Page, Paginator
from odp.api.lib.schema import get_vocabulary_schema
from odp.api.models import VocabularyModel, VocabularyTermModel, VocabularyTermModelIn
from odp.db import Session
from odp.db.models import AuditCommand, Vocabulary, VocabularyTerm, VocabularyTermAudit
from odp.lib.schema import schema_catalog

router = APIRouter()


def output_vocabulary_model(vocabulary: Vocabulary) -> VocabularyModel:
    return VocabularyModel(
        id=vocabulary.id,
        scope_id=vocabulary.scope_id,
        schema_id=vocabulary.schema_id,
        schema_uri=vocabulary.schema.uri,
        schema_=schema_catalog.get_schema(URI(vocabulary.schema.uri)).value,
        terms=[VocabularyTermModel(
            id=term.term_id,
            data=term.data,
        ) for term in vocabulary.terms]
    )


@router.get(
    '/',
    response_model=Page[VocabularyModel],
    dependencies=[Depends(Authorize(ODPScope.VOCABULARY_READ))],
)
async def list_vocabularies(
        paginator: Paginator = Depends(),
):
    return paginator.paginate(
        select(Vocabulary),
        lambda row: output_vocabulary_model(row.Vocabulary),
    )


@router.get(
    '/{vocabulary_id}',
    response_model=VocabularyModel,
    dependencies=[Depends(Authorize(ODPScope.VOCABULARY_READ))],
)
async def get_vocabulary(
        vocabulary_id: str,
):
    if not (vocabulary := Session.get(Vocabulary, vocabulary_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return output_vocabulary_model(vocabulary)


@router.post(
    '/{vocabulary_id}/term',
)
async def create_term(
        vocabulary_id: str,
        term_in: VocabularyTermModelIn,
        term_schema: JSONSchema = Depends(get_vocabulary_schema),
        auth: Authorized = Depends(VocabularyAuthorize()),
):
    if Session.get(VocabularyTerm, (vocabulary_id, term_in.id)):
        raise HTTPException(HTTP_409_CONFLICT, 'Term already exists in vocabulary')

    # the id is validated by the term schema
    term_in.data['id'] = term_in.id

    validity = term_schema.evaluate(JSON(term_in.data)).output('detailed')
    if not validity['valid']:
        raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

    term = VocabularyTerm(
        vocabulary_id=vocabulary_id,
        term_id=term_in.id,
        data=term_in.data,
    )
    term.save()

    VocabularyTermAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.insert,
        timestamp=datetime.now(timezone.utc),
        _vocabulary_id=term.vocabulary_id,
        _term_id=term.term_id,
        _data=term.data,
    ).save()


@router.put(
    '/{vocabulary_id}/term',
)
async def update_term(
        vocabulary_id: str,
        term_in: VocabularyTermModelIn,
        term_schema: JSONSchema = Depends(get_vocabulary_schema),
        auth: Authorized = Depends(VocabularyAuthorize()),
):
    if not (term := Session.get(VocabularyTerm, (vocabulary_id, term_in.id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    # the id in the data cannot be changed
    term_in.data['id'] = term_in.id

    if term.data != term_in.data:
        validity = term_schema.evaluate(JSON(term_in.data)).output('detailed')
        if not validity['valid']:
            raise HTTPException(HTTP_422_UNPROCESSABLE_ENTITY, validity)

        term.data = term_in.data
        term.save()

        VocabularyTermAudit(
            client_id=auth.client_id,
            user_id=auth.user_id,
            command=AuditCommand.update,
            timestamp=datetime.now(timezone.utc),
            _vocabulary_id=term.vocabulary_id,
            _term_id=term.term_id,
            _data=term.data,
        ).save()


@router.delete(
    '/{vocabulary_id}/term/{term_id}',
)
async def delete_term(
        vocabulary_id: str,
        term_id: str,
        auth: Authorized = Depends(VocabularyAuthorize()),
):
    if not (term := Session.get(VocabularyTerm, (vocabulary_id, term_id))):
        raise HTTPException(HTTP_404_NOT_FOUND)

    term.delete()

    VocabularyTermAudit(
        client_id=auth.client_id,
        user_id=auth.user_id,
        command=AuditCommand.delete,
        timestamp=datetime.now(timezone.utc),
        _vocabulary_id=term.vocabulary_id,
        _term_id=term.term_id,
        _data=term.data,
    ).save()
