from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    (
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'author_client', HTTPStatus.OK),
        ('edit_url', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'not_author_client', HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_status_codes(
    request,
    url_fixture,
    client_fixture,
    expected_status,
):
    url = request.getfixturevalue(url_fixture)
    current_client = request.getfixturevalue(client_fixture)

    response = current_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize('url_fixture', ('edit_url', 'delete_url'))
def test_anonymous_user_is_redirected_to_login(
    client,
    login_url,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)

    assertRedirects(response, f'{login_url}?next={url}')


def test_authorized_user_logs_out_by_post_request(
    author_client,
    logout_url,
):
    response = author_client.post(logout_url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session
