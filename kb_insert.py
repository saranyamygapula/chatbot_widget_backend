import asyncio
import os

from agno.knowledge.chunking.row import RowChunking
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.json_reader import JSONReader
from agno.vectordb.pgvector import PgVector
from agno.vectordb.search import SearchType
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

knowledge = Knowledge(vector_db=vector_db)

# Paste a fresh signed URL from Supabase Storage here — no spaces or line breaks
DATASET_URL = os.getenv("DATASET_URL")  # recommended: put it in .env


async def main():
    print("Starting JSON ingestion...")

    await knowledge.ainsert(
        url=DATASET_URL,
        reader=JSONReader(
            chunking_strategy=RowChunking(),
        ),
    )

    print("Ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())
