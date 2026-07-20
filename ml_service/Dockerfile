FROM python:3.12-slim

# جلوگیری از ساخت فایل‌های pyc
ENV PYTHONDONTWRITEBYTECODE=1

# لاگ‌ها مستقیم داخل ترمینال
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نصب dependency ها
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# پورت FastAPI
EXPOSE 8002

# اجرای FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]