# Using a slim version for a smaller base image
FROM python:3.10.8-slim-bullseye

RUN apt-get clean && apt-get update && apt-get install -y \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

WORKDIR /code

# Copy just the requirements first
COPY ./requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Increase timeout to wait for the new installation
RUN pip install --no-cache-dir -r requirements.txt --timeout 200

# Copy the rest of the application
COPY . .

EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "6"]