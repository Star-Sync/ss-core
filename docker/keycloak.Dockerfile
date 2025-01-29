FROM python:3.10-slim

WORKDIR /app

# Install required packages with specific versions
RUN pip install --no-cache-dir \
    requests==2.31.0 \
    python-keycloak==3.7.0

# Copy your initialization script
COPY docker/scripts/init_keycloak_users.py .

CMD ["python", "init_keycloak_users.py"]
