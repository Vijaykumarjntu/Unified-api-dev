from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from ..adapters.github import GitHubAdapter
from ..adapters.slack import SlackAdapter
from ..models import Contact, APIResponse

router = APIRouter(tags=["contacts"])

# Factory to get the right adapter
def get_adapter(provider: str, access_token: str):
    adapters = {
        "github": GitHubAdapter,
        "slack": SlackAdapter,
    }
    
    if provider not in adapters:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}. Supported: github, slack")
    
    return adapters[provider](access_token)


@router.get("/contacts")
async def get_contacts(
    provider: str = Query(..., description="Provider: github or slack"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Get contacts from a provider.
    
    - **provider**: github or slack
    - **Authorization**: Bearer token from OAuth
    """
    
    # Check authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Extract token (remove "Bearer " prefix)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")
    
    try:
        # Get adapter and fetch contacts
        adapter = get_adapter(provider, token)
        contacts = await adapter.get_contacts()
        
        return APIResponse(
            success=True,
            data=contacts,
            provider=provider
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch contacts from {provider}: {str(e)}"
        )


@router.post("/contacts")
async def create_contact(
    provider: str = Query(..., description="Provider: github or slack"),
    email: str = Query(..., description="Email address"),
    first_name: Optional[str] = Query(None, description="First name"),
    last_name: Optional[str] = Query(None, description="Last name"),
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Create a contact in a provider.
    
    For GitHub: "stars" a repository (email format: owner/repo)
    For Slack: Not supported (returns mock)
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        adapter = get_adapter(provider, token)
        contact = await adapter.create_contact(email, first_name, last_name)
        
        return APIResponse(
            success=True,
            data=contact,
            provider=provider
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create contact in {provider}: {str(e)}"
        )


@router.get("/contacts/all")
async def get_all_contacts(
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Get contacts from ALL configured providers at once.
    Requires tokens for all providers to be passed.
    
    Authorization header should contain comma-separated: "github:token1,slack:token2"
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # Parse multi-provider token format: "github:token123,slack:token456"
    tokens = {}
    for item in authorization.split(","):
        if ":" in item:
            provider, token = item.split(":", 1)
            tokens[provider.strip()] = token.strip()
    
    results = {}
    errors = {}
    
    for provider, token in tokens.items():
        try:
            adapter = get_adapter(provider, token)
            contacts = await adapter.get_contacts()
            results[provider] = contacts
        except Exception as e:
            errors[provider] = str(e)
    
    return {
        "success": True,
        "data": results,
        "errors": errors if errors else None
    }