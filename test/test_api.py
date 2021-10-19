from sqlalchemy import select

from odp.db import Session
from odp.db.models import Project
from test.factories import ProjectFactory


def test_create_project(api):
    project = ProjectFactory.stub()
    r = api.post('/project/', json=dict(
        id=project.id,
        name=project.name,
    ))
    assert r.status_code == 200
    assert r.json() is None

    result = Session.execute(select(Project)).scalar_one()
    assert (result.id, result.name) == (project.id, project.name)


def test_update_project(api):
    projects = ProjectFactory.create_batch(2)
    projects[0] = ProjectFactory.stub(id=projects[0].id)
    r = api.put('/project/', json=dict(
        id=projects[0].id,
        name=projects[0].name,
    ))
    assert r.status_code == 200
    assert r.json() is None

    result = Session.execute(select(Project)).scalars().all()
    assert set((row.id, row.name) for row in result) \
           == set((project.id, project.name) for project in projects)


def test_delete_project(api):
    projects = ProjectFactory.create_batch(2)
    r = api.delete(f'/project/{projects[0].id}')

    assert r.status_code == 200
    assert r.json() is None

    result = Session.execute(select(Project)).scalar_one()
    assert (result.id, result.name) == (projects[1].id, projects[1].name)
