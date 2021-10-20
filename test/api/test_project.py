import pytest
from sqlalchemy import select

from odp.db import Session
from odp.db.models import Project
from test.factories import ProjectFactory, CollectionFactory


@pytest.fixture
def project_batch():
    return [
        ProjectFactory(collections=CollectionFactory.create_batch(3))
        for _ in range(5)
    ]


def collection_ids(project):
    return tuple(collection.id for collection in project.collections)


def assert_db_result(projects):
    Session.expire_all()
    result = Session.execute(select(Project)).scalars().all()
    assert set((row.id, row.name, collection_ids(row)) for row in result) \
           == set((project.id, project.name, collection_ids(project)) for project in projects)


def assert_json_result(json, project):
    assert json['id'] == project.id
    assert json['name'] == project.name
    assert tuple(json['collection_ids']) == collection_ids(project)


def test_get_project(api, project_batch):
    r = api.get(f'/project/{project_batch[2].id}')
    assert r.status_code == 200
    assert_json_result(r.json(), project_batch[2])
    assert_db_result(project_batch)


def test_create_project(api, project_batch):
    project_batch += [project := ProjectFactory.build()]
    r = api.post('/project/', json=dict(
        id=project.id,
        name=project.name,
        collection_ids=collection_ids(project),
    ))
    assert r.status_code == 200
    assert r.json() is None
    assert_db_result(project_batch)


def test_update_project(api, project_batch):
    project_batch[2] = ProjectFactory.build(
        id=project_batch[2].id,
        collections=CollectionFactory.create_batch(2),
    )
    r = api.put('/project/', json=dict(
        id=project_batch[2].id,
        name=project_batch[2].name,
        collection_ids=collection_ids(project_batch[2]),
    ))
    assert r.status_code == 200
    assert r.json() is None
    assert_db_result(project_batch)


def test_delete_project(api, project_batch):
    r = api.delete(f'/project/{project_batch[2].id}')
    del project_batch[2]
    assert r.status_code == 200
    assert r.json() is None
    assert_db_result(project_batch)
