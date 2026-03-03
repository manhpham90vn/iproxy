FROM python:3.12-slim

ARG UID=1000
ARG GID=1000

RUN groupadd -g ${GID} iproxy 2>/dev/null || true && \
    useradd -u ${UID} -g ${GID} -s /bin/bash -m iproxy 2>/dev/null || true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    gosu \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
