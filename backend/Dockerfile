FROM python:3.9.18-bookworm
LABEL maintainer="aprian.immanuel@danasaham.co.id"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libpq-dev \
    cmake \
    curl \
    ffmpeg \
    g++ \
    gcc \
    git \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libboost-python-dev \
    libboost-thread-dev \
    libdc1394-dev \
    libeigen3-dev \
    libglew-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer1.0-dev \
    libgtk-3-dev \
    libjpeg-dev \
    liblapack-dev \
    libopenblas-dev \
    libopencv-dev \
    libpng-dev \
    libpostproc-dev \
    libsm6 \
    libswscale-dev \
    libtbb-dev \
    libtesseract-dev \
    libtiff-dev \
    libv4l-dev \
    libx11-dev \
    libxext6 \
    libxine2-dev \
    libxrender-dev \
    libxvidcore-dev \
    libx264-dev \
    python3-dev \
    python3-numpy \
    python3-pip \
    wget \
    unzip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* && \
    adduser --disabled-password --gecos '' django-user

RUN mkdir -p /app/media/test_media && \
    chown -R django-user:django-user /py && \
    chown -R django-user:django-user /app/media

ENV PATH="/py/bin:$PATH"

USER django-user