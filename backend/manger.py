from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from product import Product
from persona_selector import PersonaSelector, PersonaSelectionCriteria
from product_reviewer import ProductReviewer
from review_summarizer import ReviewSummarizer
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ReviewConfiguration:
    """Configuration for review generation process"""
    persona_criteria: PersonaSelectionCriteria
    num_personas: int
    ai_provider: str
    api_key: str
    model_config: Optional[Dict[str, Any]] = None
    randomize_if_insufficient: bool = True


class Manager:
    """
    manages the entire review generation and summarization process
    """
    def __init__(
            self,
            persona_data_path: str,
            summarizer_api_key: str
    ):
        """
        Initialize ReviewManager with required components
        """
        self.persona_selector = PersonaSelector(persona_data_path)
        self.summarizer = ReviewSummarizer(summarizer_api_key)

    async def generate_product_reviews(self,product: Product,config: ReviewConfiguration) -> Dict[str, Any]:
        """
        Generate and summarize reviews for a product
        """
        try:
            selected_personas = self.persona_selector.get_selected_personas(
                criteria=config.persona_criteria,
                num_personas=config.num_personas,
                randomize_if_insufficient=config.randomize_if_insufficient
            )

            logger.info(f"Selected {len(selected_personas)} personas for review generation")
            #logger is there for debugging
            reviewer = ProductReviewer(
                provider=config.ai_provider,
                api_key=config.api_key,
                model_config=config.model_config
            )
            reviews = []
            for persona in selected_personas:
                try:
                    review_session = reviewer.generate_review(
                        product=product,
                        profile=persona.to_reviewer_profile()
                    )

                    reviews.append({
                        'persona': {
                            'name': persona.name,
                            'age': persona.age,
                            'profession': persona.profession,
                            'nationality': persona.nationality,
                            'salary_range': persona.salary_range,
                            'hobbies': persona.hobbies,
                            'priorities': persona.priorities
                        },
                        'review': review_session.final_review,
                        'timestamp': review_session.messages[-1]['timestamp'] if review_session.messages else None
                    })

                except Exception as e:
                    logger.error(f"Error generating review for persona {persona.name}: {str(e)}")
                    continue

            product_info = {
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': getattr(product, 'category', 'N/A')
            }

            review_texts = [r['review'] for r in reviews]
            summary = await self.summarizer.summarize_reviews(
                reviews=review_texts,
                product_info=product_info
            )

            return {
                'product': product_info,
                'summary': summary,
                'metadata': {
                    'total_personas': len(selected_personas),
                    'successful_reviews': len(reviews),
                    'ai_provider': config.ai_provider
                }
            }

        except Exception as e:
            logger.error(f"Error in review generation process: {str(e)}")
            raise

    def get_available_persona_criteria(self) -> Dict[str, List]:
        """
        Get available criterion for persona selection
        """
        return self.persona_selector.get_unique_values()