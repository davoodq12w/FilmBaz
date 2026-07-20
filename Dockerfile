FROM python:3.13

LABEL authors="davoodq12w"
LABEL author_email="davod.q12w@gmail.com"

WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN mkdir -p /app/staticfiles

EXPOSE 8000
