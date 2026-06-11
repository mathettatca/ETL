FROM apache/airflow:3.2.1-python3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

WORKDIR /opt/airflow

COPY pyproject.toml uv.lock* ./

# Dùng pip của airflow user, cài uv trước
RUN pip install --no-cache-dir uv \
    && uv export --frozen --no-dev --no-emit-project \
       --format requirements.txt \
       --output-file /tmp/requirements.txt \
    && uv pip install --no-cache -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY dags ./dags
COPY src ./src