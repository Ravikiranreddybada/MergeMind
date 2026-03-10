"""
FastAPI backend for the Bug‑to‑PR Autopilot
===========================================

This module exposes a minimal REST API to manage bug-to-PR runs.
It is intentionally lightweight and avoids external dependencies for
state persistence or SSE streaming. In a production deployment you
should replace the in‑memory RunService with an implementation that
uses Redis and Postgres, and use ``sse_starlette`` or another SSE
library to stream live events to the frontend.
"""

from __future__ import annotations

import asyncio
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from .services.runs import RunService

import os

app = FastAPI(title="MergeMind API", version="1.0.0")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
run_service = RunService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "services": {
            "backend": "running",
            "github": "connected" if run_service._runs else "idle"
        }
    }

@app.post("/runs")
async def create_run(payload: dict):
    """Create a new run"""
    issue_url = payload.get("issueUrl")
    repo = payload.get("repo")
    if not issue_url or not repo:
        raise HTTPException(status_code=400, detail="issueUrl and repo are required")
    run_id = await run_service.start(issue_url, repo)
    return {"runId": run_id}

@app.get("/runs")
async def list_runs():
    """List all runs"""
    runs = []
    for run_id, run in run_service._runs.items():
        runs.append({
            "runId": run_id,
            "issueUrl": run["issueUrl"],
            "repo": run["repo"],
            "status": run["status"]
        })
    return runs

@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get run details"""
    run = run_service._runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.get("/runs/{run_id}/events")
async def get_run_events(run_id: str):
    """Get run events as Server-Sent Events"""
    run = run_service._runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    q = run_service._event_queues.get(run_id)
    if not q:
        raise HTTPException(status_code=404, detail="Run events not found")
    
    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=30.0)
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive
                yield f"event: keepalive\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/runs/{run_id}/approve")
async def approve_run(run_id: str, body: dict):
    """Approve or reject a gate"""
    gate = body.get("gate")
    decision = body.get("decision")
    note = body.get("note", "")
    
    if gate is None or decision is None:
        raise HTTPException(status_code=400, detail="gate and decision are required")
    
    run = run_service._runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    await run_service.approve(run_id, gate, decision, note)
    return {"status": "success"}

