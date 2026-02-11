import uvicorn
from app.api.views import app

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)