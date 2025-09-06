FROM python:3.12-alpine

WORKDIR /app
# Install system deps including certificates and timezone data
RUN apk add --no-cache build-base libpq-dev ca-certificates tzdata curl && \
    update-ca-certificates

COPY watchdog.py /app/

RUN pip install --no-cache-dir requests psycopg2-binary urllib3

CMD ["python", "watchdog.py"]
