from abc import ABC, abstractmethod
from typing import List
from ..models import Contact

class BaseAdapter(ABC):
    """Base class for all provider adapters"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
    
    @abstractmethod
    async def get_contacts(self) -> List[Contact]:
        """Fetch and normalize contacts from provider"""
        pass
    
    @abstractmethod
    async def create_contact(self, email: str, first_name: str = None, last_name: str = None) -> Contact:
        """Create a contact in provider"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass