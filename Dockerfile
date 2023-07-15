FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

#CMD ["sh", "-c", "celery -A tasks worker --loglevel=info & uvicorn main:app --host=0.0.0.0 --port 8000"]
