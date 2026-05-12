from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

# Unified contact schema - YOUR API's shape
class Contact(BaseModel):
    id: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    createdAt: datetime
    provider: Literal['github', 'slack', 'notion']

# OAuth token storage (in-memory for now)
class OAuthToken(BaseModel):
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    user_id: str

# API response wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[list[Contact] | Contact] = None
    error: Optional[str] = None
    provider: Optional[str] = None