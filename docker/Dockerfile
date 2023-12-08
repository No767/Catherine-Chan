####################################################################################################
## Builder image
####################################################################################################
FROM python:3.11-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  curl \
  git \
  && apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /catherine

COPY /pyproject.toml /catherine/
COPY /poetry.lock /catherine/

RUN poetry export --output requirements.txt --without-hashes --only main

####################################################################################################
## Final image
####################################################################################################
FROM python:3.11-slim-bookworm

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  tini \
  bash \
  netcat-traditional \
  git \
  && apt-get clean

WORKDIR /catherine
COPY /bot/ /catherine/bot
COPY /migrations /catherine/migrations
COPY migrations-runner.py /catherine/migrations-runner.py
COPY /docker/start.sh /catherine/start.sh
COPY /docker/wait-for /catherine/wait-for

COPY --from=builder /catherine/requirements.txt /catherine/requirements.txt

RUN adduser --disabled-password --gecos "" catherine \
  && chown -R catherine:catherine /catherine \
  && chmod +x /catherine/start.sh \
  && chmod +x /catherine/wait-for

USER catherine

ENV PATH="${PATH}:${HOME}/.local/bin"

RUN pip install --user -r requirements.txt

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/catherine/start.sh"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="Catherine-Chan"
LABEL org.opencontainers.image.description="The all-in-one toolkit for LGBTQ+ folks"
LABEL org.opencontainers.image.licenses="GPL-3.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Catherine-Chan"
