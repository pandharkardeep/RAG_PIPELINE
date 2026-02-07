from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


class ResearchRequest(BaseModel):
    """Request for niche research analysis"""
    niche: str  # Main topic/niche to research
    subreddits: Optional[List[str]] = None  # Subreddits to monitor
    days: int = 7  # Days of data to analyze
    idea_count: int = 20  # Number of content ideas to generate


class TrendingTopic(BaseModel):
    """A trending topic or question"""
    topic: str
    source: str  # reddit, google_trends, etc.
    score: float  # Engagement/relevance score
    context: Optional[str] = None


class ContentIdea(BaseModel):
    """A validated content idea"""
    title: str
    description: str
    pain_point: Optional[str] = None
    target_audience: Optional[str] = None
    content_type: str  # video, article, tweet thread, etc.
    confidence_score: float  # 0-1 how validated this idea is
    sources: List[str] = []  # Where we found evidence for this idea


class ResearchReport(BaseModel):
    """Complete research report"""
    niche: str
    trending_topics: List[TrendingTopic]
    content_ideas: List[ContentIdea]
    pain_points: List[str]
    questions: List[str]  # Questions people are asking
    stats: Dict[str, Any]  # Pipeline statistics


class ResearchResponse(BaseModel):
    """API response for research endpoint"""
    success: bool
    report: Optional[ResearchReport] = None
    message: str
