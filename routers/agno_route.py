import base64
import io
import json
import os

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from agents.cnc_agent import CNCAgent
from core.htil_handler import handle_purchase_resume
from core.run_store import RUN_STORE
from models.Model import ChatRequest, ResumeRequest

agno_router = APIRouter(prefix="/agnochat", tags=["Agno Chatbot"])


class ChatRequest(BaseModel):
    user_input: str


# @agno_router.post("/start")
# async def start_chat(request: ChatRequest):
#     """
#     Standard Agno + MCP Chat Endpoint

#     Supports:
#     ✅ Normal responses
#     ✅ MCP tool calling
#     ✅ Tool JSON-string outputs
#     ✅ Human-in-the-loop pause
#     ✅ Frontend-safe standardized format
#     """

#     try:
#         # -----------------------------------
#         # 1. Run agent asynchronously
#         # -----------------------------------
#         run = await CaAgent.arun(input=request.user_input, user_id="")

#         # -----------------------------------
#         # 2. Human-in-the-loop Pause Handling
#         # -----------------------------------
#         if run.status.name == "paused":
#             tool_exec = run.requirements[0].tool_execution

#             return {
#                 "status": "paused",
#                 "run_id": run.run_id,
#                 "message": "Tool execution requires approval.",
#                 "action": {
#                     "tool_name": tool_exec.tool_name,
#                     "args": tool_exec.tool_args,
#                 },
#                 "data": None,
#             }

#         # -----------------------------------
#         # 3. Completed Response Handling
#         # -----------------------------------
#         if run.status.name == "completed":
#             # Default response message
#             assistant_message = run.content
#             payload_data = None

#             # -----------------------------------
#             # 4. If tool was executed, extract output
#             # -----------------------------------
#             if run.tools:
#                 last_tool = run.tools[-1]
#                 raw_result = last_tool.result

#                 # Try parsing tool result as JSON string
#                 try:
#                     parsed = json.loads(raw_result)

#                     # If tool returned structured output
#                     assistant_message = parsed.get("message", assistant_message)
#                     payload_data = parsed.get("data", None)

#                 except Exception:
#                     # Tool returned plain string → keep as message
#                     assistant_message = raw_result or assistant_message

#             return {
#                 "status": "success",
#                 "run_id": run.run_id,
#                 "message": assistant_message,
#                 "action": None,
#                 "data": payload_data,
#             }

#         # -----------------------------------
#         # 5. Fallback (Unexpected Status)
#         # -----------------------------------
#         return {
#             "status": "error",
#             "run_id": getattr(run, "run_id", None),
#             "message": f"Unexpected run status: {run.status.name}",
#             "action": None,
#             "data": None,
#         }

#     # -----------------------------------
#     # 6. Global Error Catch
#     # -----------------------------------
#     except Exception as e:
#         return {
#             "status": "error",
#             "run_id": None,
#             "message": str(e),
#             "action": None,
#             "data": None,
#         }

import asyncio
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

# --------------------------------------------------
# Router
# --------------------------------------------------

agno_router = APIRouter()

# --------------------------------------------------
# Agent Imports
# --------------------------------------------------
# from agents.cnc_agent import CNCAgent
# Assume CNCAgent is already defined

# --------------------------------------------------
# Request Models
# --------------------------------------------------


class ChatRequest(BaseModel):
    user_input: str


class StopRequest(BaseModel):
    run_id: str


# --------------------------------------------------
# Global Stores
# --------------------------------------------------

# Store active running asyncio tasks
RUN_TASKS: Dict[str, asyncio.Task] = {}

# Store paused runs (human approval required)
PAUSED_RUNS: Dict[str, object] = {}


# --------------------------------------------------
# START Endpoint
# --------------------------------------------------


class AudioRequest(BaseModel):
    audioBase64: str
    lang: str = "en"


@agno_router.post("/groq/transcribe")
async def transcribe_audio(body: AudioRequest):
    try:
        # Decode base64 to bytes
        audio_bytes = base64.b64decode(body.audioBase64)

        # Build multipart form data
        files = {
            "file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav"),
        }
        data = {
            "model": "whisper-large-v3",
            "language": "en",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                },
                files=files,
                data=data,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        return {"error": str(e), "detail": e.response.text}
    except Exception as e:
        return {"error": str(e)}


@agno_router.post("/start")
async def start_chat(request: ChatRequest):
    """
    Starts Agno Agent run.

    Supports:
    ✅ Normal response
    ✅ Tool calling
    ✅ Pause + human approval
    ✅ Stores running tasks
    """

    try:
        # -----------------------------------
        # 1. Create async task for agent run
        # -----------------------------------

        task = asyncio.create_task(CNCAgent.arun(input=request.user_input, user_id=""))

        # -----------------------------------
        # 2. Wait for agent result
        # -----------------------------------

        run = await task

        # -----------------------------------
        # 3. Save task reference
        # -----------------------------------

        RUN_TASKS[run.run_id] = task

        # -----------------------------------
        # 4. Handle Pause Case
        # -----------------------------------

        if run.status.name == "paused":
            tool_exec = run.requirements[0].tool_execution

            # Store paused run
            PAUSED_RUNS[run.run_id] = run

            return {
                "status": "paused",
                "run_id": run.run_id,
                "message": "Tool execution requires approval.",
                "action": {
                    "tool_name": tool_exec.tool_name,
                    "args": tool_exec.tool_args,
                },
                "data": None,
            }

        # -----------------------------------
        # 5. Handle Completed Case
        # -----------------------------------

        if run.status.name == "completed":
            assistant_message = run.content
            payload_data = None

            # If tool executed → parse output
            if run.tools:
                last_tool = run.tools[-1]
                raw_result = last_tool.result

                try:
                    parsed = json.loads(raw_result)

                    assistant_message = parsed.get("message", assistant_message)
                    payload_data = parsed.get("data", None)

                except Exception:
                    assistant_message = raw_result or assistant_message

            return {
                "status": "success",
                "run_id": run.run_id,
                "message": assistant_message,
                "action": None,
                "data": payload_data,
            }

        # -----------------------------------
        # 6. Unexpected Status
        # -----------------------------------

        return {
            "status": "error",
            "run_id": run.run_id,
            "message": f"Unexpected run status: {run.status.name}",
            "action": None,
            "data": None,
        }

    except Exception as e:
        return {
            "status": "error",
            "run_id": None,
            "message": str(e),
            "action": None,
            "data": None,
        }


# --------------------------------------------------
# STOP Endpoint
# --------------------------------------------------


@agno_router.post("/stop")
async def stop_agent(request: StopRequest):
    """
    Stops an agent run when user clicks Pause/Stop.

    Cancels:
    ✅ Running tasks
    ✅ Paused runs
    """

    run_id = request.run_id

    # -----------------------------------
    # 1. Cancel Running Task
    # -----------------------------------

    if run_id in RUN_TASKS:
        task = RUN_TASKS[run_id]

        if not task.done():
            task.cancel()

        del RUN_TASKS[run_id]

        return {
            "status": "stopped",
            "run_id": run_id,
            "message": "Agent execution stopped successfully.",
            "action": None,
            "data": None,
        }

    # -----------------------------------
    # 2. Remove Paused Run
    # -----------------------------------

    if run_id in PAUSED_RUNS:
        del PAUSED_RUNS[run_id]

        return {
            "status": "stopped",
            "run_id": run_id,
            "message": "Paused agent run cleared successfully.",
            "action": None,
            "data": None,
        }

    # -----------------------------------
    # 3. Run Not Found
    # -----------------------------------

    return {
        "status": "error",
        "run_id": run_id,
        "message": "Run ID not found or already completed.",
        "action": None,
        "data": None,
    }


@agno_router.post("/resume")
async def resume_chat(request: ResumeRequest):
    run = RUN_STORE.get(request.run_id)

    if not run:
        return {"error": "Invalid or expired run_id"}

    te = run.requirements[0].tool_execution

    decision = await handle_purchase_resume(
        state=request.details,
        tool_name=te.tool_name,
        user_response=request.response,
    )

    state = {"details": request.details}

    if decision["type"] == "END":
        del RUN_STORE[request.run_id]
        return {"type": "RESUMED", "response": decision["message"]}

    te.confirmed = True
    te.confirmation_note = "Approved via API"

    final = CNCAgent.acontinue_run(run_response=run)

    del RUN_STORE[request.run_id]

    return {
        "type": "RESUMED",
        "response": final.content,
    }
