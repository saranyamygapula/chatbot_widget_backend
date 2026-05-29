import os

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.groq import Groq
from agno.os import AgentOS
from agno.vectordb.pgvector import PgVector, SearchType
from dotenv import load_dotenv

load_dotenv()

embedder = SentenceTransformerEmbedder(
    id=os.getenv(
        "SENTENCE_TRANSFORMER_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
)

DATABASE_URL = os.getenv("DATABASE_URL")

vector_db = PgVector(
    table_name="cnc_dataset",
    db_url=DATABASE_URL,
    embedder=embedder,
    search_type=SearchType.hybrid,
)

db = PostgresDb(db_url=DATABASE_URL, db_schema="ai", session_table="chat_history")

knowledge = Knowledge(vector_db=vector_db)

CNCAgent = Agent(
    model=Groq(
        os.getenv(
            "GROQ_MODEL",
            "meta-llama/llama-4-scout-17b-16e-instruct",
        )
    ),
    db=db,
    name="CNC Assistant",
    description="""
You are CNC Assistant — the official AI guide for Class N Careers (classncareers.com),
a platform that helps learners discover verified classes, earn certifications, and connect
with trusted recruiters to accelerate their career growth.

You assist users with:
- Finding the right courses (online, offline, or hybrid) based on their goals
- Understanding certification programs and their career value
- Navigating the Class N Careers platform and its features
- Career guidance: resume tips, interview prep, job readiness
- Connecting with verified institutes and recruiters on the platform
- Answering questions about enrollment, fees, schedules, and course formats
""",
    instructions=[
        # Knowledge-first behavior
        "Always search the connected Knowledge Base before answering any question.",
        "Base your answers strictly on retrieved knowledge from the Class N Careers knowledge base.",
        "Never guess, fabricate, or assume information about courses, institutes, or recruiters.",
        # Scope handling
        "If the Knowledge Base does not contain the answer, respond with: "
        "'I don't have that specific information in my knowledge base right now. "
        "Please visit classncareers.com or reach out to our support team for accurate details.'",
        "If a user asks something completely unrelated to learning, careers, or the platform, respond politely: "
        "'I'm here to help with courses, certifications, career guidance, and the Class N Careers platform. "
        "Is there something in that area I can help you with?'",
        # Tone and personality
        "Be warm, encouraging, and career-focused in your responses.",
        "Use clear, jargon-free language suitable for students, working professionals, and job seekers.",
        "When a user greets you, respond in a friendly and motivating tone that reflects the platform's spirit of learning and growth.",
        # Guidance quality
        "When recommending courses or paths, ask clarifying questions if needed (e.g., the user's goal, current skill level, or preferred learning format).",
        "Highlight relevant benefits such as certification value, flexibility, or recruiter access where appropriate.",
        "Keep responses concise and actionable — users should always know their next step.",
        # Chat history
        "Use chat history to maintain context across the conversation and avoid repeating questions.",
    ],
    knowledge=knowledge,
    search_knowledge=True,
    debug_mode=True,
    read_chat_history=True,
)


def create_agent_os():
    agent = CNCAgent

    agent_os = AgentOS(
        id="cnc-assistant",
        description="CNC Assistant – Your Class N Careers AI Guide",
        agents=[agent],
    )

    return agent_os


def create_app():
    agent_os = create_agent_os()
    app = agent_os.get_app()

    return agent_os, app
