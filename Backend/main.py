from fastapi import FastAPI, exceptions
from fastapi.middleware.cors import CORSMiddleware
from routers import articles, tweets, cleanup, charts, knowledge_base, research
from config import ALLOWED_ORIGINS, HOST, PORT
import uvicorn

app = FastAPI(
    title="RAG Pipeline API",
    description="Backend API for RAG-based tweet generation and news analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
app.include_router(articles.router)
app.include_router(tweets.router)
app.include_router(cleanup.router)
app.include_router(charts.router)
app.include_router(knowledge_base.router)
app.include_router(research.router)


@app.get("/")
def health_check():
    """Health check endpoint for HF Spaces"""
    return {"status": "healthy", "message": "RAG Pipeline API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
