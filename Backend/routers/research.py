"""
Research Router - AI-Powered Niche Research for Content Creators

Endpoints for analyzing niches, finding trending topics,
and generating validated content ideas.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List

from services.research_service import ResearchService
from models.ResearchModels import (
    ResearchRequest, ResearchResponse, ResearchReport,
    TrendingTopic, ContentIdea
)

router = APIRouter(prefix='/research', tags=['Research'])

# Initialize research service (LLM will be injected if needed)
research_service = None

try:
    # Try to import LLM service for enhanced analysis
    from services.llm_service import LLMService
    llm = LLMService()
    research_service = ResearchService(llm_service=llm)
except Exception as e:
    print(f"⚠ LLM not available for research: {e}")
    research_service = ResearchService()


@router.post("/analyze", response_model=ResearchResponse)
async def analyze_niche(request: ResearchRequest):
    """
    Analyze a niche and generate validated content ideas.
    
    Args:
        niche: Main topic to research (e.g., "personal finance")
        subreddits: Optional list of subreddits to monitor
        days: Days of data to analyze (default: 7)
        idea_count: Number of content ideas to generate (default: 20)
    
    Returns:
        Research report with trending topics, pain points, and content ideas
    """
    try:
        if not request.niche or request.niche.strip() == "":
            raise HTTPException(status_code=400, detail="Niche cannot be empty")
        
        # Run research pipeline
        report = research_service.research(
            niche=request.niche,
            subreddits=request.subreddits,
            days=request.days,
            idea_count=request.idea_count
        )
        
        return ResearchResponse(
            success=True,
            report=report,
            message=f"Generated {len(report.content_ideas)} content ideas for '{request.niche}'"
        )
        
    except Exception as e:
        print(f"❌ Research error: {e}")
        import traceback
        traceback.print_exc()
        
        return ResearchResponse(
            success=False,
            report=None,
            message=str(e)
        )


@router.get("/trending/{niche}")
async def get_trending(niche: str, limit: int = 20):
    """
    Get trending topics for a niche (quick lookup).
    
    Args:
        niche: Topic to get trends for
        limit: Max number of trending topics
    
    Returns:
        List of trending topics from Google Trends and Reddit
    """
    try:
        # Quick trends lookup
        trends = research_service.get_google_trends(niche, related_topics=limit)
        
        return {
            "success": True,
            "niche": niche,
            "trending": [
                TrendingTopic(
                    topic=t['topic'],
                    source=t.get('source', 'google_trends'),
                    score=t.get('score', 0),
                    context=t.get('type', '')
                )
                for t in trends[:limit]
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "niche": niche,
            "trending": [],
            "error": str(e)
        }


@router.get("/quick-ideas/{niche}")
async def quick_ideas(niche: str, count: int = 10):
    """
    Quick content idea generation (no deep scraping).
    
    Args:
        niche: Topic to generate ideas for
        count: Number of ideas to generate
    
    Returns:
        List of content ideas based on trends
    """
    try:
        trends = research_service.get_google_trends(niche)
        
        # Generate quick ideas from trends
        ideas = research_service.generate_ideas(
            niche=niche,
            analysis={'questions': [], 'pain_points': []},
            trends=trends,
            count=count
        )
        
        return {
            "success": True,
            "niche": niche,
            "ideas": ideas
        }
        
    except Exception as e:
        return {
            "success": False,
            "niche": niche,
            "ideas": [],
            "error": str(e)
        }
