# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy local files to container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir requests

# Command to run the script
CMD ["python", "comments.py"]
