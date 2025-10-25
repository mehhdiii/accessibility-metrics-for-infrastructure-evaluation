FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    build-essential cmake git \
    libpcl-dev \
    libboost-all-dev \
    libgl1-mesa-glx \
    libx11-6 \
    python3 python3-pip \
    && pip3 install --no-cache-dir flask \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /data
