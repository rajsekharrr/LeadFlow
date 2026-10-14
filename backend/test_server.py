"""
Minimal FastAPI app to test uvicorn server startup.

This is a temporary test file - the actual app will be created in Step 7.
"""
from fastapi import FastAPI

app = FastAPI(title="LeadFlow API - Setup Test")

@app.get("/")
def root():
    return {"status": "Backend setup complete", "step": 2}

@app.get("/health")
def health():
    return {"status": "ok"}
