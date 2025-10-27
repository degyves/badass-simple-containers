	# Badass simple containers demo with PostgreSQL and React

A FastAPI application that greets users and stores them in a PostgreSQL database, with a React frontend.

## Features
- React frontend with name input and user table
- Greets new users and adds them to the database
- Welcomes back existing users
- Simple PostgreSQL integration with user tracking
- Containerized with Podman and podman-compose

## Quick Start

### Prerequisites
- Podman installed
- podman-compose installed (`pip install podman-compose`)

### Using Podman Compose (Recommended)

1. **Install podman and podman-compose:**
   ```bash
   # Install podman (if not already installed)
   brew install podman
   
   # Install podman-compose
   pip install podman-compose
   ```

2. **Create and start a podman machine:**
   ```bash
   podman machine init --cpus 8 --memory 8192 --user-mode-networking --rootful
   podman machine start
   ```

3. **Start the application:**
   ```bash
   podman-compose up --build
   ```

4. **Open the frontend:**
   - Navigate to http://localhost:3000 in your browser
   - Enter a name and click Submit
   - See the greeting message and user table

5. **Test the API directly (optional):**
   ```bash
   # First time user
   curl http://localhost:8000/hello/victor
   # Response: {"message": "Hello, victor. You've been added to the list!"}
   
   # Returning user
   curl http://localhost:8000/hello/victor
   # Response: {"message": "Welcome back, victor!"}
   
   # List all users
   curl http://localhost:8000/users
   ```

6. **Stop the application:**
   ```bash
   podman-compose down
   ```

### Using Podman Directly (Alternative)

1. **Create and start a podman machine:**
   ```bash
   podman machine init --cpus 8 --memory 8192 --user-mode-networking --rootful
   podman machine start
   ```

2. **Start PostgreSQL:**
   ```bash
   podman run -d --name postgres \
     -e POSTGRES_DB=userdb \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=password \
     -p 5432:5432 \
     postgres:14.19-alpine3.21
   ```

3. **Build and run the app:**
   ```bash
   podman build -t my-python-app .
   podman run -d --name app \
     -e DB_HOST=host.containers.internal \
     -p 8000:8000 \
     my-python-app
   ```

4. **Build and run the frontend:**
   ```bash
   cd frontend
   podman build -t my-react-app .
   podman run -d --name frontend \
     -e REACT_APP_API_URL=http://localhost:8000 \
     -p 3000:3000 \
     my-react-app
   ```

### Using Docker Compose (If you prefer Docker)

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Stop the application:**
   ```bash
   docker-compose down
   ```

## Database Schema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
