FROM python:3.12.5-bookworm
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
        tzdata \
        ntpdate \
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
        python3-dev \
        python3-setuptools \
        python3-numpy \
        python3-scipy \
        python3-pip \
        python3-sklearn \
        python3-sklearn-lib \
        python3-joblib \
        python3-matplotlib \
        python3-threadpoolctl \
        python3-mdp \
        python3-openpyxl \
        python3-reportlab \
        python3-reportlab-accel \
        python3-renderpm \
        python3-venv \
        python3-wheel \
        python3-distutils \
        build-essential \
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

# Ensure the static folder exists and copy the logo
RUN mkdir -p /apps/app/config/dttotDocReport/static/ && \
    cp /apps/static/logo_danasaham_surat.jpg /apps/app/config/dttotDocReport/static/logo_danasaham_surat.jpg

# Set permissions for application files
RUN mkdir -p /apps/media/test_media /apps/logs && \
    touch /apps/logs/debug.log && \
    chmod 666 /apps/logs/debug.log && \
    chown -R $DJANGO_USER:$DJANGO_USER $VENV_PATH /apps /apps/logs /apps/media /apps/media/test_media /apps/app/config/dttotDocReport/static

# Download spacy models using the correct Python environment
RUN $VENV_PATH/bin/python -m spacy download xx_ent_wiki_sm

# Change ownership of migration directories
RUN chown -R $DJANGO_USER:$DJANGO_USER /apps/app/config/core/migrations

ENV PATH="$VENV_PATH/bin:$PATH"

USER $DJANGO_USER
