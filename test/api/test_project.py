from random import randint

import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Project
from test.api import assert_empty_result, assert_forbidden, all_scopes, all_scopes_excluding
from test.factories import ProjectFactory, CollectionFactory


@pytest.fixture
def project_batch():
    """Create and commit a batch of Project instances."""
    return [
        ProjectFactory(collections=CollectionFactory.create_batch(randint(0, 3)))
        for _ in range(randint(3, 5))
    ]


def project_build(**id):
    """Build and return an uncommitted Project instance.
    Referenced collections are however committed."""
    return ProjectFactory.build(
        **id,
        collections=CollectionFactory.create_batch(randint(0, 3)),
    )


def collection_ids(project):
    return tuple(collection.id for collection in project.collections)


def assert_db_state(projects):
    """Verify that the DB project table contains the given project batch."""
    Session.expire_all()
    result = Session.execute(select(Project)).scalars().all()
    assert set((row.id, row.name, collection_ids(row)) for row in result) \
           == set((project.id, project.name, collection_ids(project)) for project in projects)


def assert_json_result(response, json, project):
    """Verify that the API result matches the given project object."""
    assert response.status_code == 200
    assert json['id'] == project.id
    assert json['name'] == project.name
    assert tuple(json['collection_ids']) == collection_ids(project)


def assert_json_results(response, json, projects):
    """Verify that the API result list matches the given project batch."""
    json.sort(key=lambda j: j['id'])
    projects.sort(key=lambda p: p.id)
    for n, project in enumerate(projects):
        assert_json_result(response, json[n], project)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROJECT_READ], True),
    ([ODPScope.PROJECT_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROJECT_READ, ODPScope.PROJECT_ADMIN), False),
])
def test_list_projects(api, project_batch, scopes, authorized):
    r = api(scopes).get('/project/')
    if authorized:
        assert_json_results(r, r.json(), project_batch)
    else:
        assert_forbidden(r)
    assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROJECT_READ], True),
    ([ODPScope.PROJECT_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROJECT_READ, ODPScope.PROJECT_ADMIN), False),
])
def test_get_project(api, project_batch, scopes, authorized):
    r = api(scopes).get(f'/project/{project_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), project_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROJECT_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROJECT_ADMIN), False),
])
def test_create_project(api, project_batch, scopes, authorized):
    modified_project_batch = project_batch + [project := project_build()]
    r = api(scopes).post('/project/', json=dict(
        id=project.id,
        name=project.name,
        collection_ids=collection_ids(project),
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_project_batch)
    else:
        assert_forbidden(r)
        assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROJECT_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROJECT_ADMIN), False),
])
def test_update_project(api, project_batch, scopes, authorized):
    modified_project_batch = project_batch.copy()
    modified_project_batch[2] = (project := project_build(id=project_batch[2].id))
    r = api(scopes).put('/project/', json=dict(
        id=project.id,
        name=project.name,
        collection_ids=collection_ids(project),
    ))
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_project_batch)
    else:
        assert_forbidden(r)
        assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([ODPScope.PROJECT_ADMIN], True),
    ([], False),
    (all_scopes, True),
    (all_scopes_excluding(ODPScope.PROJECT_ADMIN), False),
])
def test_delete_project(api, project_batch, scopes, authorized):
    modified_project_batch = project_batch.copy()
    del modified_project_batch[2]
    r = api(scopes).delete(f'/project/{project_batch[2].id}')
    if authorized:
        assert_empty_result(r)
        assert_db_state(modified_project_batch)
    else:
        assert_forbidden(r)
        assert_db_state(project_batch)
