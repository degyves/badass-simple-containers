# app.py

from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/{name}")
async def hello(name: str):
    """
    A simple API endpoint that returns a greeting.
    """
    return {"message": f"Hello, {name}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


