# databack

`databack` is a tool to back up your data from MySQL/PostgreSQL/SSH etc. to any other storages like S3, SCP etc. Which
can be run cron job to back up your data automatically, and you can also restore your data from backup files.

## Features

- MySQL/PostgreSQL/SSH/Local data source.
- S3/SCP/Local storage.
- Cron job to back up your data automatically.
- i18n support (English and Chinese).
- Web UI to manage your backup tasks.

## Screenshots

You can try it on [Demo](https://demo.databack.dev/) site.

![databack](./images/home.png)
![databack](./images/datasource.png)

## Pro Version

There is also a paid pro version, which has more features:

- Admin management and access control.
- More data sources and storages. (coming soon)
- Action logs audit.
- Feature request and technical support.
- More features coming soon.

Demo site: [https://pro.databack.dev/login](https://pro.databack.dev/login)

- **email**: `demo@databack.dev`
- **password**: `123456`

You can also [contact me](mailto:long2ice@gmail.com) to get a trial license.

## Deployment

The easiest way to deploy `databack` is to use `docker-compose`.

```yml
version: "3"
services:
  databack:
    restart: always
    env_file: .env
    network_mode: host
    image: ghcr.io/long2ice/databack/databack:full
```

## Configuration

Just set environment variables in `.env` file.

```dotenv
DB_URL=mysql://root:123456@127.0.0.1:3306/databack
DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/0
SENTRY_DSN='xxx' # remove it if you don't use sentry
ENV=production
WORKER=True
```

## Worker

By default, `databack` will start a builtin worker to run tasks when environment variable `WORKER` is `True`. If you
want to start multiple workers, you can run `rearq databack.tasks:rearq worker` command.

For `docekr-compose` deployment:

```yml
version: "3"
services:
  worker:
    restart: always
    env_file: .env
    network_mode: host
    image: ghcr.io/long2ice/databack/databack:full
    entrypoint: rearq databack.tasks:rearq worker -t
```

## Timezone

By default, `databack` will use `UTC` timezone for `cron` expression. If you want to use other timezone, you can set
environment variable `TZ` to your timezone.

## Frontend

The frontend project is [here](https://github.com/long2ice/databack-web).

## License

This project is licensed under the [Apache-2.0](./LICENSE) License.
