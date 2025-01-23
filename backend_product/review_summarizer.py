from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReviewSummary:
    """Structured format for review summaries"""
    overall_sentiment: str
    purchase_intent_percentage: float
    confidence_score: float
    key_strengths: List[str]
    key_concerns: List[str]
    demographic_insights: Dict[str, str]
    common_themes: List[str]
    recommendation: str
    detailed_summary: str

    @classmethod
    def from_json(cls, json_str: str) -> 'ReviewSummary':
        try:
            print(json_str)
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
            overall_sentiment="Neutral",
            purchase_intent_percentage=0.0,
            confidence_score=0.0,
            key_strengths=["Unable to parse review"],
            key_concerns=["Unable to parse review"],
            demographic_insights={"error": "Unable to parse review"},
            common_themes=["Unable to parse review"],
            recommendation="Unable to generate recommendation due to parsing error",
            detailed_summary="Unable to generate summary due to parsing error"
        )

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.__dict__, indent=2)


def _create_summary_prompt(reviews: List[str], product_info: Optional[Dict] = None) -> str:
    """Creates prompt requesting JSON format"""
    product_context = ""
    if product_info:
        product_context = (
            "Product Context:\n"
            f"Name: {product_info.get('name', 'N/A')}\n"
            f"Description: {product_info.get('description', 'N/A')}\n"
            f"Price: {product_info.get('price', 'N/A')}\n"
            f"Category: {product_info.get('category', 'N/A')}\n"
        )

    # Format reviews
    reviews_text = "\n\n".join([f"Review {i + 1}: {review}" for i, review in enumerate(reviews)])

    return f"""
        Analyze these product reviews and provide insights as a JSON object in the exact format below. Your response must be strict JSON without additional text or comments.
        - Your response contains no duplicate keys.
        - It adheres strictly to the provided JSON format.
        product details:
        {product_context}

        Personas and Reviews:
        {reviews_text}

        Required JSON format:
        {{
            "overall_sentiment": "string (e.g., Very Positive, Positive, Neutral, Negative, Very Negative)",
            "purchase_intent_percentage": float (0-100),
            "confidence_score": float (0-100),
            "key_strengths": ["List of 3-5 main strengths"],
            "key_concerns": ["List of 3-5 main concerns"],
            "demographic_insights": {{
                "profession_based": "e.g., Engineers liked the product for its durability",
                "age_based": "e.g., Popular among users aged 25-34",
                "nationality_based": "e.g., Preferred by users in North America"
            }},
            "common_themes": ["List of 4-6 recurring themes"],
            "recommendation": "e.g., This product is recommended for...",
            "detailed_summary": "2-3 paragraphs with a natural summary"
        }}
        Ensure that your output is strictly valid JSON. Do not include any additional commentary.
        """


class ReviewSummarizer:
    """Summarizes the all the review given by the agents """
    def __init__(self, api_key: str):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.2,
            google_api_key=api_key
        )

    async def summarize_reviews(self,reviews: List[str],product_info: Optional[Dict] = None ) -> ReviewSummary:
        messages = [
            SystemMessage(
                content="You are a professional review analyst. Your task is to provide a comprehensive and insightful"
                        "summary of the given product reviews. Follow the structure provided and ensure your response "
                        "is strictly in JSON format. Be precise, clear, and include actionable insights while "
                        "adhering to the required output format."),
            HumanMessage(content=_create_summary_prompt(reviews, product_info))
        ]
        try:
            response = self.model.invoke(messages)
            logger.debug(f"Raw AI response: {response.content}")
            return ReviewSummary.from_json(response.content)
        except Exception as e:
            logger.error(f"Error in summarize_reviews: {str(e)}")
            # Return a default summary instead of raising an exception
            return ReviewSummary(
                overall_sentiment="Neutral",
                purchase_intent_percentage=0.0,
                confidence_score=0.0,
                key_strengths=["Error processing review"],
                key_concerns=["Error processing review"],
                demographic_insights={"error": "Processing failed"},
                common_themes=["Error processing review"],
                recommendation="Unable to generate recommendation due to processing error",
                detailed_summary=f"Error occurred while processing reviews: {str(e)}"
            )