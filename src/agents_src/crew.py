from crewai import Crew, Process
from src.agents_src.agents.question_answer_agent import qa_agent
from src.agents_src.tasks.Question_answer_task import qa_task

qa_crew = Crew(
    agents = [qa_agent],
    tasks = [qa_task],
    process=Process.sequential,   # ✅ add this
)


print("Tools registered:", [t.name for t in qa_agent.tools])