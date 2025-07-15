from qdrant_client import QdrantClient, models
from langchain_openai import OpenAIEmbeddings
import uuid


class SemanticCache:
    def __init__(self, qdrant_url="http://vector-db:6333", cache_collection="semantic-cache", threshold=0.4):

        # OpenAI embedding model
        self.encoder = OpenAIEmbeddings(model="text-embedding-3-large")

        # Qdrant client (persistent)
        self.qdrant_client = QdrantClient(url=qdrant_url)

        # Cache collection
        self.cache_collection_name = cache_collection

        # Similarity threshold
        self.similarity_threshold = threshold

        # Create cache collection if not exists
        if not self.qdrant_client.collection_exists(self.cache_collection_name):
            self.qdrant_client.create_collection(
                collection_name=self.cache_collection_name,
                vectors_config=models.VectorParams(
                    size=3072,  # OpenAI text-embedding-3-large output size
                    distance=models.Distance.COSINE
                )
            )

    # Generate embedding
    def get_embedding(self, text):
        return self.encoder.embed_query(text)

    # Search cache
    def search_cache(self, query):
        vector = self.get_embedding(query)

        result = self.qdrant_client.search(
            collection_name=self.cache_collection_name,
            query_vector=vector,
            limit=1
        )

        if result:
            hit = result[0]
            if hit.score >= 1 - self.similarity_threshold:
                # Return cached response
                return hit.payload['response_text']

        # Return None
        return None

    # Add to cache
    def add_to_cache(self, question, response_text):
        vector = self.get_embedding(question)

        point_id = str(uuid.uuid4())

        self.qdrant_client.upsert(
            collection_name=self.cache_collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"question": question,
                             "response_text": response_text}
                )
            ]
        )

