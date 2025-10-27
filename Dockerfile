# Use a base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your app code
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run the app
CMD ["python", "app.py"]
