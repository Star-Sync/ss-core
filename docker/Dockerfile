# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /opt/app

COPY requirements.txt /opt/app

RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app/ /opt/app

# Expose the port the app runs on
EXPOSE 8000

WORKDIR /opt

# Command to run the application with logging configuration
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "app/logging_config.yaml", "--workers", "1"]
