from crewai import Task
from src.agents_src.agents.question_answer_agent import qa_agent
from pydantic import BaseModel


class AnswerStructure(BaseModel):
    answer: str
    sources: list[str]
    tool_used: str
    rationale: str

qa_task = Task(
    agent=qa_agent,
    name="Question Answering Task",
    description="""
Your ONLY job is to call the rag_query_tool with this exact query: "{user_query}"
You are FORBIDDEN from answering without calling rag_query_tool first.
Step 1: Call rag_query_tool with query="{user_query}"
Step 2: Use the result to formulate your answer.
chat_history: "{chat_history}"

- Do NOT answer from your own knowledge
- If rag_query_tool returns no results, only then say the knowledge source does not contain the information
- Always include sources, tool_used, and rationale in your response
""",
    expected_output="""
    A structured JSON object with the following fields:
    {
    "answer": "Direct response to the query (1-3 paragraphs, clear and accurate).
                If no answer is found, return: 'The knowledge source does not contain the required information.'",
    "sources": ["List of document titles, sections, or citations used (empty list if none)"],
    "tool_used": "Name of the retrieval/analysis tool invoked (e.g., RAG Retriever, VectorDB, ChatHistory, etc.)",
    "rationale": "Brief explanation of why this answer was chosen, or why no relevant information was found"
    }
    """,
    output_pydantic=AnswerStructure,
)