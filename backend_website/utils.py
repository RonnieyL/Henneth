from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime


class AIProvider(str, Enum):
    """Supported AI providers for website analysis"""
    GEMINI = "gemini"
    OPENAI = "openai"

@dataclass
class VisualAnalysis:
    view_type: str
    analysis: str


@dataclass
class WebsiteAnalysisOutput:
    url: str
    timestamp: str
    visual_analyses: List[VisualAnalysis]
    content_analysis: str

@dataclass
class ReviewerProfile:
    """Represents the web analyzer's profile and expertise."""
    profession: str
    specialization: str = "web development"
    age : int = 30
    years_experience: int = 5
    expertise_areas: List[str] = None
    analysis_priorities: List[str] = None
    technical_skills: List[str] = None
    industry_focus: str = "general"

    def __post_init__(self):
        """Initialize default values for lists"""
        if self.expertise_areas is None:
            self.expertise_areas = ["UX/UI", "Performance", "SEO", "Accessibility"]
        if self.analysis_priorities is None:
            self.analysis_priorities = ["user experience", "performance", "accessibility", "content quality"]
        if self.technical_skills is None:
            self.technical_skills = ["HTML", "CSS", "JavaScript", "Web Performance", "SEO"]


class AnalysisSession:
    """Class to manage a website analysis session's results"""
    def __init__(self):
        self.url: str = ""
        self.timestamp: str = datetime.now().isoformat()
        self.visual_analyses: List[Dict[str, str]] = []
        self.content_analysis: Optional[str] = None

    def update_analysis(self, url: str, visual_analyses: List[Dict[str, str]], content_analysis: str):
        """Update the analysis results"""
        self.url = url
        self.visual_analyses = visual_analyses
        self.content_analysis = content_analysis
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert session to dictionary format matching scraper output"""
        return {
            "url": self.url,
            "timestamp": self.timestamp,
            "visual_analyses": self.visual_analyses,
            "content_analysis": self.content_analysis
        }