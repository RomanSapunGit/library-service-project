FROM python:3.10-alpine3.21

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache gcc musl-dev python3-dev linux-headers

RUN pip install -r requirements.txt

COPY . .

RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user