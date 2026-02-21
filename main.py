import os

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from agents.ca_agent import create_app
from routers.agno_route import agno_router

load_dotenv()


agent_os, app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.add_middleware(
#     JWTMiddleware,
#     verification_keys=["your-jwt-verification-key"],
#     validate=True,
#     exclude_paths=["/health", "/docs", "/agnochat/start"],
# )


app.include_router(agno_router)


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "4093"))

    agent_os.serve(
        app=app,
        port=8000,
        reload=False,
    )
    # uvicorn.run(
    #     "main:app",
    #     host="0.0.0.0",
    #     port=port,
    #     reload=True,
    # )


if __name__ == "__main__":
    main()
