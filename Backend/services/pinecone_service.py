from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_KEY
import time

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
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"Upserted {min(i + batch_size, len(vectors))}/{len(vectors)} vectors")
    
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
