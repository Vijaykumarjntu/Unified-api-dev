import httpx
from typing import List
from datetime import datetime
from .base import BaseAdapter
from ..models import Contact

class GitHubAdapter(BaseAdapter):
    """GitHub API adapter - gets users/stars as "contacts" """
    
    @property
    def provider_name(self) -> str:
        return "github"
    
    async def get_contacts(self) -> List[Contact]:
        """Get user's starred repos as contact list"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/starred",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            repos = response.json()
            
            # Normalize GitHub data to our Contact shape
            contacts = []
            for repo in repos[:20]:  # Limit for demo
                contacts.append(Contact(
                    id=str(repo['id']),
                    email=f"{repo['name']}@github.demo",  # GitHub doesn't have emails for starred repos
                    firstName=repo['name'],
                    lastName=repo['owner']['login'],
                    createdAt=datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00')),
                    provider=self.provider_name
                ))
            return contacts
    
    async def create_contact(self, email: str, first_name: str = None, last_name: str = None) -> Contact:
        """Star a repo - simplified as 'create contact'"""
        # For demo, we'll just return a mock
        return Contact(
            id="mock_123",
            email=email,
            firstName=first_name,
            lastName=last_name,
            createdAt=datetime.now(),
            provider=self.provider_name
        )