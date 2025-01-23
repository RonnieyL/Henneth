from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


@dataclass
class WebsiteAnalysisSummary:
    """Structured format for website analysis summaries"""
    overall_assessment: str
    usability_score: float
    confidence_score: float
    key_strengths: List[str]
    key_issues: List[str]
    technical_insights: Dict[str, str]
    user_experience_themes: List[str]
    recommendations: List[str]
    detailed_summary: str

    @classmethod
    def from_json(cls, json_str: str) -> 'WebsiteAnalysisSummary':
        try:
            start_index = json_str.find('{')
            json_string = json_str[start_index:]
            decoder = json.JSONDecoder()
            data, _ = decoder.raw_decode(json_string)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON is not a dictionary.")
            return cls(**data)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Content: {json_str}")
        except Exception as e:
            logger.error(f"Error parsing JSON: {e} - Content: {json_str}")
        return cls(
            overall_assessment="Neutral",
            usability_score=0.0,
            confidence_score=0.0,
            key_strengths=["Unable to parse analysis"],
            key_issues=["Unable to parse analysis"],
            technical_insights={"error": "Unable to parse analysis"},
            user_experience_themes=["Unable to parse analysis"],
            recommendations=["Unable to generate recommendations"],
            detailed_summary="Unable to generate summary due to parsing error"
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.__dict__, indent=2)


def _create_summary_prompt(analyses: List[str], website_info: Optional[Dict] = None) -> str:
    """Creates prompt requesting JSON format"""
    website_context = ""
    if website_info:
        website_context = (
            "Website Context:\n"
            f"URL: {website_info.get('url', 'N/A')}\n"
            f"Purpose: {website_info.get('purpose', 'N/A')}\n"
            f"Category: {website_info.get('category', 'N/A')}\n"
        )

    # Format analyses
    analyses_text = "\n\n".join([f"Analysis {i + 1}: {analysis}" for i, analysis in enumerate(analyses)])

    return f"""
        Analyze these website analyses and provide insights as a JSON object in the exact format below. 
        Your response must be strict JSON without additional text or comments.

        Website details:
        {website_context}

        Analyses and Reviews:
        {analyses_text}

        Required JSON format:
        {{
            "overall_assessment": "string (e.g., Excellent, Good, Average, Needs Improvement, Poor)",
            "usability_score": float (0-100),
            "confidence_score": float (0-100),
            "key_strengths": ["List of 3-5 main strengths"],
            "key_issues": ["List of 3-5 main issues"],
            "technical_insights": {{
                "performance": "e.g., Fast loading times with optimized images",
                "accessibility": "e.g., Good ARIA implementation but needs color contrast improvements",
                "seo": "e.g., Well-structured content with proper meta tags"
            }},
            "user_experience_themes": ["List of 4-6 recurring UX observations"],
            "recommendations": ["List of 3-5 actionable improvements"],
            "detailed_summary": "2-3 paragraphs with a comprehensive analysis"
        }}
        Ensure that your output is strictly valid JSON. Do not include any additional commentary.
        """


class WebsiteAnalysisSummarizer:
    """Summarizes multiple website analyses into a comprehensive report"""

    def __init__(self, api_key: str):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.2,
            google_api_key=api_key
        )

    async def summarize_analyses(self, analyses: List[str],
                                 website_info: Optional[Dict] = None) -> WebsiteAnalysisSummary:
        messages = [
            SystemMessage(
                content="You are a professional website analyst. Your task is to provide a comprehensive and insightful"
                        "summary of the given website analyses. Follow the structure provided and ensure your response "
                        "is strictly in JSON format. Focus on technical aspects, user experience, and actionable insights."
            ),
            HumanMessage(content=_create_summary_prompt(analyses, website_info))
        ]
        try:
            response = self.model.invoke(messages)
            logger.debug(f"Raw AI response: {response.content}")
            return WebsiteAnalysisSummary.from_json(response.content)
        except Exception as e:
            logger.error(f"Error in summarize_analyses: {str(e)}")
            return WebsiteAnalysisSummary(
                overall_assessment="Neutral",
                usability_score=0.0,
                confidence_score=0.0,
                key_strengths=["Error processing analysis"],
                key_issues=["Error processing analysis"],
                technical_insights={"error": "Processing failed"},
                user_experience_themes=["Error processing analysis"],
                recommendations=["Unable to generate recommendations"],
                detailed_summary=f"Error occurred while processing analyses: {str(e)}"
            )