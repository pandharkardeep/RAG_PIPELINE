# import requests

# url = "https://real-time-news-data.p.rapidapi.com/search"

# querystring = {"query":"Football","limit":"10","time_published":"anytime","country":"US","lang":"en"}

# headers = {
# 	"x-rapidapi-key": "74b10f24c9msh9fd947632f86905p187aebjsne3e91483531a",
# 	"x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# print(response.json())

from fastapi import FastAPI, exceptions
from fastapi.middleware.cors import CORSMiddleware
from routers import news_ingestion

if __name__ == "__main__":
    app = FastAPI()
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],  # Angular dev server
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
        allow_headers=["*"],  # Allows all headers
    )
    
    app.include_router(news_ingestion.router)
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)