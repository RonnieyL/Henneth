from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebsiteAnalysisParser:
    """Parser for converting website analysis data into formatted string output"""

    def __init__(self):
        """Initialize the analysis parser"""
        pass

    def parse(self, data: Dict[str, Any]) -> str:
        """
        Parse the analysis data and return a formatted string

        Args:
            data: Dictionary containing website info, summary data, and metadata

        Returns:
            Formatted string containing the parsed analysis
        """
        try:
            website = data.get('website', {})
            summary = data.get('summary', {})
            metadata = data.get('metadata', {})

            strengths_list = "\n".join(f"• {strength}" for strength in summary.key_strengths)
            issues_list = "\n".join(f"• {issue}" for issue in summary.key_issues)
            ux_themes_list = "\n".join(f"• {theme}" for theme in summary.user_experience_themes)
            recommendations_list = "\n".join(f"• {rec}" for rec in summary.recommendations)

            technical_insights = "\n".join(
                f"• {key.title()}: {value}"
                for key, value in summary.technical_insights.items()
            )

            return f"""
🌐 WEBSITE INFORMATION
URL: {website.get('url', 'N/A')}

📊 ANALYSIS SUMMARY
Overall Assessment: {summary.overall_assessment}
Usability Score: {summary.usability_score:.1f}/100
Confidence Score: {summary.confidence_score:.1f}%

💪 KEY STRENGTHS
{strengths_list}

⚠️ KEY ISSUES
{issues_list}

🔧 TECHNICAL INSIGHTS
{technical_insights}

👥 USER EXPERIENCE THEMES
{ux_themes_list}

💡 RECOMMENDATIONS
{recommendations_list}

📝 DETAILED SUMMARY
{summary.detailed_summary}

ℹ️ ANALYSIS METADATA
Total Personas: {metadata.get('total_personas', 0)}
Successful Analyses: {metadata.get('successful_analyses', 0)}
AI Provider: {metadata.get('ai_provider', 'N/A')}
"""

        except Exception as e:
            logger.error(f"Error parsing analysis: {str(e)}")
            return f"Error parsing analysis: {str(e)}"