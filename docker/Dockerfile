# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

COPY ../requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ../flaskr /app

EXPOSE 5000

ENV FLASK_APP=hello.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
