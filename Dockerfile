FROM ubuntu:noble

ARG DESCRIPTION
ARG SYNCSERVER_BIN
ARG DEPENDENCIES
ARG DBTYPE=mysql
ENV DBTYPE=$DBTYPE

LABEL maintainer="syncstorage-rs@fritz-elfert.de"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends $DEPENDENCIES && rm -rf /var/lib/apt/lists/*

ENV RUST_LOG=info
ENV SYNC_TOKENSERVER__RUN_MIGRATIONS=true
ENV PUBLIC_URL=https://publicurl.tld
ENV MAX_CLIENTS=1

ENV SYNC_CONFIG=

WORKDIR /app
COPY --chmod=755 $SYNCSERVER_BIN entrypoint.sh .

ENTRYPOINT ["/app/entrypoint.sh"]
