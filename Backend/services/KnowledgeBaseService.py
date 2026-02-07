from models.ThreadModels import (
    Insight, SearchResult, InsightConnection, Citation,
    IngestRequest, IngestResponse
)
from services.emb_service import emb_service
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import uuid
import os
import re
from datetime import datetime


class KnowledgeBaseService:
    """
    Core service for the Curiosity Compounder Knowledge Base.
    Handles insight ingestion, semantic search, and connection discovery.
    """
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize the Knowledge Base with ChromaDB and embedding service.
        
        Args:
            persist_directory: Directory for persistent storage (default: Backend/knowledge_data)
        """
        if persist_directory is None:
            persist_directory = os.path.join(os.path.dirname(__file__), "..", "knowledge_data")
        
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding service (reuse existing sentence-transformers)
        self.embedder = emb_service()
        
        # Get or create the insights collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name="insights",
            metadata={"description": "Curiosity Compounder Knowledge Base"}
        )
    
    def ingest_insight(self, request: IngestRequest) -> IngestResponse:
        """
        Ingest a new insight into the knowledge base.
        
        Args:
            request: IngestRequest with title, content, source_type, etc.
            
        Returns:
            IngestResponse with generated ID, extracted topics, and confirmation
        """
        # Generate unique ID
        insight_id = str(uuid.uuid4())
        
        # Extract topics from content
        extracted_topics = self._extract_topics(request.content)
        
        # Combine manual topics with extracted ones
        all_topics = list(set(request.topics + extracted_topics))
        
        # Generate embedding for the content
        combined_text = f"{request.title}\n\n{request.content}"
        embedding = self.embedder.generate_embeddings(combined_text).tolist()
        
        # Prepare metadata (ChromaDB requires flat structure with simple types)
        metadata = {
            "title": request.title,
            "source_type": request.source_type,
            "topics": ",".join(all_topics),  # Store as comma-separated string
            "citation_count": len(request.citations),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Add any additional metadata (flatten nested dicts)
        for key, value in request.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                metadata[f"meta_{key}"] = value
        
        # Store citation references as JSON string if present
        if request.citations:
            citation_data = [
                {"url": c.source_url, "title": c.source_title, "type": c.source_type}
                for c in request.citations
            ]
            metadata["citations_json"] = str(citation_data)
        
        # Add to ChromaDB collection
        self.collection.add(
            ids=[insight_id],
            embeddings=[embedding],
            documents=[request.content],
            metadatas=[metadata]
        )
        
        return IngestResponse(
            id=insight_id,
            message="Insight ingested successfully",
            extracted_topics=extracted_topics,
            citation_count=len(request.citations)
        )
    
    def search(self, query: str, top_k: int = 10, filters: Optional[Dict[str, str]] = None) -> List[SearchResult]:
        """
        Semantic search across all insights.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (source_type, topic, etc.)
            
        Returns:
            List of SearchResult with insights, scores, and connections
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embeddings(query).tolist()
        
        # Build where clause for filters
        where_clause = None
        if filters:
            where_conditions = []
            if "source_type" in filters and filters["source_type"]:
                where_conditions.append({"source_type": {"$eq": filters["source_type"]}})
            if "topic" in filters and filters["topic"]:
                where_conditions.append({"topics": {"$contains": filters["topic"]}})
            
            if len(where_conditions) == 1:
                where_clause = where_conditions[0]
            elif len(where_conditions) > 1:
                where_clause = {"$and": where_conditions}
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for idx, insight_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][idx]
                document = results["documents"][0][idx]
                distance = results["distances"][0][idx] if results["distances"] else 0
                
                # Convert distance to similarity score (ChromaDB uses L2 distance by default)
                similarity_score = 1 / (1 + distance)
                
                # Reconstruct Insight object
                insight = Insight(
                    id=insight_id,
                    title=metadata.get("title", "Untitled"),
                    content=document,
                    source_type=metadata.get("source_type", "unknown"),
                    topics=metadata.get("topics", "").split(",") if metadata.get("topics") else [],
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat())),
                    metadata={k.replace("meta_", ""): v for k, v in metadata.items() if k.startswith("meta_")}
                )
                
                # Find related insights (connections)
                related = self.find_connections(insight_id, top_k=3, exclude_self=True)
                
                # Suggest topics based on content
                suggested_topics = self._suggest_related_topics(insight.topics)
                
                search_results.append(SearchResult(
                    insight=insight,
                    similarity_score=similarity_score,
                    related_insights=related,
                    suggested_topics=suggested_topics
                ))
        
        return search_results
    
    def find_connections(self, insight_id: str, top_k: int = 5, exclude_self: bool = True) -> List[InsightConnection]:
        """
        Find insights related to a given insight based on semantic similarity.
        
        Args:
            insight_id: ID of the source insight
            top_k: Number of connections to find
            exclude_self: Whether to exclude the source insight from results
            
        Returns:
            List of InsightConnection objects
        """
        # Get the source insight's embedding
        try:
            source_result = self.collection.get(
                ids=[insight_id],
                include=["embeddings", "metadatas"]
            )
            
            if not source_result or not source_result["ids"]:
                return []
            
            source_embedding = source_result["embeddings"][0]
            source_metadata = source_result["metadatas"][0]
            source_topics = source_metadata.get("topics", "").split(",") if source_metadata.get("topics") else []
            
        except Exception:
            return []
        
        # Query for similar insights
        query_k = top_k + 1 if exclude_self else top_k
        results = self.collection.query(
            query_embeddings=[source_embedding],
            n_results=query_k,
            include=["metadatas", "distances"]
        )
        
        connections = []
        
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for idx, connected_id in enumerate(results["ids"][0]):
                # Skip self if needed
                if exclude_self and connected_id == insight_id:
                    continue
                
                if len(connections) >= top_k:
                    break
                
                metadata = results["metadatas"][0][idx]
                distance = results["distances"][0][idx] if results["distances"] else 0
                similarity_score = 1 / (1 + distance)
                
                # Find shared topics
                connected_topics = metadata.get("topics", "").split(",") if metadata.get("topics") else []
                shared_topics = list(set(source_topics) & set(connected_topics))
                
                connections.append(InsightConnection(
                    connected_insight_id=connected_id,
                    connected_insight_title=metadata.get("title", "Untitled"),
                    similarity_score=similarity_score,
                    shared_topics=shared_topics,
                    connection_type="semantic"
                ))
        
        return connections
    
    def get_insight(self, insight_id: str) -> Optional[Insight]:
        """
        Get a specific insight by ID.
        
        Args:
            insight_id: The insight's unique identifier
            
        Returns:
            Insight object or None if not found
        """
        try:
            result = self.collection.get(
                ids=[insight_id],
                include=["documents", "metadatas"]
            )
            
            if not result or not result["ids"]:
                return None
            
            metadata = result["metadatas"][0]
            document = result["documents"][0]
            
            return Insight(
                id=insight_id,
                title=metadata.get("title", "Untitled"),
                content=document,
                source_type=metadata.get("source_type", "unknown"),
                topics=metadata.get("topics", "").split(",") if metadata.get("topics") else [],
                created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat())),
                metadata={k.replace("meta_", ""): v for k, v in metadata.items() if k.startswith("meta_")}
            )
        except Exception:
            return None
    
    def get_all_topics(self) -> List[str]:
        """
        Get all unique topics across all insights.
        
        Returns:
            List of unique topic strings
        """
        all_results = self.collection.get(include=["metadatas"])
        
        topics_set = set()
        if all_results and all_results["metadatas"]:
            for metadata in all_results["metadatas"]:
                topics_str = metadata.get("topics", "")
                if topics_str:
                    for topic in topics_str.split(","):
                        topic = topic.strip()
                        if topic:
                            topics_set.add(topic)
        
        return sorted(list(topics_set))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with counts and metadata
        """
        all_results = self.collection.get(include=["metadatas"])
        
        total_insights = len(all_results["ids"]) if all_results["ids"] else 0
        
        source_types = {}
        topics_count = {}
        
        if all_results and all_results["metadatas"]:
            for metadata in all_results["metadatas"]:
                # Count source types
                source_type = metadata.get("source_type", "unknown")
                source_types[source_type] = source_types.get(source_type, 0) + 1
                
                # Count topics
                topics_str = metadata.get("topics", "")
                if topics_str:
                    for topic in topics_str.split(","):
                        topic = topic.strip()
                        if topic:
                            topics_count[topic] = topics_count.get(topic, 0) + 1
        
        return {
            "total_insights": total_insights,
            "source_types": source_types,
            "unique_topics": len(topics_count),
            "top_topics": sorted(topics_count.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _extract_topics(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract key topics from text using simple keyword extraction.
        Uses TF-based approach with stopword removal.
        
        Args:
            text: Content to extract topics from
            top_n: Number of topics to extract
            
        Returns:
            List of topic strings
        """
        # Simple stopwords list
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'their', 'them', 'he', 'she',
            'his', 'her', 'we', 'our', 'you', 'your', 'i', 'my', 'me', 'not',
            'no', 'yes', 'so', 'if', 'then', 'than', 'when', 'where', 'what',
            'which', 'who', 'how', 'why', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'just',
            'also', 'very', 'even', 'still', 'already', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'under',
            'again', 'further', 'once', 'here', 'there', 'any', 'up', 'down', 'out'
        }
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stopwords and count
        word_freq = {}
        for word in words:
            if word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:top_n]]
    
    def _suggest_related_topics(self, current_topics: List[str], max_suggestions: int = 3) -> List[str]:
        """
        Suggest related topics based on co-occurrence with current topics.
        
        Args:
            current_topics: List of topics from the current insight
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested topic strings
        """
        if not current_topics:
            return []
        
        # Get all insights and their topics
        all_results = self.collection.get(include=["metadatas"])
        
        # Count topic co-occurrences
        co_occurrence = {}
        current_topics_set = set(current_topics)
        
        if all_results and all_results["metadatas"]:
            for metadata in all_results["metadatas"]:
                topics_str = metadata.get("topics", "")
                if topics_str:
                    insight_topics = set(t.strip() for t in topics_str.split(",") if t.strip())
                    
                    # Check if this insight shares any topics with current
                    if insight_topics & current_topics_set:
                        # Count other topics in this insight
                        for topic in insight_topics - current_topics_set:
                            co_occurrence[topic] = co_occurrence.get(topic, 0) + 1
        
        # Sort by co-occurrence and return top suggestions
        sorted_topics = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)
        
        return [topic for topic, _ in sorted_topics[:max_suggestions]]
    
    def delete_insight(self, insight_id: str) -> bool:
        """
        Delete an insight from the knowledge base.
        
        Args:
            insight_id: ID of the insight to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[insight_id])
            return True
        except Exception:
            return False
