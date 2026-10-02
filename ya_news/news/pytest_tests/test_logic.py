from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст комментария'}


def test_anonymous_cannot_create_comment(
    client,
    detail_url,
    login_url,
):
    comments_count = Comment.objects.count()

    response = client.post(detail_url, data=FORM_DATA)

    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == comments_count


def test_author_can_create_comment(
    author,
    author_client,
    news,
    detail_url,
):
    comments_count = Comment.objects.count()

    response = author_client.post(detail_url, data=FORM_DATA)

    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_comment_with_bad_words_is_not_created(
    author_client,
    detail_url,
    bad_word,
):
    comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой же ты {bad_word}!'}

    response = author_client.post(detail_url, data=bad_words_data)

    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    detail_url,
):
    comments_count = Comment.objects.count()

    response = author_client.post(edit_url, data=FORM_DATA)

    updated = Comment.objects.get(pk=comment.pk)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == comments_count
    assert updated.text == FORM_DATA['text']
    assert updated.author == comment.author
    assert updated.news == comment.news


def test_not_author_cannot_edit_comment(
    not_author_client,
    comment,
    edit_url,
):
    response = not_author_client.post(edit_url, data=FORM_DATA)

    saved = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert saved.text == comment.text
    assert saved.author == comment.author
    assert saved.news == comment.news


def test_author_can_delete_comment(
    author_client,
    comment,
    delete_url,
    detail_url,
):
    response = author_client.post(delete_url)

    assertRedirects(response, f'{detail_url}#comments')
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_not_author_cannot_delete_comment(
    not_author_client,
    comment,
    delete_url,
):
    response = not_author_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
