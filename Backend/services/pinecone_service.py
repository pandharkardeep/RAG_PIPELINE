from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_KEY
import time

import re


class PineconeService:
    def __init__(self, index_name="news-articles", dimension=384):
        """
        Initialize Pinecone service
        
        Args:
            index_name (str): Name of the Pinecone index
            dimension (int): Dimension of embeddings (384 for all-MiniLM-L6-v2)
        """
        self.pc = Pinecone(api_key=PINECONE_KEY)
        self.index_name = index_name
        self.dimension = dimension
        self.index = None
    
    def clean_article_text(text: str) -> str:
        if not text:
            return ""

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

    # Remove common junk patterns (tune this list)
        junk_patterns = [
            r"\bsubscribe\b",
            r"\bsign up\b",
            r"\bcookie\b",
            r"\badvertisement\b",
            r"\ball rights reserved\b",
        ]
        for pat in junk_patterns:
            text = re.sub(pat, "", text, flags=re.I)

        # Remove excessive repeated "he said / she said" style clutter
        text = re.sub(r"\b(he|she|they)\s+(said|told)\b", "", text, flags=re.I)

        # Re-normalize spacing after removals
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def create_index(self, metric="cosine", cloud="aws", region="us-east-1"):
        """
        Create a new Pinecone index if it doesn't exist
        
        Args:
            metric (str): Distance metric (cosine, euclidean, dotproduct)
            cloud (str): Cloud provider
            region (str): Cloud region
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating index '{self.index_name}'...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            print(f"Index '{self.index_name}' created successfully!")
        else:
            print(f"Index '{self.index_name}' already exists.")
        
        self.index = self.pc.Index(self.index_name)
        return self.index
    
    def get_index(self):
        """Get or connect to existing index"""
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
        return self.index
    
    def upsert_vectors(self, vectors):
        """
        Upsert vectors to Pinecone
        
        Args:
            vectors (list): List of tuples (id, embedding, metadata)
        """
        if self.index is None:
            self.get_index()
        
        # Clean metadata text for each vector
        cleaned_vectors = []
        for vector_id, embedding, metadata in vectors:
            # Clean the text in metadata if it exists
            if 'text' in metadata and metadata['text']:
                metadata['text'] = PineconeService.clean_article_text(metadata['text'])
            cleaned_vectors.append((vector_id, embedding, metadata))
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(cleaned_vectors), batch_size):
            batch = cleaned_vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"Upserted {min(i + batch_size, len(cleaned_vectors))}/{len(cleaned_vectors)} vectors")
    
    def query_similar(self, query_embedding, top_k=5, include_metadata=True):
        """
        Query for similar vectors
        
        Args:
            query_embedding (list): Query embedding vector
            top_k (int): Number of results to return
            include_metadata (bool): Whether to include metadata
            
        Returns:
            dict: Query results
        """
        if self.index is None:
            self.get_index()
        
        results = self.index.query(
            vector=query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding,
            top_k=top_k,
            include_metadata=include_metadata
        )
        return results
    
    def get_stats(self):
        """Get index statistics"""
        if self.index is None:
            self.get_index()
        return self.index.describe_index_stats()
    
    def delete_all(self):
        """Delete all vectors from index"""
        if self.index is None:
            self.get_index()
        self.index.delete(delete_all=True)
        print(f"All vectors deleted from index '{self.index_name}'")
    
    def delete_by_metadata_filter(self, filter_dict):
        """
        Delete vectors by metadata filter
        
        Args:
            filter_dict (dict): Metadata filter to match vectors for deletion
            
        Returns:
            int: Number of vectors deleted (estimated)
        """
        if self.index is None:
            self.get_index()
        
        try:
            # First, query to see how many vectors match
            # We'll use a dummy vector for counting
            stats_before = self.get_stats()
            
            # Delete by filter
            self.index.delete(filter=filter_dict)
            
            # Give Pinecone a moment to process the deletion
            import time
            time.sleep(2)
            
            stats_after = self.get_stats()
            deleted_count = stats_before.get('total_vector_count', 0) - stats_after.get('total_vector_count', 0)
            
            print(f"Deleted {deleted_count} vectors matching filter: {filter_dict}")
            return deleted_count
        except Exception as e:
            print(f"Error deleting by metadata filter: {e}")
            raise

