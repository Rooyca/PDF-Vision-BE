# PDF2Slide - Convert PDF to Slides (Backend)

This is the backend of PDF2Slide. It is built using Python and FastApi. It uses Celery to run tasks asynchronously, Redis as a message broker and MongoDB as a database.

- Check out the Frond-end [here](https://github.com/Rooyca/PDF-Vision)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## Installation

We currently support 3 ways to install and run the backend. The first one is using Docker, the second one is using Docker-compose and the third one is manually installing the dependencies and running the backend.

### Docker-compose (recommended)

To run the backend using Docker-compose you should edit the file `docker-compose.yml` and change the following variables:

```bash
- SMTP_SERVER=smtp-relay.sendinblue.com
- SMTP_USER=user@mail.com
- SMTP_PASS=password
- SMTP_PORT=587
- SENDER=sender@mail.com
- S3_ENDPOINT=https://11111.r2.cloudflarestorage.com
- KEY_ID=id
- KEY_SECRET=secret
- URL_STORAGE=https://example.com/
```

For `S3_ENDPOINT` you can use the cloudflare storage or any other storage that supports S3.

After that you can run the following command to run the entire stack:

```bash
docker-compose up -d
```

### Docker

To run the backend using Docker you need to have Docker installed on your machine. You can find instructions on how to install Docker [here](https://docs.docker.com/get-docker/).

Once you have Docker installed you can run the following command to build the backend image:

```bash
docker run -e MONGO='mongodb://localhost:27017/' \
       -e CELERY_BROKER_URL='redis://localhost:6379/0' \
       -e CELERY_RESULT_BACKEND='redis://localhost:6379/0' \
        rooyca/pdf2slide-be:slim
```

We need to make sure that MongoDB and Redis are running before running the command above. You can run the following commands to run MongoDB and Redis using Docker:

```bash
docker run -d -p 27017:27017 mongo
docker run -d -p 6379:6379 redis
```

### Manual

To run the backend manually you need to have Python 3.9 installed on your machine. You can find instructions on how to install Python [here](https://www.python.org/downloads/).

Once you have Python installed you can run the following command to install the dependencies:

```bash
pip install -r requirements.txt
```

We also need to make sure that MongoDB and Redis are running before running the backend. You can run the following commands to run MongoDB and Redis using Docker:

```bash
docker run -d -p 27017:27017 mongo
docker run -d -p 6379:6379 redis
```

Finally, you can run the backend using the following command:

```bash
uvicorn main:app --reload
celery -A main worker --loglevel=info
```

#### To run Celery on Windows 

```bash
pip install eventlet
celery -A main worker -l info -P eventlet
```

Now you can access `http://localhost:8000/docs` to see the API documentation.

### Fly.io

You can also run the backend on Fly.io. You can find instructions on how to install Fly.io [here](https://fly.io/docs/getting-started/installing-flyctl/).

Once you have Fly.io installed you can run the following command to deploy the backend:

```bash
flyctl launch
```

After the configuration is done you can add envairoment variables. To do so you can check the `fly.toml.example` file. Then run the following command to deploy the app:


```bash
flyctl deploy
```

## Usage

You can allways read the API documentation at `http://localhost:8000/docs`. Shortly, you can use the following endpoints:

### POST /files

This endpoint is used to upload a file. You can upload a file using the following command:

```bash
curl -X 'POST' \
  'https://localhost:8000/files/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@INV_2023_00006.pdf;type=application/pdf' \
  -F 'owner_email=example@example.com' \
  -F 'slides_name=slideName'
```

### GET /files/{task_id}

This endpoint is used to get the status of a task. You can get the status of a task using the following command:

```bash
curl -X 'GET' \
  'https://localhost:8000/files/{task_id}' \
  -H 'accept: application/json'
```

### DELETE /files/{task_id}

This endpoint is used to delete a slide. You can delete a slide using the following command:

```bash
curl -X 'DELETE' \
  'https://localhost:8000/files/{task_id}' \
  -H 'accept: application/json'
```


## Contributing

Contributions are always welcome! <3


## Contact

You can contact me at:

- [Mas.to](https://mas.to/@rooyca)
- [Telegram](https://t.me/seiseiseis)
