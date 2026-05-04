FROM python:3.12-slim

LABEL authors="davoodq12w"
LABEL author_email="davod.q12w@gmail.com"

WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY rq.txt /app/
RUN pip install -U pip
RUN pip install --no-cache-dir -r rq.txt \
    --index-url https://mirror.abrha.net/repository/pypi/simple \
    --trusted-host mirror.abrha.net

COPY . /app/
RUN mkdir -p /app/staticfiles

EXPOSE 8000
