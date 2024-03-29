import uvicorn
from api.endpoints import app


if __name__ == "__main__":
    # Start the FastAPI service
    uvicorn.run(app, host="0.0.0.0", port=8000)