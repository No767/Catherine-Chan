####################################################################################################
## Final image
####################################################################################################
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  tini \
  bash \
  netcat-traditional \
  git \
  && apt-get clean

WORKDIR /catherine
COPY /bot/ /catherine/bot
COPY /requirements.txt /catherine/requirements.txt
COPY /docker/start.sh /catherine/start.sh
COPY /docker/wait-for /catherine/wait-for

RUN adduser --disabled-password --gecos "" catherine \
  && chown -R catherine:catherine /catherine \
  && chmod +x /catherine/start.sh \
  && chmod +x /catherine/wait-for

USER catherine

ENV PATH="${PATH}:/home/catherine/.local/bin"

RUN pip install --user -r requirements.txt

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/catherine/start.sh"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="Catherine-Chan"
LABEL org.opencontainers.image.description="The all-in-one toolkit for LGBTQ+ folks"
LABEL org.opencontainers.image.licenses="GPL-3.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Catherine-Chan"
