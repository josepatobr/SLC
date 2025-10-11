FROM python:3.8-slim

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

RUN pip install --upgrade pip && pip install uv


ENV DOCKERIZE_VERSION=v1.0.0

RUN curl -sSL https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64.tar.gz \
  | tar -C /usr/local/bin -xzv

COPY pyproject.toml uv.lock ${APP_HOME}

RUN uv sync --no-install-project

COPY . ${APP_HOME}

RUN uv sync

RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid 1000 --shell /bin/sh --create-home dev-user \
  && chown -R dev-user:dev-user ${APP_HOME}

USER dev-user

ENV PATH="/${APP_HOME}/.venv/bin:$PATH"

EXPOSE 8000


CMD ["dockerize", "-wait", "tcp://redis:6379", "-timeout", "30s", "uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
