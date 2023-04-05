FROM python:3.11 as builder
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN mkdir -p /databack
WORKDIR /databack
COPY pyproject.toml poetry.lock /databack/
ENV POETRY_VIRTUALENVS_CREATE false
RUN pip3 install poetry && poetry install --no-root
COPY . /databack
RUN poetry install

FROM node as frontend-builder
RUN git clone https://github.com/long2ice/databack-web.git /databack-web
WORKDIR /databack-web
RUN npm install && npm run build

FROM python:3.11-slim
WORKDIR /databack
RUN apt update -y && apt install -y default-mysql-client postgresql-client
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /databack /databack
COPY --from=frontend-builder /databack-web/dist /databack/static
ENTRYPOINT ["uvicorn", "databack.app:app", "--host", "0.0.0.0"]
CMD ["--port", "8000"]
