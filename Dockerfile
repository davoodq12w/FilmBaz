FROM python:latest

LABEL authors="davoodq12w"
LABEL author_email="davod.q12w@gmail.com"

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY rq.txt /app/
RUN pip install -U pip
RUN pip install --no-cache-dir -r rq.txt

COPY . /app/

RUN mkdir -p /app/static

EXPOSE 8000

CMD ["gunicorn", "FilmBaz.wsgi:application", "--bind", "0.0.0.0:8000"]

