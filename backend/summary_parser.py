from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summary_parser:
    """Parser for converting review summary data into formatted string output"""

    def __init__(self):
        """Initialize the summary parser"""
        pass

    def parse(self, data: Dict[str, Any]) -> str:
        """
        Parse the summary data and return a formatted string

        Args:
            data: Dictionary containing product info, summary data, and metadata

        Returns:
            Formatted string containing the parsed summary
        """
        try:
            product = data.get('product', {})
            summary = data.get('summary', {})
            metadata = data.get('metadata', {})

            strengths_list = "\n".join(f"• {strength}" for strength in summary.key_strengths)
            concerns_list = "\n".join(f"• {concern}" for concern in summary.key_concerns)
            themes_list = "\n".join(f"• {theme}" for theme in summary.common_themes)

            return f"""
📦 PRODUCT INFORMATION
Name: {product.get('name', 'N/A')}
Price: {product.get('price', 'N/A')}
Category: {product.get('category', 'N/A')}

📊 REVIEW SUMMARY
Overall Sentiment: {summary.overall_sentiment}
Purchase Intent: {summary.purchase_intent_percentage:.1f}%
Confidence Score: {summary.confidence_score:.1f}%

💪 STRENGTHS
{strengths_list}

⚠️ CONCERNS
{concerns_list}

👥 DEMOGRAPHIC INSIGHTS
• Profession: {summary.demographic_insights.get('profession_based', 'N/A')}
• Age: {summary.demographic_insights.get('age_based', 'N/A')}
• Nationality: {summary.demographic_insights.get('nationality_based', 'N/A')}

🎯 COMMON THEMES
{themes_list}

💡 RECOMMENDATION
{summary.recommendation}

📝 DETAILED SUMMARY
{summary.detailed_summary}

ℹ️ ANALYSIS METADATA
Total Personas: {metadata.get('total_personas', 0)}
Successful Reviews: {metadata.get('successful_reviews', 0)}
AI Provider: {metadata.get('ai_provider', 'N/A')}
"""

        except Exception as e:
            logger.error(f"Error parsing summary: {str(e)}")
            return f"Error parsing summary: {str(e)}"