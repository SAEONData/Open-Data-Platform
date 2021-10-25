import pytest
from sqlalchemy import select

from odp import ODPScope
from odp.db import Session
from odp.db.models import Project
from test.api import assert_empty_result, assert_forbidden
from test.factories import ProjectFactory, CollectionFactory


@pytest.fixture
def project_batch():
    return [
        ProjectFactory(collections=CollectionFactory.create_batch(3))
        for _ in range(5)
    ]


def collection_ids(project):
    return tuple(collection.id for collection in project.collections)


def assert_db_state(projects):
    Session.expire_all()
    result = Session.execute(select(Project)).scalars().all()
    assert set((row.id, row.name, collection_ids(row)) for row in result) \
           == set((project.id, project.name, collection_ids(project)) for project in projects)


def assert_json_result(response, json, project):
    assert response.status_code == 200
    assert json['id'] == project.id
    assert json['name'] == project.name
    assert tuple(json['collection_ids']) == collection_ids(project)


def assert_json_results(response, json, projects):
    for n, project in enumerate(sorted(projects, key=lambda p: p.id)):
        assert_json_result(response, json[n], project)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.PROJECT_READ], True),
    ([ODPScope.PROJECT_ADMIN], False),
    ([ODPScope.PROJECT_ADMIN, ODPScope.PROJECT_READ], True),
])
def test_list_projects(api, project_batch, scopes, authorized):
    r = api(scopes).get('/project/')
    if authorized:
        assert_json_results(r, r.json(), project_batch)
    else:
        assert_forbidden(r)
    assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.PROJECT_READ], True),
    ([ODPScope.PROJECT_ADMIN], False),
    ([ODPScope.PROJECT_ADMIN, ODPScope.PROJECT_READ], True),
])
def test_get_project(api, project_batch, scopes, authorized):
    r = api(scopes).get(f'/project/{project_batch[2].id}')
    if authorized:
        assert_json_result(r, r.json(), project_batch[2])
    else:
        assert_forbidden(r)
    assert_db_state(project_batch)


@pytest.mark.parametrize('scopes, authorized', [
    ([], False),
    ([ODPScope.PROJECT_READ], False),
    ([ODPScope.PROJECT_ADMIN], True),
    ([ODPScope.PROJECT_ADMIN, ODPScope.PROJECT_READ], True),
])
def test_create_project(api, project_batch, scopes, authorized):
    modified_project_batch = project_batch + [project := ProjectFactory.build()]
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
    ([], False),
    ([ODPScope.PROJECT_READ], False),
    ([ODPScope.PROJECT_ADMIN], True),
    ([ODPScope.PROJECT_ADMIN, ODPScope.PROJECT_READ], True),
])
def test_update_project(api, project_batch, scopes, authorized):
    modified_project_batch = project_batch.copy()
    modified_project_batch[2] = (project := ProjectFactory.build(
        id=project_batch[2].id,
        collections=CollectionFactory.create_batch(2),
    ))
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
    ([], False),
    ([ODPScope.PROJECT_READ], False),
    ([ODPScope.PROJECT_ADMIN], True),
    ([ODPScope.PROJECT_ADMIN, ODPScope.PROJECT_READ], True),
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
