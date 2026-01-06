from sentence_transformers import SentenceTransformer

class emb_service:
    def __init__(self):
        """
        Initialize embedding service with Sentence Transformers model
        Using all-MiniLM-L6-v2: lightweight, fast, optimized for semantic similarity
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384
    
    def generate_embeddings(self, text):
        """
        Generate embeddings for given text
        
        Args:
            text (str or list): Single text string or list of texts
            
        Returns:
            numpy.ndarray: Embedding vector(s)
        """
        embeddings = self.model.encode(text)
        return embeddings
    
    def get_dimension(self):
        """Return the dimension of embeddings"""
        return self.embedding_dimension
    
    def ingest_news_to_pinecone():
        """
        Main function to ingest news articles into Pinecone
        """
        # Step 1: Initialize services
        chunker = chunk()
        embedder = emb_service()
        pinecone = PineconeService(
            index_name="news-articles",
            dimension=embedder.get_dimension()
        )
        
        # Step 2: Create Pinecone index
        pinecone.create_index(metric="cosine", cloud="aws", region="us-east-1")
        
        # Step 3: Chunk documents
        chunks_data = chunker.textsplit()
        
        # Step 4: Generate embeddings
        texts = [chunk_data['text'] for chunk_data in chunks_data]
        
        # Generate embeddings in batches for efficiency
        batch_size = 32
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding batches"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = embedder.generate_embeddings(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        
        
        # Step 5: Prepare vectors for Pinecone
        vectors = []
        
        for idx, (chunk_data, embedding) in enumerate(zip(chunks_data, all_embeddings)):
            vector_id = f"news_{chunk_data['doc_id']}_{chunk_data['chunk_id']}"
            metadata = {
                'text': chunk_data['text'],
                'filename': chunk_data['filename'],
                'chunk_id': chunk_data['chunk_id'],
                'doc_id': chunk_data['doc_id']
            }
            vectors.append((vector_id, embedding.tolist(), metadata))
        
        # Upload to Pinecone
        pinecone.upsert_vectors(vectors)
        
        
        stats = pinecone.get_stats()
        
        
        test_query = "construction projects and infrastructure development"
        test_embedding = embedder.generate_embeddings(test_query)
        results = pinecone.query_similar(test_embedding, top_k=3)
        
        print(f"\nTop 3 results for query: '{test_query}'")
        for i, match in enumerate(results['matches'], 1):
            print(f"\n{i}. Score: {match['score']:.4f}")
            print(f"   File: {match['metadata']['filename']}")
            print(f"   Text preview: {match['metadata']['text'][:200]}...")
        
        print("\n✓ All done! Your news articles are now in Pinecone.")