from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from models.ThreadModels import (
    IngestRequest, IngestResponse, SearchResult, Insight, InsightConnection
)
from services.KnowledgeBaseService import KnowledgeBaseService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

_kb_service = None


def get_kb_service() -> KnowledgeBaseService:
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service


@router.post("/ingest", response_model=IngestResponse)
async def ingest_insight(request: IngestRequest):
    """
    Ingest a new thread/insight into the knowledge base.
    
    - Automatically extracts topics from content
    - Generates semantic embeddings for search
    - Stores in local ChromaDB for persistent retrieval
    """
    try:
        service = get_kb_service()
        response = service.ingest_insight(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest insight: {str(e)}")


@router.get("/search", response_model=List[SearchResult])
async def search_knowledge(
    query: str = Query(..., description="Search query text"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results to return"),
    source_type: Optional[str] = Query(None, description="Filter by source type: thread, article, note, analysis"),
    topic: Optional[str] = Query(None, description="Filter by topic")
):
    """
    Semantic search across all insights with connection discovery.
    
    Returns insights ranked by relevance, along with:
    - Related insights (connections)
    - Suggested topics for further exploration
    """
    try:
        service = get_kb_service()
        
        filters = {}
        if source_type:
            filters["source_type"] = source_type
        if topic:
            filters["topic"] = topic
        
        results = service.search(query, top_k, filters if filters else None)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/connections/{insight_id}", response_model=List[InsightConnection])
async def get_connections(
    insight_id: str,
    top_k: int = Query(5, ge=1, le=20, description="Number of connections to find")
):
    """
    Find related insights based on semantic similarity.
    
    Discovers connections between insights that share:
    - Similar content (semantic)
    - Common topics
    - Shared citations
    """
    try:
        service = get_kb_service()
        connections = service.find_connections(insight_id, top_k)
        return connections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find connections: {str(e)}")


@router.get("/insights/{insight_id}", response_model=Insight)
async def get_insight(insight_id: str):
    """
    Get a specific insight by ID.
    """
    service = get_kb_service()
    insight = service.get_insight(insight_id)
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return insight


@router.get("/topics", response_model=List[str])
async def get_all_topics():
    """
    Get all unique topics across the knowledge base.
    
    Useful for building filter dropdowns and topic clouds.
    """
    try:
        service = get_kb_service()
        topics = service.get_all_topics()
        return topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")


@router.get("/topics/suggest")
async def suggest_topics(
    content: str = Query(..., description="Content to extract topics from"),
    top_n: int = Query(5, ge=1, le=10, description="Number of topics to extract")
):
    """
    Extract and suggest topics for given content.
    
    Useful for:
    - Auto-tagging new insights before ingestion
    - Discovering themes in draft content
    """
    try:
        service = get_kb_service()
        topics = service._extract_topics(content, top_n)
        return {"topics": topics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic extraction failed: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    Get statistics about the knowledge base.
    
    Returns:
    - Total number of insights
    - Breakdown by source type
    - Top topics by frequency
    """
    try:
        service = get_kb_service()
        stats = service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/insights/{insight_id}")
async def delete_insight(insight_id: str):
    """
    Delete an insight from the knowledge base.
    """
    service = get_kb_service()
    success = service.delete_insight(insight_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Insight not found or could not be deleted")
    
    return {"message": "Insight deleted successfully", "id": insight_id}
