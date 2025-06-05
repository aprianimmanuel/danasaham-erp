FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv-installer

FROM python:3.12.10-slim-bookworm

ENV PYTHONUNBUFFERED=1

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    cmake \
    git \
    libpq-dev \
    curl \
    unzip \
    tzdata \
    pkg-config \
    libxml2-dev \
    libxmlsec1-dev \
    postgresql-client \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    python3-scipy \
    python3-wheel \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
COPY --from=uv-installer /usr/local/bin/uv /bin/uv

# Set workdir
WORKDIR /apps

# Copy dependency config
COPY ./pyproject.toml ./uv.lock /apps/

# Create and activate virtualenv + sync dependencies
RUN uv venv -v && uv pip install --upgrade pip && uv sync --frozen

# Activate venv
ENV PATH="/apps/.venv/bin:/apps/.venv/lib:$PATH"

# Download spacy models
RUN uv run --with spacy spacy download xx_ent_wiki_sm && uv run --with spacy spacy validate

# Copy application code
COPY . .

# Permission settings
RUN adduser --disabled-password --gecos "" starpoin_aprianimmanuel

# Add Django user
USER starpoin_aprianimmanuel
