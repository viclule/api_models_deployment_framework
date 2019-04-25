FROM python:3.7-alpine
MAINTAINER Vicente Guerrero

ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
# delete the temporal requirements
RUN apk del .tmp-build-deps

# Setup directory structure
RUN mkdir /src
WORKDIR /src
COPY ./src/ /src

RUN adduser -D user
USER user
