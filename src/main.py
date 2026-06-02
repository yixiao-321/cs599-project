from app.data.init_data import init_sample_data
from app.main import app
import uvicorn
from app.config import config

def main():
    init_sample_data()
    
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

if __name__ == "__main__":
    main()