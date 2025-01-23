from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class AIProvider(str, Enum):
    """we will be supporting two AI providers for now google and openai"""
    """
    thinking about adding cohere and claude too later cohere because its cheap and claude because its responses are better
    """
    GEMINI = "gemini"
    OPENAI = "openai"


@dataclass
class ReviewerProfile:
    """Represents the reviewer's profile information."""
    profession: str
    age: int = 30
    nationality: str = ""
    salary_range: str = ""
    priorities: str = "practicality, comfort, long-term value"
    hobbies: str = ""
    constraints: str = ""


class ReviewSession:
    """Class to manage a review session"""
    def __init__(self):
        self.messages: List[dict] = []
        self.final_review: Optional[str] = None
        self.confidence_score: float = 0.0

    def add_message(self, role: str, content: str):
        """Add a message to the session history"""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': self._get_timestamp()
        })

    @staticmethod
    def _get_timestamp():
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


