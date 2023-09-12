FROM python:3.11.4-slim-buster
LABEL maintainer="amirammina@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /vol/web/media

