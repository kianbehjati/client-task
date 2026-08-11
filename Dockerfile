FROM python:3.14-alpine3.23

WORKDIR /code

ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .