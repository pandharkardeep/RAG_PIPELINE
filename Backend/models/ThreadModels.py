from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class Citation(BaseModel):
    """Reference to an external source cited in an insight"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_url: Optional[str] = None
    source_title: str
    source_type: str = "article"  # "research", "regulation", "article", "tweet"
    excerpt: Optional[str] = None  # Relevant quoted text
    insight_id: Optional[str] = None  # Parent insight reference


class InsightConnection(BaseModel):
    """Represents a connection between two related insights"""
    connected_insight_id: str
    connected_insight_title: str
    similarity_score: float
    shared_topics: List[str] = []
    connection_type: str = "semantic"  # "semantic", "citation", "topic"


class Insight(BaseModel):
    """A piece of knowledge - thread, article, note, or analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    source_type: str = "thread"  # "thread", "article", "note", "analysis"
    topics: List[str] = []  # Auto-extracted topics
    citations: List[Citation] = []  # Referenced sources
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}  # Flexible metadata (author, platform, etc.)


class SearchResult(BaseModel):
    """Search result with related insights and suggestions"""
    insight: Insight
    similarity_score: float
    related_insights: List[InsightConnection] = []
    suggested_topics: List[str] = []


class IngestRequest(BaseModel):
    """Request model for ingesting new insights"""
    title: str
    content: str
    source_type: str = "thread"
    topics: List[str] = []  # Optional manual topics
    citations: List[Citation] = []
    metadata: Dict[str, Any] = {}


class IngestResponse(BaseModel):
    """Response after ingesting an insight"""
    id: str
    message: str
    extracted_topics: List[str]
    citation_count: int


class SearchRequest(BaseModel):
    """Request model for searching the knowledge base"""
    query: str
    top_k: int = 10
    source_type: Optional[str] = None
    topic: Optional[str] = None