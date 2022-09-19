FROM python:3.10

WORKDIR /app

COPY Pipfile* ./

RUN apt-get update \
    && pip install --upgrade pip && pip install pipenv \
    && pipenv install --system --deploy

COPY . /app
