FROM python:3.9-alpine3.13
LABEL maintainer="aprian.immanuel@danasaham.co.id"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
  /py/bin/pip install --upgrade pip && \
  apk add --update --no-cache postgresql-client && \
  apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev libffi-dev libressl-dev libxslt-dev libxml2-dev xmlsec-dev python3-dev zlib-dev jpeg-dev gcc libjpeg62-dev openssl-dev cmake alpine-sdk && \
  /py/bin/pip install -r /tmp/requirements.txt && \
  if [ $DEV = "true" ]; \
    then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
  fi && \
  rm -rf /tmp && \
  apk del .tmp-build-deps && \
  adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN mkdir -p /app/media/test_media && \
    chown -R django-user:django-user /py && \
    chown -R django-user:django-user /app/media

ENV PATH="/py/bin:$PATH"

USER django-user