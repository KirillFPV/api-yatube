# API Yatube

REST API для постов, групп и комментариев на Django REST Framework.
Все ресурсы доступны только пользователям с токеном. Изменять и удалять
посты и комментарии может только их автор. Группы доступны для чтения;
управлять ими можно через админку Django.

## Запуск

Используйте Python 3.10–3.12 и выполните команды из корня репозитория:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cd yatube_api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Пользователей и группы можно создавать в админке: `http://127.0.0.1:8000/admin/`.

## Получение токена

```bash
curl -X POST http://127.0.0.1:8000/api/v1/api-token-auth/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "your_username", "password": "your_password"}'
```

Ответ: `{"token": "..."}`. В последующих запросах передавайте заголовок
`Authorization: Token <полученный токен>`.

## Эндпоинты

| Адрес | Методы | Назначение |
| --- | --- | --- |
| `/api/v1/api-token-auth/` | POST | Получить токен по логину и паролю |
| `/api/v1/posts/` | GET, POST | Получить посты или создать пост |
| `/api/v1/posts/{post_id}/` | GET, PUT, PATCH, DELETE | Получить, изменить или удалить пост |
| `/api/v1/groups/` | GET | Получить группы |
| `/api/v1/groups/{group_id}/` | GET | Получить группу |
| `/api/v1/posts/{post_id}/comments/` | GET, POST | Получить комментарии поста или создать комментарий |
| `/api/v1/posts/{post_id}/comments/{comment_id}/` | GET, PUT, PATCH, DELETE | Получить, изменить или удалить комментарий |

При создании поста передайте обязательное поле `text`, при необходимости —
`group` (идентификатор группы) и `image` (файл в multipart-запросе).
При создании комментария передайте `text`: пост определяется адресом запроса.
Автор всегда определяется по токену.

Запросы POST возвращают созданный объект и статус 201, PUT и PATCH —
изменённый объект и статус 200, DELETE — статус 204 без тела ответа.
Без действительного токена API возвращает 401, при изменении чужого контента —
403, при обращении к отсутствующему объекту — 404.

## Проверки

Из корня репозитория с активированным окружением:

```bash
pytest
flake8
python yatube_api/manage.py check
```

Дополнительная коллекция запросов и инструкция к ней находятся
в `postman_collection/`. Скрипт её подготовки очищает базу данных;
запускайте его только для тестовой базы.
