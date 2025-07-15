from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from src.ai_prompts.pdf_prompt import pdf_processor_system_prompt
from langchain_openai import OpenAIEmbeddings, OpenAI
from src.cache.connection import SemanticCache
from qdrant_client import QdrantClient, models
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the GenAI client
llm = OpenAI()

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

COLLECTION_NAME = "pdf_chunks"

# Initialize Qdrant client
client = QdrantClient(url="http://vector-db:6333")

# Check if collection exists
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=3072,
            distance=models.Distance.COSINE
        )
    )

# Vector DB
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://vector-db:6333",
    collection_name=COLLECTION_NAME,
    embedding=embedding_model
)

cache = SemanticCache()


def process_query(query: str):
    try:
        # Check cache first
        cached_response = cache.search_cache(query)
        if cached_response:
            return cached_response

        # Search the vector db for relevant documents
        search_results = vector_db.similarity_search(query=query)

        # Construct the context
        context = "\n\n\n".join([
            f"Page Content: {result.page_content}\n"
            f"Page Number: {result.metadata.get('page_label', 'N/A')}\n"
            f"File Location: {result.metadata.get('source', 'N/A')}"
            for result in search_results
        ])

        # Construct the system prompt
        SYSTEM_PROMPT = pdf_processor_system_prompt(context)

        # Generate the response
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", query),
        ]

        response = llm.invoke(messages)

        # Cache the response for future use
        cache.add_to_cache(query, response)

        return response

    except Exception as e:
        logger.error(f"❌ Error in process_query: {e}", exc_info=True)
        return "An error occurred while processing your query. Please try again later."
