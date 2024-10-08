FROM python:3.12-slim-bookworm AS requirements-stage

WORKDIR /tmp

RUN pip install --upgrade pip && pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y default-libmysqlclient-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /app
