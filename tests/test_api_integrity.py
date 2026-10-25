"""Проверки вложенных ресурсов и защиты связей между объектами."""

from http import HTTPStatus

import pytest

from posts.models import Comment, Post

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('method', ('get', 'post'))
def test_comments_require_existing_post(user_client, method):
    response = getattr(user_client, method)(
        '/api/v1/posts/99999/comments/', data={'text': 'Комментарий'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert not Comment.objects.exists()


@pytest.mark.parametrize('method', ('get', 'put', 'patch', 'delete'))
def test_comment_is_scoped_to_post(
    user_client, post, another_post, comment_1_post, method
):
    response = getattr(user_client, method)(
        f'/api/v1/posts/{another_post.pk}/comments/{comment_1_post.pk}/',
        data={'text': 'Изменённый текст'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_1_post.refresh_from_db()
    assert comment_1_post.post == post
    assert comment_1_post.text == 'Коммент 1'


@pytest.mark.parametrize('method', ('put', 'patch'))
def test_comment_links_cannot_be_reassigned(
    user_client, post, another_post, another_user, comment_1_post, method
):
    response = getattr(user_client, method)(
        f'/api/v1/posts/{post.pk}/comments/{comment_1_post.pk}/',
        data={
            'text': 'Новый текст',
            'author': another_user.username,
            'post': another_post.pk,
        },
    )
    assert response.status_code == HTTPStatus.OK
    comment_1_post.refresh_from_db()
    assert comment_1_post.author == post.author
    assert comment_1_post.post == post
    assert response.json()['text'] == 'Новый текст'


def test_comment_creation_uses_authenticated_user_and_url(
    user_client, user, another_user, post, another_post
):
    response = user_client.post(
        f'/api/v1/posts/{post.pk}/comments/',
        data={
            'text': 'Комментарий',
            'author': another_user.username,
            'post': another_post.pk,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    comment = Comment.objects.get(pk=response.json()['id'])
    assert comment.author == user
    assert comment.post == post


@pytest.mark.parametrize('method', ('post', 'put', 'patch'))
def test_post_author_cannot_be_assigned(
    user_client, user, another_user, post, method
):
    url = '/api/v1/posts/'
    if method != 'post':
        url += f'{post.pk}/'
    response = getattr(user_client, method)(
        url, data={'text': 'Пост', 'author': another_user.username}
    )
    expected_status = (
        HTTPStatus.CREATED if method == 'post' else HTTPStatus.OK
    )
    assert response.status_code == expected_status
    assert Post.objects.get(pk=response.json()['id']).author == user


def test_author_can_delete_comment(user_client, post, comment_1_post):
    response = user_client.delete(
        f'/api/v1/posts/{post.pk}/comments/{comment_1_post.pk}/'
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not Comment.objects.filter(pk=comment_1_post.pk).exists()


@pytest.mark.parametrize('method', ('put', 'patch', 'delete'))
def test_groups_cannot_be_changed(user_client, group_1, method):
    response = getattr(user_client, method)(
        f'/api/v1/groups/{group_1.pk}/', data={'title': 'Другая группа'}
    )
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    original_title = group_1.title
    group_1.refresh_from_db()
    assert group_1.title == original_title
