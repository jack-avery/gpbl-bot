# Pull base image
FROM alpine:latest

## install dependencies
RUN apk update && \
    apk add python3~3.11 && \
    apk add py3-pip

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --break-system-packages -r requirements.txt
