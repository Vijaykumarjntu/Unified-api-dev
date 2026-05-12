from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime  # add at top
import os

load_dotenv()

app = FastAPI(title="Unified API", description="One API to rule all SaaS", version="0.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "Unified API",
        "version": "0.1.0",
        "endpoints": [
            "GET /health",
            "GET /api/v1/contacts",
            "GET /api/v1/auth/{provider}/login",
            "GET /api/v1/auth/{provider}/callback"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "OK", "timestamp": datetime.now().isoformat()}



# Import routes (we'll add these in Level 2)
# from .routes import contacts, auth
from .routes import auth
# app.include_router(contacts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)