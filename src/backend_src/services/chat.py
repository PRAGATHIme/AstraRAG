import logging
from src.agents_src.tools.rag_qa_tool import rag_query_tool

logger = logging.getLogger(__name__)

def get_answer(chat_history: list) -> dict:
    last_user_message = chat_history[-1]
    user_query = last_user_message["content"]
    result = rag_query_tool.run(user_query)
    return {
        "answer": result.get("answer", "No answer found"),
        "sources": result.get("source_files", []),
        "tool_used": "RAG Retriever",
        "rationale": "Answer retrieved directly from vector store"
    }