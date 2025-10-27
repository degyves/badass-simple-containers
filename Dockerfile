# Use a base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . /app

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]
