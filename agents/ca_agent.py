import os

from agno.agent import Agent
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.groq import Groq
from agno.os import AgentOS
from agno.tools.mcp import MCPTools
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from dotenv import load_dotenv

load_dotenv()

mcp_tools = MCPTools(transport="streamable-http", url="http://localhost:3333/mcp")

embedder = SentenceTransformerEmbedder(
    id=os.getenv(
        "SENTENCE_TRANSFORMER_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",  # fallback
    )
)

vector_db = LanceDb(
    table_name="ca_docs",
    uri="./lancedb",
    search_type=SearchType.vector,
    embedder=embedder,
)

knowledge = Knowledge(vector_db=vector_db)


CaAgent = Agent(
    model=Groq(
        os.getenv(
            "GROQ_MODEL",
            "meta-llama/llama-4-scout-17b-16e-instruct",  # fallback
        )
    ),
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
