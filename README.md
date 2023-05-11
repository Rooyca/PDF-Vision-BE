# PDFVision Backend

- ~Check out PDFVision [here](https://pdf.rooyca.xyz)~.
- Check out the Frond-End [here](https://github.com/Rooyca/PDF-Vision).

To run locally you need to run FastAPI with:

> uvicorn main:app --reload

And Celery:

> celery -A task worker --loglevel=info

And you can run a container with Redis and other with MongoDB.

### To run Celery on Windows 

> pip install eventlet

> celery -A <module> worker -l info -P eventlet
