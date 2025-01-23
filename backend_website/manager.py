from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from website import Website
from persona_selector import WebsitePersonaSelector, WebsitePersonaSelectionCriteria
from website_reviewer import WebsiteReviewer
from review_summarizer import WebsiteAnalysisSummarizer
from scraper import WebsiteAnalyzer
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebsiteReviewConfiguration:
    """Configuration for website review generation process"""
    persona_criteria: WebsitePersonaSelectionCriteria
    num_personas: int
    ai_provider: str
    reviewer_api_key: str
    model_config: Optional[Dict[str, Any]] = None
    randomize_if_insufficient: bool = True


class WebsiteManager:
    """
    Manages the entire website analysis pipeline from scraping to review generation
    """

    def __init__(
            self,
            persona_data_path: str,
            summarizer_api_key: str,
            scraper_api_key: str
    ):
        """
        Initialize WebsiteManager with required components

        Args:
            persona_data_path: Path to Excel file containing reviewer personas
            summarizer_api_key: API key for the summarizer service
            scraper_api_key: API key for the website scraper (Gemini)
        """
        self.persona_selector = WebsitePersonaSelector(persona_data_path)
        self.summarizer = WebsiteAnalysisSummarizer(summarizer_api_key)
        self.scraper = WebsiteAnalyzer(scraper_api_key)

    async def analyze_website(self, url: str, config: WebsiteReviewConfiguration) -> Dict[str, Any]:
        """
        Complete website analysis pipeline:
        1. Scrape website data
        2. Generate reviews from multiple personas
        3. Summarize all analyses

        Args:
            url: Website URL to analyze
            config: Configuration for the analysis process
        """
        try:
            # Step 1: Scrape website data
            logger.info(f"Starting website analysis for: {url}")
            scrape_result = await self.scraper.analyze_website(url)

            # Create Website object from scrape results
            website = Website.from_dict({
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'visual_analyses': [
                    {'view_type': analysis.view_type, 'analysis': analysis.analysis}
                    for analysis in scrape_result.visual_analyses
                ],
                'content_analysis': scrape_result.content_analysis
            })

            # Step 2: Get reviewer personas
            selected_personas = self.persona_selector.get_selected_personas(
                criteria=config.persona_criteria,
                num_personas=config.num_personas,
                randomize_if_insufficient=config.randomize_if_insufficient
            )

            logger.info(f"Selected {len(selected_personas)} personas for website analysis")

            # Step 3: Generate reviews from each persona
            reviewer = WebsiteReviewer(
                provider=config.ai_provider,
                api_key=config.reviewer_api_key,
                model_config=config.model_config
            )

            analyses = []
            for persona in selected_personas:
                try:
                    # Convert scraped data to review format
                    website_content = website

                    analysis_session = await reviewer.generate_review(
                        url=url,
                        profile=persona,
                        website=website_content
                    )

                    analyses.append({
                        'persona': {
                            'profession': persona.profession,
                            'specialization': persona.specialization,
                            'years_experience': persona.years_experience,
                            'expertise_areas': persona.expertise_areas,
                            'industry_focus': persona.industry_focus
                        },
                        'analysis': analysis_session.content_analysis,
                        'timestamp': analysis_session.timestamp
                    })

                except Exception as e:
                    logger.error(f"Error generating analysis for persona {persona.profession}: {str(e)}")
                    continue

            # Step 4: Summarize all analyses
            website_info = {
                'url': url,
                'category': getattr(website, 'category', 'N/A')
            }

            analysis_texts = [a['analysis'] for a in analyses]
            summary = await self.summarizer.summarize_analyses(
                analyses=analysis_texts,
                website_info=website_info
            )

            return {
                'website': website_info,
                'scrape_data': {
                    'visual_analyses': website.visual_analyses,
                    'content_analysis': website.content_analysis
                },
                'summary': summary,
                'metadata': {
                    'total_personas': len(selected_personas),
                    'successful_analyses': len(analyses),
                    'ai_provider': config.ai_provider
                }
            }

        except Exception as e:
            logger.error(f"Error in website analysis process: {str(e)}")
            raise

    def get_available_persona_criteria(self) -> Dict[str, List]:
        """
        Get available criteria for persona selection
        """
        return self.persona_selector.get_unique_values()


# Example usage:
