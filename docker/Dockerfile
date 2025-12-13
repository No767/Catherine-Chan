FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS build

# Compile bytecode and enable caching
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_COMPILE_BYTECODE=1 
ENV UV_LINK_MODE=copy

# Disable Python downloads as the system Python interpreter instead
ENV UV_PYTHON_DOWNLOADS=0

# Set Tini version
# Ref: https://github.com/krallin/tini?tab=readme-ov-file#using-tini
ENV TINI_VERSION=v0.19.0

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && apt-get clean

WORKDIR /app/

COPY requirements.txt /app/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    uv venv && uv pip install -r requirements.txt
    
# Add project source code
COPY ./src /app

FROM python:3.14-slim-trixie

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/catherine

# Set up non-root user
RUN groupadd --system --gid 999 catherine \
 && useradd --system --gid 999 --uid 999 --no-create-home catherine

# Copy the server from the builder
COPY --from=build /app /catherine
COPY --from=build --chmod=+x /tini /tini

# Place executables in the environment at the front of the path
ENV PATH="/catherine/.venv/bin:$PATH"

# Use non-root user
USER catherine

EXPOSE 6789

# Setup tini
ENTRYPOINT ["/tini", "--"]

CMD ["python3", "/catherine/main.py"]

STOPSIGNAL SIGTERM

LABEL org.opencontainers.image.title="Catherine-Chan"
LABEL org.opencontainers.image.description="The all-in-one toolkit for LGBTQ+ folks"
LABEL org.opencontainers.image.licenses="GPL-3.0"
LABEL org.opencontainers.image.source="https://github.com/No767/Catherine-Chan"