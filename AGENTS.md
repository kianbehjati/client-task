# AGENTS.md

- **Stack**: Django 6.1, Django REST Framework, PostgreSQL 18, Celery, Celery Beat, `uv`, `ruff`.
- **Commands**:
  - Run app: `docker compose up --build`
  - Run tests: `python manage.py test` (or inside container via docker compose)
  - Run migrations: `python manage.py makemigrations && python manage.py migrate`
  - Format & lint: `ruff format . && ruff check .`
  - Package management: `uv pip install -r requirements.txt` (using `.venv`)
- **Environment**: Requires `.env` file containing `SECRET_KEY`, `DEBUG`, `DB_USER`, `DB_PASSWORD`. Database uses Docker secrets (`db_user.txt`, `db_passowrd.txt`).
