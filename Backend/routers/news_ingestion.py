from fastapi import FastAPI
from fastapi import APIRouter
from pydantic import BaseModel
import requests
router = APIRouter()


@router.get("/news_ingestion")
def news_ingestion(query: str, limit: int):
    url = "https://real-time-news-data.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "limit": limit,
        "country": "US",
        "lang": "en"
    }

    headers = {
        "x-rapidapi-key": "74b10f24c9msh9fd947632f86905p187aebjsne3e91483531a",
        "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

