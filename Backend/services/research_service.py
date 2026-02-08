"""
AI-Powered Research Service for Content Creators

Scrapes Reddit, Google Trends, and analyzes content to generate
validated content ideas for YouTubers, podcasters, and newsletter writers.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
# Reddit API
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("⚠ PRAW not available - Reddit scraping disabled")

# Google Trends
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠ pytrends not available - Google Trends disabled")

from models.ResearchModels import TrendingTopic, ContentIdea, ResearchReport


class ResearchService:
    """
    AI-powered research service that identifies trending topics
    and generates validated content ideas.
    """
    
    def __init__(self, llm_service=None):
        """
        Initialize research service.
        
        Args:
            llm_service: Optional LLM service for content analysis
        """
        self.llm_service = llm_service
        self.reddit = None
        self.pytrends = None
        
        # Initialize Reddit if credentials available
        if PRAW_AVAILABLE:
            self._init_reddit()
        
        # Initialize Google Trends
        if PYTRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
                print("✓ Google Trends initialized")
            except Exception as e:
                print(f"⚠ Google Trends init failed: {e}")
        
        print("ResearchService initialized")
    
    def _init_reddit(self):
        """Initialize Reddit API client"""
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        user_agent = os.environ.get('REDDIT_USER_AGENT', 'RAG_Pipeline/1.0')
        
        if client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                print("✓ Reddit API initialized")
            except Exception as e:
                print(f"⚠ Reddit init failed: {e}")
        else:
            print("⚠ Reddit credentials not found (set REDDIT_CLIENT_ID/SECRET)")
    
    def scrape_reddit(
        self, 
        query : str,
        subreddits: List[str], 
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape top posts and comments from subreddits.
        
        Args:
            subreddits: List of subreddit names (without r/)
            days: Number of days to look back
            limit: Max posts per subreddit
            
        Returns:
            List of post data with engagement metrics
        """
        posts = []
        
        if not self.reddit:
            print("⚠ Reddit not available, using mock data")
            return self._get_mock_reddit_data(subreddits)
        
        for sub_name in subreddits:
            try:
                results = self.reddit.subreddit(sub_name).search(
                    query=query, 
                    sort="top", 
                    time_filter="week", 
                    limit=limit)
                
                # Get top posts from the past week
                for post in results:
                    post_data = {
                        'title': post.title,
                        'selftext': post.selftext[:500] if post.selftext else '',
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'subreddit': sub_name,
                        'url': post.url,
                        'created_utc': post.created_utc,
                        'upvote_ratio': post.upvote_ratio,
                        'is_question': '?' in post.title,
                        'source': 'reddit'
                    }
                    posts.append(post_data)
                    
                    # Get top comments for insight into discussions
                    post.comments.replace_more(limit=0)
                    for comment in post.comments[:5]:
                        if hasattr(comment, 'body') and len(comment.body) > 50:
                            posts.append({
                                'title': f"Comment on: {post.title[:50]}",
                                'selftext': comment.body[:500],
                                'score': comment.score,
                                'subreddit': sub_name,
                                'is_question': '?' in comment.body,
                                'source': 'reddit_comment'
                            })
                
                print(f"✓ Scraped r/{sub_name}: {len([p for p in posts if p.get('subreddit') == sub_name])} items")
                
            except Exception as e:
                print(f"⚠ Error scraping r/{sub_name}: {e}")
        
        return posts
    
    def _get_mock_reddit_data(self, subreddits: List[str]) -> List[Dict[str, Any]]:
        """Return mock data when Reddit API is not available"""
        mock_posts = []
        for sub in subreddits:
            mock_posts.extend([
                {
                    'title': f'What is the best way to start with {sub}?',
                    'selftext': 'Looking for beginner advice...',
                    'score': 150,
                    'num_comments': 45,
                    'subreddit': sub,
                    'is_question': True,
                    'source': 'reddit_mock'
                },
                {
                    'title': f'Common mistakes in {sub} - lessons learned',
                    'selftext': 'After 5 years of experience...',
                    'score': 320,
                    'num_comments': 89,
                    'subreddit': sub,
                    'is_question': False,
                    'source': 'reddit_mock'
                },
                {
                    'title': f'Why is nobody talking about this {sub} strategy?',
                    'selftext': 'I discovered something interesting...',
                    'score': 245,
                    'num_comments': 67,
                    'subreddit': sub,
                    'is_question': True,
                    'source': 'reddit_mock'
                }
            ])
        return mock_posts
    
    def get_google_trends(self, niche: str, related_topics: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending searches and related queries from Google Trends.
        
        Args:
            niche: Main topic to research
            related_topics: Number of related topics to return
            
        Returns:
            List of trending topics with interest scores
        """
        trends = []
        
        if not self.pytrends:
            print("⚠ Google Trends not available, using mock data")
            return self._get_mock_trends_data(niche)
        
        try:
            # Build payload for the niche
            self.pytrends.build_payload([niche], timeframe='now 7-d')
            
            # Get related queries
            related = self.pytrends.related_queries()
            
            if niche in related and related[niche]['rising'] is not None:
                rising = related[niche]['rising']
                for _, row in rising.head(related_topics).iterrows():
                    trends.append({
                        'topic': row['query'],
                        'score': float(row['value']),
                        'type': 'rising',
                        'source': 'google_trends'
                    })
            
            if niche in related and related[niche]['top'] is not None:
                top = related[niche]['top']
                for _, row in top.head(related_topics).iterrows():
                    trends.append({
                        'topic': row['query'],
                        'score': float(row['value']),
                        'type': 'top',
                        'source': 'google_trends'
                    })
            
            print(f"✓ Google Trends: found {len(trends)} related queries")
            
        except Exception as e:
            print(f"⚠ Google Trends error: {e}")
            return self._get_mock_trends_data(niche)
        
        return trends
    
    def _get_mock_trends_data(self, niche: str) -> List[Dict[str, Any]]:
        """Return mock trends data"""
        return [
            {'topic': f'{niche} for beginners', 'score': 100, 'type': 'rising', 'source': 'trends_mock'},
            {'topic': f'{niche} tips 2024', 'score': 85, 'type': 'rising', 'source': 'trends_mock'},
            {'topic': f'how to {niche}', 'score': 95, 'type': 'top', 'source': 'trends_mock'},
            {'topic': f'{niche} mistakes to avoid', 'score': 78, 'type': 'top', 'source': 'trends_mock'},
        ]
    
    def analyze_content(self, posts: List[Dict[str, Any]], niche: str) -> Dict[str, Any]:
        """
        Use LLM to analyze posts and extract pain points, questions, patterns.
        
        Args:
            posts: List of scraped posts
            niche: The niche being researched
            
        Returns:
            Analysis results with pain points, questions, patterns
        """
        # Extract questions from posts
        questions = []
        pain_points = []
        
        for post in posts:
            title = post.get('title', '')
            text = post.get('selftext', '')
            
            # Simple pattern matching for questions
            if post.get('is_question') or '?' in title:
                questions.append(title)
            
            # Look for pain point indicators
            pain_indicators = ['struggle', 'problem', 'issue', 'help', 'confused', 
                             'frustrated', 'hard', 'difficult', 'stuck', 'fail']
            combined_text = (title + ' ' + text).lower()
            for indicator in pain_indicators:
                if indicator in combined_text:
                    pain_points.append(title)
                    break
        
        # If LLM is available, do deeper analysis
        if self.llm_service:
            try:
                llm_analysis = self._llm_analyze(posts, niche)
                questions.extend(llm_analysis.get('questions', []))
                pain_points.extend(llm_analysis.get('pain_points', []))
            except Exception as e:
                print(f"⚠ LLM analysis failed: {e}")
        
        # Deduplicate
        questions = list(set(questions))[:20]
        pain_points = list(set(pain_points))[:15]
        
        return {
            'questions': questions,
            'pain_points': pain_points,
            'post_count': len(posts),
            'avg_engagement': sum(p.get('score', 0) for p in posts) / max(len(posts), 1)
        }
    
    def _llm_analyze(self, posts: List[Dict[str, Any]], niche: str) -> Dict[str, Any]:
        """Use LLM for deeper content analysis"""
        # Prepare sample posts for LLM
        sample_posts = posts[:15]  # Limit to avoid token overflow
        posts_text = "\n".join([
            f"- {p.get('title', '')} (score: {p.get('score', 0)})"
            for p in sample_posts
        ])
        
        prompt = f"""Analyze these {niche} community posts and extract:
1. Top 5 recurring pain points
2. Top 5 questions people are asking
3. Top 3 content gaps (topics not covered well)

Posts:
{posts_text}

Respond in JSON format:
{{"pain_points": [...], "questions": [...], "content_gaps": [...]}}"""

        try:
            if hasattr(self.llm_service, 'model') and self.llm_service.model:
                self.llm_service._load_model()
                response = self.llm_service.model.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    temperature=0.3
                )
                content = response["choices"][0]["message"]["content"]
                
                # Extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            print(f"⚠ LLM analysis error: {e}")
        
        return {'questions': [], 'pain_points': [], 'content_gaps': []}
    
    def generate_ideas(
        self,
        niche: str,
        analysis: Dict[str, Any],
        trends: List[Dict[str, Any]],
        count: int = 20
    ) -> List[ContentIdea]:
        """
        Generate validated content ideas based on research.
        
        Args:
            niche: The niche being researched
            analysis: Results from analyze_content
            trends: Google Trends data
            count: Number of ideas to generate
            
        Returns:
            List of ContentIdea objects
        """
        ideas = []
        
        # Generate ideas from questions
        for q in analysis.get('questions', [])[:count//3]:
            ideas.append(ContentIdea(
                title=f"Answering: {q}",
                description=f"Create content addressing this common question from the {niche} community",
                pain_point=q,
                content_type="video,article",
                confidence_score=0.85,
                sources=["reddit"]
            ))
        
        # Generate ideas from pain points
        for pp in analysis.get('pain_points', [])[:count//3]:
            ideas.append(ContentIdea(
                title=f"Solving: {pp[:60]}...",
                description=f"Help your audience overcome this common struggle",
                pain_point=pp,
                content_type="tutorial,guide",
                confidence_score=0.80,
                sources=["reddit"]
            ))
        
        # Generate ideas from trends
        for trend in trends[:count//3]:
            ideas.append(ContentIdea(
                title=f"{trend['topic'].title()} - Complete Guide",
                description=f"Capitalize on rising search interest in {trend['topic']}",
                target_audience=f"People searching for {trend['topic']}",
                content_type="video,blog",
                confidence_score=min(trend.get('score', 50) / 100, 0.95),
                sources=["google_trends"]
            ))
        
        # If LLM available, generate more creative ideas
        if self.llm_service and len(ideas) < count:
            try:
                llm_ideas = self._llm_generate_ideas(niche, analysis, count - len(ideas))
                ideas.extend(llm_ideas)
            except Exception as e:
                print(f"⚠ LLM idea generation failed: {e}")
        
        return ideas[:count]
    
    def _llm_generate_ideas(self, niche: str, analysis: Dict[str, Any], count: int) -> List[ContentIdea]:
        """Use LLM to generate creative content ideas"""
        questions = analysis.get('questions', [])[:5]
        pain_points = analysis.get('pain_points', [])[:5]
        
        prompt = f"""You are a content strategist. Generate {count} unique content ideas for a {niche} creator.

Based on these audience pain points:
{json.dumps(pain_points, indent=2)}

And these questions they're asking:
{json.dumps(questions, indent=2)}

For each idea provide:
- title: Catchy title
- description: Brief description
- content_type: video/article/thread/podcast

Respond with JSON array of ideas."""

        ideas = []
        try:
            if hasattr(self.llm_service, 'model') and self.llm_service.model:
                self.llm_service._load_model()
                response = self.llm_service.model.create_chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500,
                    temperature=0.7
                )
                content = response["choices"][0]["message"]["content"]
                
                # Extract JSON array
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    raw_ideas = json.loads(json_match.group())
                    for idea in raw_ideas:
                        ideas.append(ContentIdea(
                            title=idea.get('title', 'Untitled'),
                            description=idea.get('description', ''),
                            content_type=idea.get('content_type', 'video'),
                            confidence_score=0.70,
                            sources=["llm_generated"]
                        ))
        except Exception as e:
            print(f"⚠ LLM idea generation error: {e}")
        
        return ideas
    
    def research(
        self,
        niche: str,
        subreddits: Optional[List[str]] = None,
        days: int = 7,
        idea_count: int = 20
    ) -> ResearchReport:
        """
        Run complete research pipeline.
        
        Args:
            niche: Topic/niche to research
            subreddits: Subreddits to scrape (auto-generated if not provided)
            days: Days of data to analyze
            idea_count: Number of content ideas to generate
            
        Returns:
            Complete ResearchReport
        """
        stats = {
            'reddit_posts': 0,
            'trends_found': 0,
            'questions_extracted': 0,
            'pain_points_found': 0
        }
        
        # Auto-generate subreddit names if not provided
        if not subreddits:
            subreddits = ["all"]
        
        # Step 1: Scrape Reddit
        print(f"📊 Researching: {niche}")
        posts = self.scrape_reddit(niche, subreddits, days)
        stats['reddit_posts'] = len(posts)
        
        # Step 2: Get Google Trends
        trends_data = self.get_google_trends(niche)
        stats['trends_found'] = len(trends_data)
        
        # Step 3: Analyze content
        analysis = self.analyze_content(posts, niche)
        stats['questions_extracted'] = len(analysis.get('questions', []))
        stats['pain_points_found'] = len(analysis.get('pain_points', []))
        
        # Step 4: Generate ideas
        ideas = self.generate_ideas(niche, analysis, trends_data, idea_count)
        
        # Build trending topics list
        trending_topics = [
            TrendingTopic(
                topic=t['topic'],
                source=t.get('source', 'google_trends'),
                score=t.get('score', 0),
                context=t.get('type', '')
            )
            for t in trends_data
        ]
        
        # Add high-engagement Reddit topics
        top_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:10]
        for post in top_posts:
            trending_topics.append(TrendingTopic(
                topic=post.get('title', '')[:100],
                source='reddit',
                score=float(post.get('score', 0)),
                context=f"r/{post.get('subreddit', 'unknown')}"
            ))
        
        print(f"✓ Research complete: {len(ideas)} ideas generated")
        
        return ResearchReport(
            niche=niche,
            trending_topics=trending_topics[:20],
            content_ideas=ideas,
            pain_points=analysis.get('pain_points', []),
            questions=analysis.get('questions', []),
            stats=stats
        )
