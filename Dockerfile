FROM node as frontend-builder
RUN git clone https://github.com/long2ice/databack-web.git /databack-web
WORKDIR /databack-web
RUN npm install && npm run build

FROM snakepacker/python:3.11
RUN apt update -y && apt install -y mysql-client curl redis-tools
RUN curl -o mongo.deb https://fastdl.mongodb.org/tools/db/mongodb-database-tools-ubuntu2204-x86_64-100.7.0.deb
RUN dpkg -i mongo.deb && rm mongo.deb
RUN echo "deb http://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -o /etc/apt/trusted.gpg.d/pgdg.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc
RUN apt update -y && apt install -y postgresql-client
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN mkdir -p /databack
WORKDIR /databack
COPY pyproject.toml poetry.lock /databack/
ENV POETRY_VIRTUALENVS_CREATE false
RUN curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py && pip install poetry && poetry install --no-root
COPY . /databack
RUN poetry install
COPY --from=frontend-builder /databack-web/dist /databack/static
ENTRYPOINT ["uvicorn", "databack.app:app", "--host", "0.0.0.0"]
CMD ["--port", "8000"]
