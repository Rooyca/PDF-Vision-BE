web: gunicorn -w 3 -k uvicorn.workers.UvicornWorker main:app
worker: celery -A main.celery worker