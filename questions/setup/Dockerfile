FROM python:3.12-slim

# Add future libraries (e.g. pandas) to requirements.txt and rebuild
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code is mounted at /work by docker-compose, so nothing else to copy
WORKDIR /work
