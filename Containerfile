# Containerfile

# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create data directory in case it doesn't exist
RUN mkdir -p ./data

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to the container
COPY . .

# Ensure proper permissions
RUN chmod -R +rwX .

# Run the application
CMD ["python", "-u", "app.py"]
