import httpx
from typing import List
from datetime import datetime
from .base import BaseAdapter
from ..models import Contact
import os

class SlackAdapter(BaseAdapter):
    
    @property
    def provider_name(self) -> str:
        return "slack"
    
    async def get_contacts(self) -> List[Contact]:
        """Fetch Slack users using bot token"""
        
        # Use bot token (not user token for better permissions)
        token = os.getenv("SLACK_BOT_TOKEN")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://slack.com/api/users.list",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            data = response.json()
            
            if not data.get('ok'):
                print(f"Slack error: {data.get('error')}")
                return self._get_mock_contacts()
            
            contacts = []
            for user in data.get('members', []):
                if user.get('deleted') or user.get('is_bot'):
                    continue
                
                profile = user.get('profile', {})
                contacts.append(Contact(
                    id=user['id'],
                    email=profile.get('email', f"{user['id']}@slack.demo"),
                    firstName=profile.get('first_name'),
                    lastName=profile.get('last_name'),
                    createdAt=datetime.fromtimestamp(float(user.get('updated', 0))),
                    provider=self.provider_name
                ))
            
            return contacts
    
    def _get_mock_contacts(self) -> List[Contact]:
        """Fallback mock data"""
        return [
            Contact(
                id="U123",
                email="you@yourworkspace.slack.com",
                firstName="Slack",
                lastName="User",
                createdAt=datetime.now(),
                provider=self.provider_name
            )
        ]
    
    async def create_contact(self, email: str, first_name: str = None, last_name: str = None) -> Contact:
        """Slack doesn't support user creation via API"""
        return Contact(
            id="mock_slack",
            email=email,
            firstName=first_name,
            lastName=last_name,
            createdAt=datetime.now(),
            provider=self.provider_name
        )