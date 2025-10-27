# app.py

from fastapi import FastAPI
import psycopg2
import os
from datetime import datetime

app = FastAPI()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "userdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def init_db():
    """Initialize database table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/hello/{name}")
async def hello(name: str):
    """
    API endpoint that greets users and tracks them in PostgreSQL.
    Returns welcome message for existing users or adds new users.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username, created_at FROM users WHERE username = %s", (name,))
        user = cursor.fetchone()
        
        if user:
            # User exists - welcome back
            message = f"Welcome back, {name}!"
        else:
            # New user - add to database
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (name,))
            conn.commit()
            message = f"Hello, {name}. You've been added to the list!"
        
        cursor.close()
        conn.close()
        
        return {"message": message}
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

@app.get("/users")
async def list_users():
    """
    List all users in the database (bonus endpoint for testing)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, created_at FROM users ORDER BY created_at")
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {"users": [{"username": user[0], "created_at": user[1]} for user in users]}
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


