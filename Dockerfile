FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate
RUN python superuser.py
EXPOSE 8000

CMD ["uvicorn", "TglabTest.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
