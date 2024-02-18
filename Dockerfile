# Dockerfile for A_plus_tsukuba service container

# Download python image
# Python version is same as the production.
FROM python:3.8.10-buster

# Cast a spell
ENV PYTHONUNBUFFERED 1

# MySQL Connector
RUN apt-get update && apt-get install -y \
    default-mysql-client cron \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /aplus_mobile_fcm_server

# Install poerty
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false
    # venv is not used in the container

# Set working dir
WORKDIR /aplus_mobile_fcm_server

# Copy poetry files
COPY ./pyproject.toml* ./poetry.lock* ./

# Install Dependencies
RUN poetry install --no-root
# Cast a spell "--no-root" cf. https://github.com/python-poetry/poetry/issues/689 

# Copy .env for local
COPY ./.env_local ./.env
COPY ./firebaseServiceAccountKey.json ./firebaseServiceAccountKey.json

# Copy files
COPY ./manage.py ./
COPY ./pytest.ini ./

# Copy batch files
COPY ./batch_check_update.py ./batch_check_update.py
COPY ./batch_config_local.yaml ./batch_config.yaml

# NOTICE
# ./fcm_server and ./app are synchronized by volume configs in docker-compose.yml

# CRON
COPY ./crontab_local /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab
