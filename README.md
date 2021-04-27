# topfood-backend Django

## Requirements

- [Python 3.9](https://www.python.org)
- [Docker](https://www.docker.com)
- [Docker Compose](https://docs.docker.com/compose/)
- [Virtualenv](https://github.com/pypa/virtualenv/)
- [Git](https://git-scm.com/)

## Development

- Create the virtual environment and activate it

        virtualenv -p python3 venv
        source venv/bin/activate
- Install the requirements `pip install -r requirements.txt`
- Start the dockers `docker-compose up` with the database and the localstack
- Run the server with `python manage.py runserver 8000`

You need a `.env`file with your environment variables, here's an example file:
```
LOAD_ENVS_FROM_FILE=True
ENVIRONMENT=development
SECRET_KEY='#*=topfood-backend Django=*#'
DEFAULT_FROM_EMAIL='topfood-backend <noreply@topfood-backend.com>'
DATABASE_URL=postgres://postgres:postgres@localhost:5432/topfood-backend
AWS_STORAGE_BUCKET_NAME=topfood-backend-backend
AWS_S3_REGION_NAME=us-east-1
SENTRY_DSN=
```

## Create S3 Bucket

To use the File Upload feature, you'll need to manually create the S3 Bucket. You can manage this by entering `python manage.py shell` and executing the following
```.python
[1]:    import boto3
[2]:    s3 = boto3.client('s3', endpoint_url='http://localhost:4566', aws_access_key_id='', aws_secret_access_key='')
[3]:    s3.create_bucket(Bucket='topfood-backend-backend', ACL='public-read')
``` 