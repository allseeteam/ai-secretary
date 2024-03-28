FROM python:3.8-slim-buster

WORKDIR /ai-secretary

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    git \
    cmake \
    gperf \
    g++ \
    supervisor && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --recursive https://github.com/tdlib/telegram-bot-api.git && \
    cd telegram-bot-api && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --target install

RUN pip install --no-cache-dir -r requirements.txt

ARG TELEGRAM_API_ID
ARG TELEGRAM_API_HASH
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

ENV TELEGRAM_API_ID=${TELEGRAM_API_ID}
ENV TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=${NO_PROXY}

CMD ["/usr/bin/supervisord", "-c", "./supervisord.conf"]
