from pinecone import Pinecone
from config import PINECONE_KEY

pc = Pinecone(api_key = PINECONE_KEY)
index = pc.Index("belovedrag")