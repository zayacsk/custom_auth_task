# custom_auth_task

REST API на Django + Django REST Framework с кастомной JWT-аутентификацией и RBAC-моделью доступа.

## Стек

- Python 3.11+
- Django 6
- Django REST Framework
- PostgreSQL
- `psycopg2-binary`
- `bcrypt`
- `PyJWT`


## Сценарий первого запуска


```bash
sudo -u postgres psql
```

```sql
CREATE USER myproject_user WITH PASSWORD 'my_password';
CREATE DATABASE myproject_db OWNER myproject_user;
```

```bash
git clone <repo_url>
cd custom_auth_task
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd custom_auth_task
python manage.py migrate
python manage.py init_rbac
python manage.py runserver
```

## Аутентификация

Проект использует JWT.

Для защищённых endpoint-ов нужно передавать заголовок:

```http
Authorization: Bearer <token>
```

Токен возвращается после успешного логина через `/api/login/`.

После logout токен попадает в blacklist и больше не должен использоваться.

## Endpoint-ы

Ниже перечислены все основные endpoint-ы, их назначение и ограничения по доступу.

### Публичные endpoint-ы

#### `POST /api/register/`

Регистрация нового пользователя.

Пример тела запроса:

```json
{
  "first_name": "Ivan",
  "last_name": "Petrov",
  "email": "ivan@example.com",
  "password": "strong_password",
  "password_repeat": "strong_password"
}
```

Что делает:

- создаёт пользователя
- хэширует пароль через `bcrypt`
- автоматически назначает роль `user`

#### `POST /api/login/`

Вход пользователя и получение JWT-токена.

Пример тела запроса:

```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Что возвращает:

- JWT-токен
- информацию о пользователе

### Пользовательские endpoint-ы

#### `POST /api/logout/`

Выход из системы.

Что делает:

- берёт текущий токен из заголовка `Authorization`
- добавляет его в blacklist

#### `GET /api/users/`

Получение списка активных пользователей.

Доступ:

- нужен permission `read:users`

#### `GET /api/users/<user_id>/`

Получение данных конкретного пользователя.

Доступ:

- permission `read:users`
- либо владелец собственного профиля

#### `PUT /api/users/<user_id>/`

Обновление пользователя.

Можно обновить:

- `first_name`
- `last_name`
- `password`

Доступ:

- permission `update:users`
- либо владелец собственного профиля

#### `DELETE /api/users/<user_id>/`

Деактивация пользователя.

Что делает:

- не удаляет запись физически
- устанавливает `is_active = False`

Доступ:

- permission `delete:users`
- либо владелец собственного профиля

### Административные endpoint-ы

Все endpoint-ы ниже требуют роль `admin`.

#### Роли

#### `GET /api/admin/roles/`

Получение списка ролей.

#### `POST /api/admin/roles/`

Создание новой роли.

Пример тела запроса:

```json
{
  "name": "manager",
  "description": "Manager role"
}
```

#### `PUT /api/admin/roles/<role_id>/`

Обновление роли.

#### `DELETE /api/admin/roles/<role_id>/`

Удаление роли.

#### Ресурсы

#### `GET /api/admin/resources/`

Получение списка ресурсов.

#### `POST /api/admin/resources/`

Создание ресурса.

Пример тела запроса:

```json
{
  "name": "reports",
  "description": "Reports management"
}
```

#### `PUT /api/admin/resources/<resource_id>/`

Обновление ресурса.

#### `DELETE /api/admin/resources/<resource_id>/`

Удаление ресурса.

#### Разрешения

#### `POST /api/admin/permissions/`

Создание разрешения для ресурса.

Пример тела запроса:

```json
{
  "action": "read",
  "resource_id": 1
}
```

#### `DELETE /api/admin/permissions/<permission_id>/`

Удаление разрешения.

#### Назначение разрешений ролям

#### `POST /api/admin/roles/assign-permission/`

Назначение разрешения роли.

Пример тела запроса:

```json
{
  "role_id": 2,
  "permission_id": 5
}
```

#### `DELETE /api/admin/roles/remove-permission/`

Удаление разрешения у роли.

Пример тела запроса:

```json
{
  "role_id": 2,
  "permission_id": 5
}
```

#### Назначение ролей пользователям

#### `POST /api/admin/users/assign-role/`

Назначение роли пользователю.

Пример тела запроса:

```json
{
  "user_id": 3,
  "role_id": 2
}
```

#### `DELETE /api/admin/users/remove-role/`

Удаление роли у пользователя.

Пример тела запроса:

```json
{
  "user_id": 3,
  "role_id": 2
}
```

### Endpoint-ы для проектов

#### `GET /api/projects/`

Получение списка проектов.

Доступ:

- permission `read:project`

По умолчанию роль `user` после регистрации имеет именно это право.

#### `POST /api/projects/`

Создание проекта.

Пример тела запроса:

```json
{
  "name": "Internal CRM",
  "description": "Project for internal use"
}
```

Доступ:

- permission `create:project`

#### `GET /api/projects/<project_id>/`

Получение проекта по идентификатору.

Доступ:

- permission `read:project`

#### `PUT /api/projects/<project_id>/`

Обновление проекта.

Доступ:

- permission `update:project`

#### `DELETE /api/projects/<project_id>/`

Удаление проекта.

Доступ:

- permission `delete:project`

## Рекомендуемая последовательность работы с API

Ниже удобный порядок, в котором обычно используют это API.

### Сценарий администратора

1. Запустить проект и выполнить `python manage.py init_rbac`.
2. Выполнить `POST /api/login/` с `ADMIN_EMAIL` и `ADMIN_PASSWORD`.
3. Получить JWT-токен администратора.
4. При необходимости просмотреть роли через `GET /api/admin/roles/`.
5. При необходимости создать новую роль через `POST /api/admin/roles/`.
6. При необходимости создать новый ресурс через `POST /api/admin/resources/`.
7. При необходимости создать разрешение через `POST /api/admin/permissions/`.
8. Назначить разрешение роли через `POST /api/admin/roles/assign-permission/`.
9. Зарегистрировать обычного пользователя через `POST /api/register/` или использовать уже существующего.
10. Назначить пользователю роль через `POST /api/admin/users/assign-role/`.

### Сценарий обычного пользователя

1. Выполнить `POST /api/register/`.
2. Выполнить `POST /api/login/`.
3. Сохранить JWT-токен.
4. Работать с доступными endpoint-ами, передавая `Authorization: Bearer <token>`.
5. По умолчанию после регистрации пользователь может читать список проектов через `GET /api/projects/`.
6. Если администратор выдаст дополнительные права, пользователь сможет создавать, изменять или удалять проекты и работать с другими сущностями в рамках назначенных permissions.
7. По завершении сессии вызвать `POST /api/logout/`.

## Минимальная проверка после запуска

После старта сервера можно проверить проект в таком порядке:

1. `POST /api/login/` под администратором.
2. `GET /api/admin/roles/` с токеном администратора.
3. `POST /api/register/` для создания обычного пользователя.
4. `POST /api/login/` под обычным пользователем.
5. `GET /api/projects/` с токеном обычного пользователя.
