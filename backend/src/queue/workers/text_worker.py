from src.ai_prompts.text_prompt import SYSTEM_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import logging
from src.cache.connection import SemanticCache

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)

cache = SemanticCache()

def process_text(query: str):
    try:
        # Check cache first
        cached_response = cache.search_cache(query)

        if cached_response:
            return cached_response

        # Prepare conversation
        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", query),
        ]

        # Invoke Gemini model
        response = llm.invoke(messages)

        # Cache the response for future use
        cache.add_to_cache(query, response.content)

        return response.content

    except Exception as e:
        logger.error(f"❌ Error in process_text: {e}", exc_info=True)
        return "An error occurred while processing your request. Please try again later."
