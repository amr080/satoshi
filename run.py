from src.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 8080)))