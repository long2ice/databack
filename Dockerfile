FROM node as frontend-builder
RUN git clone https://github.com/long2ice/databack-web.git /databack-web
WORKDIR /databack-web
RUN npm install && npm run build

FROM golang as mongo-tools-builder
RUN apt update -y && apt install -y libkrb5-dev
RUN git clone https://github.com/mongodb/mongo-tools /mongo-tools
RUN cd /mongo-tools && ./make build -tools=mongodump,mongorestore

FROM snakepacker/python:3.11
RUN apt update -y && apt install -y mysql-client curl redis-tools
RUN echo "deb http://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -o /etc/apt/trusted.gpg.d/pgdg.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt update -y && apt install -y postgresql-client
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN mkdir -p /databack
WORKDIR /databack
COPY pyproject.toml poetry.lock /databack/
ENV POETRY_VIRTUALENVS_CREATE false
RUN curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py && pip3.11 install poetry && poetry install --no-root
COPY . /databack
RUN poetry install
COPY --from=frontend-builder /databack-web/dist /databack/static
COPY --from=mongo-tools-builder /mongo-tools/bin/mongodump /usr/bin/mongodump
COPY --from=mongo-tools-builder /mongo-tools/bin/mongorestore /usr/bin/mongorestore
ENTRYPOINT ["uvicorn", "databack.app:app", "--host", "0.0.0.0"]
CMD ["--port", "8000"]
