from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Website:
    """
    A class representing a website with its analysis data from the scraper
    """
    url: str
    visual_analyses: List[Dict[str, str]]
    content_analysis: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Website':
        """
        Create a Website instance from a dictionary.
        """
        return cls(
            url=data['url'],
            visual_analyses=data['visual_analyses'],
            content_analysis=data['content_analysis']
        )

    def to_review_format(self) -> str:
        """
        Convert website information to the format expected by the website reviewer.
        """
        # Format visual analyses
        visual_analyses_text = "\n\n".join(
            f"{analysis['view_type']} Analysis:\n{analysis['analysis']}"
            for analysis in self.visual_analyses
        )

        return f"""Website Review Information:
        Content Analysis:
        {self.content_analysis}

        Visual Analyses:
        {visual_analyses_text}
        """