FROM python:3.13-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /app/


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]