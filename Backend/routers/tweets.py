from fastapi import APIRouter, HTTPException
from services.llm_service import LLMService
from services.emb_service import emb_service
from services.pinecone_service import PineconeService
from services.news_article_retrieval import news_article_retrieval
from services.chunk import chunk
import time
import uuid

router = APIRouter(prefix='/tweets')

# Initialize services globally
llm_service = None
embedder = None
pinecone_service = None

try:
    # Initialize LLM service
    llm_service = LLMService()
    
    # Initialize embedding service (shared with articles router)
    embedder = emb_service()
    
    # Initialize Pinecone service (shared with articles router)
    pinecone_service = PineconeService(
        index_name="news-articles",
        dimension=embedder.get_dimension()
    )
    # Connect to existing index
    pinecone_service.get_index()
    
except Exception as e:
    print(f"⚠ Warning: Could not initialize services: {e}")


@router.get("/generate")
def generate_tweets(query: str, count: int = 3, top_k: int = None, fetch_limit: int = None):
    """
    Generate tweets using enhanced RAG with dynamic article fetching
    
    Flow:
    1. Fetch fresh articles for the query
    2. Scrape article content
    3. Chunk the content
    4. Generate embeddings
    5. Store in Pinecone
    6. Search Pinecone for relevant articles
    7. Generate tweets with retrieved context
    
    Args:
        query (str): Topic or query to generate tweets about
        count (int): Number of tweets to generate (default: 3, max: 10)
        top_k (int): Number of articles to retrieve for context (auto-calculated if not provided)
        fetch_limit (int): Number of fresh articles to fetch (auto-calculated if not provided)
    
    Returns:
        dict: Response with tweets, sources, and pipeline statistics
    """
    # Validate input
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty")
    
    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 50")
  
    if top_k is None:
        # 2 relevant documents per tweet, capped at 10 for performance
        top_k = min(count * 2, 50)
    
    if fetch_limit is None:
        # Fetch 2x top_k to ensure quality retrieval, capped at 20
        fetch_limit = min(top_k * 2, 50)
    
    # Still validate if user provides explicit values
    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")
    
    if fetch_limit < 1 or fetch_limit > 50:
        raise HTTPException(status_code=400, detail="fetch_limit must be between 1 and 50")
    
    # Check if services are available
    if llm_service is None:
        return {
            "success": False,
            "query": query,
            "count": 0,
            "results": [],
            "sources": [],
            "error": "LLM service not available. Model initialization failed."
        }
    
    if embedder is None or pinecone_service is None:
        return {
            "success": False,
            "query": query,
            "count": 0,
            "results": [],
            "sources": [],
            "error": "RAG services not available. Embedding or Pinecone initialization failed."
        }
    
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        timestamp = int(time.time())
        pipeline_stats = {
            "articles_fetched": 0,
            "articles_scraped": 0,
            "chunks_created": 0,
            "vectors_stored": 0,
            "search_results": 0
        }
        
        nar = news_article_retrieval(query=query, limit=fetch_limit, session_id=session_id)
        ingestion_result = nar.get_ingestion()
        
        if not ingestion_result.get('success', False):
            print("⚠ No articles fetched, will use existing Pinecone content")
        else:
            pipeline_stats["articles_fetched"] = ingestion_result.get('count', 0)
            print(f"✓ Fetched {pipeline_stats['articles_fetched']} articles from {ingestion_result.get('source', 'Unknown')}")
            
            # Step 2: Scrape article content
            try:
                nar.retrieve()
                pipeline_stats["articles_scraped"] = pipeline_stats["articles_fetched"]
                print(f"✓ Scraped {pipeline_stats['articles_scraped']} articles")
            except Exception as scrape_error:
                print(f"⚠ Scraping failed: {scrape_error}. Using existing content.")
            
            # Step 3: Chunk the content
            try:
                ch = chunk()
                chunks_data = ch.textsplit()
                pipeline_stats["chunks_created"] = len(chunks_data)
                print(f"✓ Created {pipeline_stats['chunks_created']} chunks")
                
                # Step 4: Generate embeddings
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
                    vector_id = f"tweet_{query.replace(' ', '_')}_{chunk_data['doc_id']}_{chunk_data['chunk_id']}_{timestamp}"
                    
                    # Convert embedding to list - handle both numpy array and list
                    if hasattr(embedding, 'tolist'):
                        embedding_list = embedding.tolist()
                    else:
                        embedding_list = list(embedding)
                    
                    metadata = {
                        'text': chunk_data['text'][:1000],  # Limit text size for metadata
                        'filename': chunk_data['filename'],
                        'chunk_id': chunk_data['chunk_id'],
                        'doc_id': chunk_data['doc_id'],
                        'query': query,
                        'timestamp': timestamp,
                        'session_id': session_id  # Add session_id for cleanup
                    }
                    vectors.append((vector_id, embedding_list, metadata))
                
                # Upload to Pinecone
                pinecone_service.upsert_vectors(vectors)
                pipeline_stats["vectors_stored"] = len(vectors)
                
            except Exception as chunk_error:
                import traceback
                traceback.print_exc()
        
        # Step 6: Generate query embedding and search Pinecone
        query_embedding = embedder.generate_embeddings(query)
        
        search_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format articles as context
        context_articles = []
        for i, match in enumerate(search_results.get('matches', []), 1):
            article = {
                'text': match['metadata'].get('text', ''),
                'filename': match['metadata'].get('filename', 'Unknown'),
                'score': match['score']
            }
            context_articles.append(article)
        
        pipeline_stats["search_results"] = len(context_articles)
        tweets = llm_service.generate_tweets(
            query=query,
            count=count,
            context_articles=context_articles
        )
        
        # Format response with source attribution
        sources = [
            {
                "filename": article['filename'],
                "relevance_score": round(article['score'], 4)
            }
            for article in context_articles
        ]
        
        
        return {
            "success": True,
            "query": query,
            "session_id": session_id,  # Return session_id for client reference
            "count": len(tweets),
            "results": tweets,
            "sources": sources,
            "pipeline_stats": pipeline_stats
        }
        
    except Exception as e:
        print(f"❌ Enhanced RAG tweet generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "query": query,
            "count": 0,
            "results": [],
            "sources": [],
            "error": str(e)
        }


