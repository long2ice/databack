FROM node as frontend-builder
ARG GIT_TOKEN
RUN git clone https://$GIT_TOKEN@github.com/long2ice/databack-web.git /databack-web
WORKDIR /databack-web
RUN npm install && npm run build

FROM golang as tools-builder
RUN apt update -y && apt install -y libkrb5-dev
RUN git clone https://github.com/mongodb/mongo-tools /mongo-tools
RUN cd /mongo-tools && ./make build -tools=mongodump,mongorestore
RUN git clone https://github.com/yannh/redis-dump-go.git /redis-dump-go
RUN cd /redis-dump-go && go build -o /redis-dump-go/redis-dump-go
RUN go install github.com/AlexAkulov/clickhouse-backup/cmd/clickhouse-backup@latest

FROM snakepacker/python:3.11
RUN apt update -y && apt install -y mysql-client curl redis-tools gcc libc6-dev python3.11-dev
RUN echo "deb http://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -o /etc/apt/trusted.gpg.d/pgdg.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt update -y && apt install -y postgresql-client-16
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV POETRY_VIRTUALENVS_CREATE=false
RUN mkdir -p /databack
COPY --from=frontend-builder /databack-web/dist /databack/static
COPY --from=tools-builder /mongo-tools/bin/mongodump /usr/bin/mongodump
COPY --from=tools-builder /mongo-tools/bin/mongorestore /usr/bin/mongorestore
COPY --from=tools-builder /redis-dump-go/redis-dump-go /usr/bin/redis-dump-go
COPY --from=tools-builder /go/bin/clickhouse-backup /usr/bin/clickhouse-backup
WORKDIR /databack
COPY ../pyproject.toml poetry.lock /databack/
RUN curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py && pip3.11 install poetry && poetry install --no-root && rm get-pip.py
COPY .. /databack
RUN poetry install
CMD ["python3.11", "-m", "databack.app"]
