from fastapi import FastAPI, HTTPException, Query
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import requests
from config import PINECONE_KEY
from GoogleNews import GoogleNews
from summarization.summarize_news import summarization
import pandas as pd
import sys
import io, re
from contextlib import redirect_stderr
from datetime import datetime
from services.news_article_retrieval import news_article_retrieval
from services.chunk import chunk
from services.emb_service import emb_service
from services.pinecone_service import PineconeService

router = APIRouter(prefix='/articles')

# Cache to store last fetched articles (avoids re-fetching for export)
article_cache = {
    "query": None,
    "data": None,
    "source": None,
    "timestamp": None
}

# Known media sources - grows as new sources are discovered from fetched articles
known_sources = set([
    'BBC', 'CNN', 'Reuters', 'Al Jazeera', 'The Guardian', 'Fox News',
    'The New York Times', 'The Washington Post', 'Associated Press',
    'Bloomberg', 'CNBC', 'The Wall Street Journal', 'NPR', 'ABC News',
    'NBC News', 'CBS News', 'Sky News', 'The Independent', 'The Telegraph',
    'Financial Times', 'TechCrunch', 'The Verge', 'Wired', 'Ars Technica',
    'The Hindu', 'Times of India', 'NDTV', 'India Today', 'Hindustan Times',
])

# Initialize services globally to avoid recreating them on each request
try:
    embedder = emb_service()
    pinecone_service = PineconeService(
        index_name="news-articles",
        dimension=embedder.get_dimension()
    )
    # Check if index exists before creation to avoid errors on subsequent restarts
    if "news-articles" not in [index.name for index in pinecone_service.pc.list_indexes()]:
        pinecone_service.create_index(metric="cosine", cloud="aws", region="us-east-1")
except Exception as e:
    print(f"⚠ Warning: Could not initialize")

@router.get("")
def news_ingestion(
    query: str,
    limit: int = 10,
    include_sources: Optional[List[str]] = Query(default=None, description="Only include articles from these media houses (e.g. BBC, CNN)"),
    exclude_sources: Optional[List[str]] = Query(default=None, description="Exclude articles from these media houses (e.g. Fox News)")
):
    """
    Fetch news articles, chunk them, generate embeddings, and store in Pinecone
    """
    global article_cache
    
    nar = news_article_retrieval(query, limit, include_sources=include_sources, exclude_sources=exclude_sources)
    result = nar.get_ingestion()
    
    # Cache the result for export
    if result.get('success', False):
        article_cache = {
            "query": query,
            "data": result.get('data', []),
            "source": result.get('source', 'Unknown'),
            "timestamp": datetime.now()
        }
        print(f"✓ Cached {len(article_cache['data'])} articles for query: {query}")
        
        # Auto-discover new media sources from fetched articles
        for article in result.get('data', []):
            media = article.get('media', '')
            if media and media not in known_sources and not media.startswith('http'):
                known_sources.add(media)
                print(f"✓ Discovered new source: {media}")
    
    return result

@router.get("/sources")
def get_sources():
    """
    Get list of known media sources for filtering
    """
    return {
        "sources": sorted(list(known_sources))
    }

@router.post("/ingest")
def news_addition(
    query: str,
    limit: int = 10,
    include_sources: Optional[List[str]] = Query(default=None, description="Only include articles from these media houses"),
    exclude_sources: Optional[List[str]] = Query(default=None, description="Exclude articles from these media houses")
):
    nar = news_article_retrieval(query, limit, include_sources=include_sources, exclude_sources=exclude_sources)
    nar.retrieve()
    df = nar.get_data()
    ch = chunk()
    chunks_data = ch.textsplit()
    
    # Step 3 & 4: Generate embeddings and store Fin Pinecone
    if embedder and pinecone_service and chunks_data:
        try:
            texts = [chunk_data['text'] for chunk_data in chunks_data]
            
            # Generate embeddings in batches
            batch_size = 32
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = embedder.generate_embeddings(batch_texts)
                all_embeddings.extend(batch_embeddings)
            
            vectors = []
            
            for idx, (chunk_data, embedding) in enumerate(zip(chunks_data, all_embeddings)):
                vector_id = f"news_{query}_{chunk_data['doc_id']}_{chunk_data['chunk_id']}"
                metadata = {
                    'text': chunk_data['text'][:1000],  # Limit text size for metadata
                    'filename': chunk_data['filename'],
                    'chunk_id': chunk_data['chunk_id'],
                    'doc_id': chunk_data['doc_id'],
                    'query': query
                }
                vectors.append((vector_id, embedding.tolist(), metadata))
            
            # Upload to Pinecone
            pinecone_service.upsert_vectors(vectors)
            
            # Get index stats
            stats = pinecone_service.get_stats()
            print(f"\n[5/5] Complete! Index now contains {stats.get('total_vector_count', 'N/A')} vectors")
            
        except Exception as e:
            print(f"⚠ Warning: Failed to process embeddings/Pinecone: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠ Skipping embedding/Pinecone storage (services not initialized or no chunks)")
    
@router.get("/search")
def search_articles(query: str, top_k: int = 5):
    """
    Search for similar articles in Pinecone based on query
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return (default: 5)
    
    Returns:
        dict: Search results with scores and metadata
    """
    if not embedder or not pinecone_service:
        return {
            "success": False,
            "error": "Search service not available. Pinecone not initialized.",
            "results": []
        }
    
    try:
        print(f"\n{'='*60}")
        print(f"Searching for: '{query}' (top_k: {top_k})")
        print(f"{'='*60}\n")
        
        # Generate embedding for the query
        print("[1/2] Generating query embedding...")
        query_embedding = embedder.generate_embeddings(query)
        print(f"✓ Query embedding generated")
        
        # Search Pinecone
        print("\n[2/2] Searching Pinecone...")
        results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        formatted_results = []
        for i, match in enumerate(results.get('matches', []), 1):
            formatted_results.append({
                'rank': i,
                'score': match['score'],
                'text': match['metadata'].get('text', ''),
                'filename': match['metadata'].get('filename', ''),
                'chunk_id': match['metadata'].get('chunk_id', 0),
                'source_query': match['metadata'].get('query', '')
            })
            print(f"{i}. Score: {match['score']:.4f} | File: {match['metadata'].get('filename', 'N/A')}")
        
        print(f"\n✓ Found {len(formatted_results)} results")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


@router.get("/export/csv")
def export_articles_csv():
    """
    Export cached articles as a downloadable CSV file.
    Must call /articles endpoint first to fetch and cache articles.
    
    Returns:
        StreamingResponse: CSV file download
    """
    global article_cache
    
    # Check if we have cached data
    if article_cache["data"] is None or len(article_cache["data"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="No articles cached. Please fetch articles first using /articles endpoint."
        )
    
    try:
        articles = article_cache["data"]
        query = article_cache["query"] or "unknown"
        source = article_cache["source"] or "Unknown"
        
        # Create DataFrame with relevant fields
        export_data = []
        for idx, article in enumerate(articles, 1):
            export_data.append({
                'No': idx,
                'Title': article.get('title', ''),
                'Link': article.get('link', ''),
                'Description': article.get('desc', ''),
                'Query': query,
                'Source': source,
                'Exported_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(export_data)
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"articles_{query.replace(' ', '_')}_{timestamp}.csv"
        
        print(f"✓ Exported {len(articles)} cached articles to CSV: {filename}")
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ CSV export failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
