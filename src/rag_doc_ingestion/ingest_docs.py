import logging
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore
from src.rag_doc_ingestion.config.doc_ingestion_settings import DocIngestionSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

settings = DocIngestionSettings()
logger.info("logging huggingface embedding model...")
embed_model = HuggingFaceEmbedding()

def build_vector_store_from_documents():
    logger.info("starting vector store ingestion process")
    try:
        docs_dir_path = settings.DOCUMENTS_DIR
        vector_store_path = settings.VECTOR_STORE_DIR
        collection_name = settings.COLLECTION_NAME
        logger.info(f"loading documents from directory:{docs_dir_path}")
        loader = SimpleDirectoryReader(input_dir=docs_dir_path)
        documents = loader.load_data()

        # create parser
        parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=50)
        logger.info("parsin documents into nodes")
        nodes = parser.get_nodes_from_documents(documents)
        logger.info(f"parsed {len(nodes)} nodes")
        logger.info(f"initializing chromaDB presistent clinet at {vector_store_path}")
        db = chromadb.PersistentClient(path=vector_store_path)
        
        # create or retrieve data
        chroma_collection = db.get_or_create_collection(name=collection_name)
        logger.info(f"creating chroma vector store with collection name: {collection_name}")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        # create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        logger.info("building vector stroe index")
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            vector_store=vector_store,
            embed_model=embed_model
        )
        logger.info("vectore storage build completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Error during vectore store build {e}")
        return 1
    
if __name__ == "__main__":
    from llama_index.core import SimpleDirectoryReader
    loader = SimpleDirectoryReader(input_dir=r"C:\Users\shreyas.s1\Documents\capstone_project\docs_dir")
    documents = loader.load_data()
    for doc in documents:
        print("=== DOCUMENT ===")
        print(doc.text[:500])  # print first 500 characters
        print()
    result = build_vector_store_from_documents()

    # BAAI/bge-small-en-v1.5 model used for hugging face