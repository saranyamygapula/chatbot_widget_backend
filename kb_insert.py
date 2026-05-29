import asyncio
import os

from agno.knowledge.chunking.row import RowChunking
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.json_reader import JSONReader
from agno.tools.mcp import MCPTools
from agno.vectordb.pgvector import PgVector
from agno.vectordb.search import SearchType
from dotenv import load_dotenv

load_dotenv()

mcp_tools = MCPTools(transport="streamable-http", url=os.getenv("MCP_URL") + "/mcp")

embedder = SentenceTransformerEmbedder(
    id=os.getenv(
        "SENTENCE_TRANSFORMER_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
)

DATABASE_URL = os.getenv("DATABASE_URL")

vector_db = PgVector(
    table_name="ca_docs",
    db_url=DATABASE_URL,
    embedder=embedder,
    search_type=SearchType.hybrid,
)

knowledge = Knowledge(vector_db=vector_db)


async def main():
    print("Starting JSONL ingestion...")

    await knowledge.ainsert(
        url="https://famfqniodyyripuxthsv.supabase.co/storage/v1/object/public/ca-assistant/train.json",
        reader=JSONReader(
            chunking_strategy=RowChunking(),
        ),
    )

    print("Ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())
