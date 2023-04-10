# databack

Backup your data from MySQL/PostgreSQL/SSH etc. to any other storages.

## Introduction

`databack` is a tool to back up your data from MySQL/PostgreSQL/SSH etc. to any other storages like S3, SCP etc. Which
can be run cron job to back up your data automatically.

## Screenshots

You can try it on [Demo](https://demo.databack.dev/) site.

![databack](./images/home.png)
![databack](./images/datasource.png)

## Features

- MySQL/PostgreSQL/SSH/Local data source.
- S3/SCP/Local storage.
- Cron job to back up your data automatically.
- i18n support.

## Deployment

The easiest way to deploy `databack` is to use `docker-compose`.

```yml
version: "3"
services:
  databack:
    restart: always
    env_file: .env
    network_mode: host
    image: ghcr.io/long2ice/databack/databack
  worker:
    restart: always
    env_file: .env
    network_mode: host
    image: ghcr.io/long2ice/databack/databack
    entrypoint: rearq databack.tasks:rearq worker -t
```

## Configuration

Just set environment variables in `.env` file.

```ini
DB_URL = mysql://root:123456@127.0.0.1:3306/databack
DEBUG = True
REDIS_URL = redis://127.0.0.1:6379/0
SENTRY_DSN = 'xxx'
ENV = production
```

## Frontend

The frontend project is [here](https://github.com/long2ice/databack-web).

## License

This project is licensed under the [Apache-2.0](./LICENSE) License.
