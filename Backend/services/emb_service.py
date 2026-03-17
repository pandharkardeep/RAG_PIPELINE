"""
Embedding Service — NVIDIA NeMo Retriever
Uses nvidia/llama-3.2-nemoretriever-300m-embed-v1 via OpenAI-compatible API.
Dimension: 2048
"""

from openai import OpenAI
from config import NVIDIA_NEMOTRON_API_KEY

# NVIDIA NIM endpoint (OpenAI-compatible)
_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
_MODEL_ID = "nvidia/llama-3.2-nemoretriever-300m-embed-v1"
_EMBEDDING_DIM = 2048


class emb_service:
    def __init__(self):
        """
        Initialize embedding service with NVIDIA NeMo Retriever model.
        Uses the OpenAI-compatible NVIDIA NIM endpoint.
        """
        if not NVIDIA_NEMOTRON_API_KEY:
            raise RuntimeError("NVIDIA_NEMOTRON_API_KEY is not set in environment variables.")

        self.client = OpenAI(
            api_key=NVIDIA_NEMOTRON_API_KEY,
            base_url=_NVIDIA_BASE_URL,
        )
        self.embedding_dimension = _EMBEDDING_DIM
        print(f"✓ Embedding service initialized (model={_MODEL_ID}, dim={_EMBEDDING_DIM})")

    def generate_embeddings(self, text):
        """
        Generate embeddings for given text.

        Args:
            text (str or list): Single text string or list of texts

        Returns:
            list: For a single string  → a single embedding vector (list[float])
                  For a list of strings → list of embedding vectors (list[list[float]])
        """
        single_input = isinstance(text, str)
        texts = [text] if single_input else list(text)

        # NVIDIA NIM accepts batches up to ~50; chunk larger batches
        all_embeddings = []
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=_MODEL_ID,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "NONE"},
            )
            # response.data is sorted by index
            batch_embs = [item.embedding for item in sorted(response.data, key=lambda d: d.index)]
            all_embeddings.extend(batch_embs)

        return all_embeddings[0] if single_input else all_embeddings

    def get_dimension(self):
        """Return the dimension of embeddings"""
        return self.embedding_dimension