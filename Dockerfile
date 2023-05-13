FROM python:3.9-slim

WORKDIR /app

COPY . /app

ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "celery -A tasks worker --loglevel=info & uvicorn main:app --host=0.0.0.0 --port 8000"]
