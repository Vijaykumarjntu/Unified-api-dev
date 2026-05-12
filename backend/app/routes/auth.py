# backend/app/routes/auth.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import os
from typing import Dict
import secrets
import uuid

router = APIRouter(tags=["auth"])

# In-memory token store (use Redis/DB in production)
token_store: Dict[str, Dict] = {}

class OAuthResponse(BaseModel):
    success: bool
    auth_url: str | None = None
    access_token: str | None = None
    error: str | None = None



@router.get("/auth/slack/login")
async def slack_login():
    """Slack OAuth URL redirect"""
    client_id = os.getenv("SLACK_CLIENT_ID")
    redirect_uri = "http://localhost:8000/api/v1/auth/slack/callback"
    
    auth_url = f"https://slack.com/oauth/v2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=users:read,users:read.email"
    
    return OAuthResponse(success=True, auth_url=auth_url)

@router.get("/auth/slack/callback")
async def slack_callback(code: str):
    """Exchange code for Slack token"""
    client_id = os.getenv("SLACK_CLIENT_ID")
    client_secret = os.getenv("SLACK_CLIENT_SECRET")
    print("just before the call")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": "http://localhost:8000/api/v1/auth/slack/callback"
            }
        )
        
        token_data = response.json()
        print("we got the token data of the slack")
        if not token_data.get('ok'):
            print("if block working")
            raise HTTPException(status_code=400, detail=token_data.get('error'))
        
        access_token = token_data.get('access_token') or token_data.get('bot_token')
        print("we got the access token too")
        # IMPORTANT: Redirect to frontend with token in URL
        frontend_url = f"http://localhost:3000?provider=slack&token={access_token}"
        
        return RedirectResponse(url=frontend_url)
        # return OAuthResponse(success=True, access_token=access_token)

@router.get("/auth/{provider}/login")
async def login(provider: str):
    """Get REAL GitHub OAuth URL"""
    
    if provider != "github":
        # For now, only GitHub works. Slack/Notion coming next.
        return OAuthResponse(success=False, error=f"{provider} not implemented yet")
    
    # GitHub OAuth URL
    client_id = os.getenv("GITHUB_CLIENT_ID")
    redirect_uri = "http://localhost:8000/api/v1/auth/github/callback"
    
    if not client_id:
        return OAuthResponse(success=False, error="GitHub Client ID not configured")
    
    auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=repo,user"
    
    return OAuthResponse(success=True, auth_url=auth_url)

@router.get("/auth/{provider}/callback")
async def callback(provider: str, code: str, request: Request):
    """Exchange code for access token with REAL GitHub"""
    
    if provider != "github":
        raise HTTPException(status_code=400, detail=f"{provider} not implemented")
    
    client_id = os.getenv("GITHUB_CLIENT_ID")
    client_secret = os.getenv("GITHUB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="GitHub credentials missing")
    
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": "http://localhost:8000/api/v1/auth/github/callback"
            },
            headers={"Accept": "application/json"}
        )
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        access_token = token_data["access_token"]
        
        # Store token (in production, associate with user session)
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        token_store[user_id] = {
            "provider": provider,
            "access_token": access_token,
            "user_id": user_id
        }
        
        # In a real app, you'd redirect back to frontend with user_id
        # For simplicity, we'll just return the token
        return OAuthResponse(success=True, access_token=access_token)
