FROM python:3.12.4-bookworm
LABEL maintainer="aprian.immanuel@danasaham.co.id"

ENV PYTHONUNBUFFERED=1 \
    VENV_PATH=/py

# Set up working directory and expose port
WORKDIR /apps
EXPOSE 8000

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Install system dependencies and Python packages
ARG DEV=false
ARG DJANGO_USER
ARG DJANGO_UID
ARG DJANGO_GID

RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        python3-venv \
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
        python3-setuptools \
        python3-numpy \
        python3-pip \
        python3-sklearn \
        python3-sklearn-lib \
        python3-joblib \
        python3-matplotlib \
        python3-threadpoolctl \
        python3-mdp \
        python3-openpyxl \
        wget \
        unzip && \
    python3 -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --upgrade pip && \
    $VENV_PATH/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        $VENV_PATH/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/* /usr/share/man/* /usr/share/locale/* /usr/share/info/* && \
    find /usr/lib -type f -name '*.a' -delete && \
    find /usr/include -type f -name '*.h' -delete && \
    groupadd -g $DJANGO_GID $DJANGO_USER && \
    useradd -m -u $DJANGO_UID -g $DJANGO_GID $DJANGO_USER

# Copy application files
COPY ./backend /apps

# Set permissions for application files
RUN mkdir -p /apps/app/media/test_media /apps/logs && \
    touch /apps/logs/debug.log && \
    chmod 666 /apps/logs/debug.log && \
    chown -R $DJANGO_USER:$DJANGO_USER $VENV_PATH /apps /apps/logs /apps/app/media /apps/app/media/test_media

# Change ownership of migration directories
RUN chown -R $DJANGO_USER:$DJANGO_USER /apps/app/config/core/migrations

ENV PATH="$VENV_PATH/bin:$PATH"

USER $DJANGO_USER
