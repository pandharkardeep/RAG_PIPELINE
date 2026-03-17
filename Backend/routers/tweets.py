from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from services.llm_service import LLMService
from services.emb_service import emb_service
from services.pinecone_service import PineconeService
from services.news_article_retrieval import news_article_retrieval
from services.chunk import chunk
import time
import uuid
import numpy as np
from collections import defaultdict

router = APIRouter(prefix='/tweets')

# Initialize services globally
llm_service = None
embedder = None
pinecone_service = None

try:
    llm_service = LLMService()
    embedder = emb_service()
    pinecone_service = PineconeService(
        index_name="news-articles",
        dimension=embedder.get_dimension()
    )
    pinecone_service.get_index()
except Exception as e:
    print(f"⚠ Warning: Could not initialize services: {e}")


# ─── Intelligence Pipeline Helpers ────────────────────────────────────────

def _cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    dot = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(dot / norm) if norm > 0 else 0.0


def _deduplicate_articles(articles: list, threshold: float = 0.92) -> tuple:
    """
    Duplicate Detection: Embed article titles and skip near-duplicates.

    Args:
        articles: List of article dicts with 'title' key
        threshold: Cosine similarity threshold (> this = duplicate)

    Returns:
        (unique_articles, skipped_count)
    """
    if not articles or not embedder or len(articles) <= 1:
        return articles, 0

    titles = [a.get("title", "") for a in articles]
    title_embeddings = embedder.generate_embeddings(titles)

    keep_mask = [True] * len(articles)
    skipped = 0

    for i in range(len(articles)):
        if not keep_mask[i]:
            continue
        for j in range(i + 1, len(articles)):
            if not keep_mask[j]:
                continue
            sim = _cosine_similarity(title_embeddings[i], title_embeddings[j])
            if sim > threshold:
                keep_mask[j] = False
                skipped += 1
                print(f"  ⤳ Duplicate (sim={sim:.3f}): \"{titles[j][:60]}…\"")

    unique = [a for a, keep in zip(articles, keep_mask) if keep]
    return unique, skipped


def _cluster_by_category(articles: list) -> dict:
    """
    Topic Clustering: Group articles by their category field.

    Returns:
        dict mapping category → list of articles
    """
    clusters = defaultdict(list)
    for article in articles:
        category = article.get("category", "general") or "general"
        # Take first category if comma-separated
        primary_cat = category.split(",")[0].strip().lower()
        clusters[primary_cat].append(article)

    # Log cluster distribution
    for cat, items in clusters.items():
        print(f"  📁 Cluster '{cat}': {len(items)} articles")

    return dict(clusters)


def _fetch_historical_context(query: str, top_k: int = 5) -> list:
    """
    Semantic Context Enrichment: Query Pinecone for older vectors
    matching the query to give the LLM temporal awareness.

    Returns:
        List of historical context snippets
    """
    if not embedder or not pinecone_service:
        return []

    try:
        query_embedding = embedder.generate_embeddings(query)
        results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        historical = []
        for match in results.get('matches', []):
            text = match['metadata'].get('text', '')
            ts = match['metadata'].get('timestamp', 0)
            if text and ts:
                historical.append({
                    'text': text,
                    'timestamp': ts,
                    'score': match['score'],
                    'query': match['metadata'].get('query', ''),
                })

        if historical:
            print(f"  📚 Found {len(historical)} historical context snippets")
        return historical

    except Exception as e:
        print(f"  ⚠ Historical context fetch failed: {e}")
        return []


# ─── Main Endpoint ────────────────────────────────────────────────────────

@router.get("/generate")
def generate_tweets(
    query: str,
    count: int = 3,
    top_k: int = None,
    fetch_limit: int = None,
    tone: Optional[str] = "sharp",
    include_sources: Optional[List[str]] = Query(default=None, description="Only include articles from these media houses (e.g. BBC, CNN)"),
    exclude_sources: Optional[List[str]] = Query(default=None, description="Exclude articles from these media houses (e.g. Fox News)")
):
    """
    Generate tweets using enhanced RAG pipeline with intelligence layers:

    Pipeline:
    1. Fetch fresh articles (newsdata.io)
    2. Embed headlines (nemoretriever)
    3. Intelligence pipeline:
       - Duplicate check (skip if similarity > 0.92)
       - Topic clustering (batch by category)
       - Semantic context fetch (enrich with related past news)
    4. Scrape, chunk, embed, store in Pinecone
    5. Generate tweets (deepseek-v3.2)
    """
    # Validate input
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty")

    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 50")

    if top_k is None:
        top_k = min(count * 2, 50)

    if fetch_limit is None:
        fetch_limit = min(top_k * 2, 50)

    if top_k < 1 or top_k > 50:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 50")

    if fetch_limit < 1 or fetch_limit > 50:
        raise HTTPException(status_code=400, detail="fetch_limit must be between 1 and 50")

    # Check if services are available
    if llm_service is None:
        return {
            "success": False, "query": query, "count": 0,
            "results": [], "sources": [],
            "error": "LLM service not available. Model initialization failed."
        }

    if embedder is None or pinecone_service is None:
        return {
            "success": False, "query": query, "count": 0,
            "results": [], "sources": [],
            "error": "RAG services not available. Embedding or Pinecone initialization failed."
        }

    try:
        session_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time())
        pipeline_stats = {
            "articles_fetched": 0,
            "duplicates_removed": 0,
            "articles_after_dedup": 0,
            "topic_clusters": 0,
            "historical_context_items": 0,
            "articles_scraped": 0,
            "chunks_created": 0,
            "vectors_stored": 0,
            "search_results": 0,
        }

        # ─── Step 1: Fetch articles ──────────────────────────────────
        print(f"\n{'='*60}")
        print(f"🚀 Tweet Pipeline | query={query!r} | count={count} | tone={tone}")
        print(f"{'='*60}")

        nar = news_article_retrieval(
            query=query, limit=fetch_limit, session_id=session_id,
            include_sources=include_sources, exclude_sources=exclude_sources
        )
        ingestion_result = nar.get_ingestion()

        if not ingestion_result.get('success', False):
            print("⚠ No articles fetched, will use existing Pinecone content")
        else:
            articles = ingestion_result.get('data', [])
            pipeline_stats["articles_fetched"] = len(articles)
            print(f"\n[1/6] ✓ Fetched {len(articles)} articles from {ingestion_result.get('source', 'Unknown')}")

            # ─── Step 2: Duplicate Detection ─────────────────────────
            print("\n[2/6] Deduplicating articles…")
            unique_articles, skipped = _deduplicate_articles(articles)
            pipeline_stats["duplicates_removed"] = skipped
            pipeline_stats["articles_after_dedup"] = len(unique_articles)
            print(f"  ✓ Kept {len(unique_articles)}, removed {skipped} duplicates")

            # Update the dataframe in the retrieval object with deduplicated articles
            import pandas as pd
            nar.df = pd.DataFrame(unique_articles)
            nar.df.reset_index(drop=True, inplace=True)

            # ─── Step 3: Topic Clustering ────────────────────────────
            print("\n[3/6] Clustering by topic…")
            clusters = _cluster_by_category(unique_articles)
            pipeline_stats["topic_clusters"] = len(clusters)

            # ─── Step 4: Historical Context ──────────────────────────
            print("\n[4/6] Fetching historical context…")
            historical = _fetch_historical_context(query, top_k=5)
            pipeline_stats["historical_context_items"] = len(historical)

            # ─── Step 5: Scrape, Chunk, Embed, Store ─────────────────
            print("\n[5/6] Scraping & embedding…")
            try:
                nar.retrieve()
                pipeline_stats["articles_scraped"] = len(unique_articles)
                print(f"  ✓ Scraped {pipeline_stats['articles_scraped']} articles")
            except Exception as scrape_error:
                print(f"  ⚠ Scraping failed: {scrape_error}. Using existing content.")

            try:
                ch = chunk()
                chunks_data = ch.textsplit()
                pipeline_stats["chunks_created"] = len(chunks_data)
                print(f"  ✓ Created {pipeline_stats['chunks_created']} chunks")

                # Generate embeddings
                texts = [chunk_data['text'] for chunk_data in chunks_data]
                batch_size = 32
                all_embeddings = []

                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_embeddings = embedder.generate_embeddings(batch_texts)
                    all_embeddings.extend(batch_embeddings)

                vectors = []
                for idx, (chunk_data, embedding) in enumerate(zip(chunks_data, all_embeddings)):
                    vector_id = f"tweet_{query.replace(' ', '_')}_{chunk_data['doc_id']}_{chunk_data['chunk_id']}_{timestamp}"

                    if hasattr(embedding, 'tolist'):
                        embedding_list = embedding.tolist()
                    else:
                        embedding_list = list(embedding)

                    metadata = {
                        'text': chunk_data['text'][:1000],
                        'filename': chunk_data['filename'],
                        'chunk_id': chunk_data['chunk_id'],
                        'doc_id': chunk_data['doc_id'],
                        'query': query,
                        'timestamp': timestamp,
                        'session_id': session_id,
                    }
                    vectors.append((vector_id, embedding_list, metadata))

                pinecone_service.upsert_vectors(vectors)
                pipeline_stats["vectors_stored"] = len(vectors)

            except Exception as chunk_error:
                import traceback
                traceback.print_exc()

        # ─── Step 6: Search & Generate ───────────────────────────────
        print(f"\n[6/6] Generating tweets via DeepSeek V3.2…")

        query_embedding = embedder.generate_embeddings(query)
        search_results = pinecone_service.query_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Build context from search results
        context_articles = []
        for i, match in enumerate(search_results.get('matches', []), 1):
            context_articles.append({
                'text': match['metadata'].get('text', ''),
                'filename': match['metadata'].get('filename', 'Unknown'),
                'score': match['score'],
            })
        pipeline_stats["search_results"] = len(context_articles)

        # Enrich context with historical snippets
        if 'historical' in dir() and historical:
            for h in historical:
                context_articles.append({
                    'text': h['text'],
                    'filename': f"[historical] query={h.get('query', 'unknown')}",
                    'score': h['score'],
                })

        # Enrich context with cluster metadata for better coherence
        if 'clusters' in dir() and clusters:
            cluster_summary = ", ".join(
                f"{cat} ({len(items)})" for cat, items in clusters.items()
            )
            # Prepend cluster info as a synthetic context article
            context_articles.insert(0, {
                'text': f"Topic clusters for '{query}': {cluster_summary}. "
                        f"Generate tweets that acknowledge categories without mixing unrelated topics.",
                'filename': '[meta] topic_clusters',
                'score': 1.0,
            })

        # Generate tweets
        tweets = llm_service.generate_tweets(
            query=query,
            count=count,
            context_articles=context_articles,
            tone=tone or "sharp"
        )

        # Format response with source attribution
        sources = [
            {
                "filename": article['filename'],
                "relevance_score": round(article['score'], 4)
            }
            for article in context_articles
            if not article['filename'].startswith('[')  # skip meta sources
        ]

        print(f"\n{'='*60}")
        print(f"✓ Pipeline complete | {len(tweets)} tweets | stats: {pipeline_stats}")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "query": query,
            "session_id": session_id,
            "count": len(tweets),
            "results": tweets,
            "sources": sources,
            "pipeline_stats": pipeline_stats,
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
            "error": str(e),
        }
