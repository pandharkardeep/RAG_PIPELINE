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
    print("✓ LLM service initialized successfully")
    
    # Initialize embedding service (shared with articles router)
    embedder = emb_service()
    print("✓ Embedding service initialized successfully")
    
    # Initialize Pinecone service (shared with articles router)
    pinecone_service = PineconeService(
        index_name="news-articles",
        dimension=embedder.get_dimension()
    )
    # Connect to existing index
    pinecone_service.get_index()
    print("✓ Pinecone service initialized successfully")
    
except Exception as e:
    print(f"⚠ Warning: Could not initialize services: {e}")


@router.get("/generate")
def generate_tweets(query: str, count: int = 3, top_k: int = 5, fetch_limit: int = 10):
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
        top_k (int): Number of articles to retrieve for context (default: 5, max: 10)
        fetch_limit (int): Number of fresh articles to fetch (default: 10, max: 20)
    
    Returns:
        dict: Response with tweets, sources, and pipeline statistics
    """
    # Validate input
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty")
    
    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 50")
    
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
        
        print(f"\n{'='*60}")
        print(f"Enhanced RAG Tweet Generation for: '{query}'")
        print(f"Session ID: {session_id}")
        print(f"Fetching {fetch_limit} articles, generating {count} tweets")
        print(f"{'='*60}\n")
        
        # Step 1: Fetch fresh articles
        print("[1/7] Fetching fresh news articles...")
        nar = news_article_retrieval(query=query, limit=fetch_limit, session_id=session_id)
        ingestion_result = nar.get_ingestion()
        
        if not ingestion_result.get('success', False):
            print("⚠ No articles fetched, will use existing Pinecone content")
        else:
            pipeline_stats["articles_fetched"] = ingestion_result.get('count', 0)
            print(f"✓ Fetched {pipeline_stats['articles_fetched']} articles from {ingestion_result.get('source', 'Unknown')}")
            
            # Step 2: Scrape article content
            print("\n[2/7] Scraping article content...")
            try:
                nar.retrieve()
                pipeline_stats["articles_scraped"] = pipeline_stats["articles_fetched"]
                print(f"✓ Scraped {pipeline_stats['articles_scraped']} articles")
            except Exception as scrape_error:
                print(f"⚠ Scraping failed: {scrape_error}. Using existing content.")
            
            # Step 3: Chunk the content
            print("\n[3/7] Chunking articles...")
            try:
                ch = chunk()
                chunks_data = ch.textsplit()
                pipeline_stats["chunks_created"] = len(chunks_data)
                print(f"✓ Created {pipeline_stats['chunks_created']} chunks")
                
                # Step 4: Generate embeddings
                print("\n[4/7] Generating embeddings...")
                texts = [chunk_data['text'] for chunk_data in chunks_data]
                print(f"DEBUG: Extracted {len(texts)} texts from chunks_data")
                print(f"DEBUG: chunks_data type: {type(chunks_data)}")
                if len(chunks_data) > 0:
                    print(f"DEBUG: First chunk type: {type(chunks_data[0])}")
                    print(f"DEBUG: First chunk keys: {chunks_data[0].keys() if isinstance(chunks_data[0], dict) else 'Not a dict'}")
                
                # Generate embeddings in batches
                batch_size = 32
                all_embeddings = []
                
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_embeddings = embedder.generate_embeddings(batch_texts)
                    print(f"DEBUG: batch_embeddings type: {type(batch_embeddings)}, shape: {batch_embeddings.shape if hasattr(batch_embeddings, 'shape') else 'no shape'}")
                    all_embeddings.extend(batch_embeddings)
                
                print(f"✓ Generated {len(all_embeddings)} embeddings")
                print(f"DEBUG: all_embeddings type: {type(all_embeddings)}")
                if len(all_embeddings) > 0:
                    print(f"DEBUG: First embedding type: {type(all_embeddings[0])}")
                
                # Step 5: Store in Pinecone
                print("\n[5/7] Storing vectors in Pinecone...")
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
                print(f"✓ Stored {pipeline_stats['vectors_stored']} vectors in Pinecone")
                
            except Exception as chunk_error:
                import traceback
                print(f"⚠ Chunking/embedding/storage failed: {chunk_error}. Will search existing content.")
                print("DEBUG: Full traceback:")
                traceback.print_exc()
        
        # Step 6: Generate query embedding and search Pinecone
        print("\n[6/7] Searching Pinecone for relevant articles...")
        query_embedding = embedder.generate_embeddings(query)
        print(f"✓ Query embedding generated (dimension: {len(query_embedding)})")
        
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
            print(f"  {i}. {article['filename']} (score: {article['score']:.4f})")
        
        pipeline_stats["search_results"] = len(context_articles)
        print(f"✓ Retrieved {pipeline_stats['search_results']} articles for context")
        
        # Step 7: Generate tweets using LLM with article context
        print(f"\n[7/7] Generating {count} tweets with retrieved context...")
        tweets = llm_service.generate_tweets(
            query=query,
            count=count,
            context_articles=context_articles
        )
        
        print(f"✓ Generated {len(tweets)} tweets successfully\n")
        for i, tweet in enumerate(tweets, 1):
            print(f"{i}. {tweet}\n")
        
        # Format response with source attribution
        sources = [
            {
                "filename": article['filename'],
                "relevance_score": round(article['score'], 4)
            }
            for article in context_articles
        ]
        
        print(f"{'='*60}\n")
        
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


