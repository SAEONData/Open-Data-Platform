from odp import ODPScope

all_scopes = [s for s in ODPScope]


def all_scopes_excluding(scope):
    return [s for s in ODPScope if s != scope]


def assert_empty_result(response):
    assert response.status_code == 200
    assert response.json() is None


def assert_forbidden(response):
    assert response.status_code == 403
    assert response.json() == {'detail': 'Forbidden'}


def assert_method_not_allowed(response):
    assert response.status_code == 405
    assert response.json() == {'detail': 'Method Not Allowed'}


def assert_unprocessable(response, message):
    assert response.status_code == 422
    assert response.json() == {'detail': message}
