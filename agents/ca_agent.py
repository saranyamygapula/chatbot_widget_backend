import os

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.groq import Groq
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from agno.vectordb.pgvector import PgVector, SearchType
from dotenv import load_dotenv

load_dotenv()

mcp_tools = MCPTools(transport="streamable-http", url=os.getenv("MCP_URL") + "/mcp")

embedder = SentenceTransformerEmbedder(
    id=os.getenv(
        "SENTENCE_TRANSFORMER_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",  # fallback
    )
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres.famfqniodyyripuxthsv:J2fztK65Ar3o9zhF@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres",  # fallback
)


vector_db = PgVector(
    table_name="ca_docs",
    db_url=DATABASE_URL,
    embedder=embedder,
    search_type=SearchType.hybrid,
)

db = PostgresDb(db_url=DATABASE_URL, db_schema="ai", session_table="chat_history")

knowledge = Knowledge(vector_db=vector_db)


CaAgent = Agent(
    model=Groq(
        os.getenv(
            "GROQ_MODEL",
            "meta-llama/llama-4-scout-17b-16e-instruct",  # fallback
        )
    ),
    db=db,
    name="CA Assistant",
    description="""
A professional Chartered Accountant (CA) assistant specialized in:
- GST and Indirect Tax
- Income Tax and TDS
- Accounting and Bookkeeping
- Audit and Compliance
- Company filings and regulatory guidance
""",
    # ✅ INSTRUCTIONS (Behavior Rules)
    instructions=[
        # Knowledge-first behavior
        "Always search the connected Knowledge Base before answering.",
        # Answer grounding
        "Provide answers only based on retrieved knowledge.",
        "Never guess or make up information.",
        # If KB has no answer
        "If the Knowledge Base does not contain the answer, respond with: "
        "'Sorry, I do not have this information available in my CA knowledge base.'",
        # Scope control
        "If the user asks non-CA or unrelated general questions, respond politely: "
        "'I can help only with CA, GST, Tax, and Accounting-related questions.'",
        # Conversation tone
        "Always respond in a respectful, clear, and professional tone.",
        "If the user greets you, respond warmly and professionally.",
        # Tool usage (if applicable)
        "When user asks to send an email, you MUST call the send_email tool.",
        "Do not draft emails manually.",
        "Use available tools when required to complete tasks accurately.",
    ],
    knowledge=knowledge,
    search_knowledge=True,
    debug_mode=True,
    read_chat_history=True,
    # tools=[send_email],
    tools=[mcp_tools],
)


def create_agent_os():
    agent = CaAgent

    agent_os = AgentOS(
        id="CA agent",
        description="Ca Agent",
        agents=[agent],
    )

    return agent_os


def create_app():
    agent_os = create_agent_os()
    app = agent_os.get_app()

    return agent_os, app
