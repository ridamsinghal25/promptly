from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


# upload pdf file to vector db
def upload_pdf(file_path):
    try:
        # Load PDF
        loader = PyPDFLoader(file_path)

        docs = loader.load()  # Read PDF File

        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=300,
        )
        split_docs = text_splitter.split_documents(documents=docs)

        # Vector Embeddings
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )

        # Store embeddings in Qdrant
        QdrantVectorStore.from_documents(
            documents=split_docs,
            url="http://vector-db:6333",
            collection_name="pdf_chunks",
            embedding=embedding_model
        )

        return "✅ PDF uploaded and processed successfully."

    except Exception as e:
        logger.error(f"❌ Error during PDF upload: {e}", exc_info=True)
        return f"❌ Error during PDF upload: {str(e)}"

    finally:
        # Clean up the file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted file: {file_path}")
            except Exception as cleanup_error:
                print(f"⚠️ Failed to delete file {file_path}: {cleanup_error}")
