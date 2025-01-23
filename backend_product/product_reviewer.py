from typing import TypedDict, List, Optional, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import logging
from product import Product
from utils import AIProvider, ReviewerProfile, ReviewSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: List[AIMessage | HumanMessage | SystemMessage]


class ProductReviewer:
    """
    A class to handle product review generation it makes API call using the provider given .
    """
    def __init__(
            self,
            provider: AIProvider | str,
            api_key: str,
            model_config: Optional[dict] = None
    ):
        """
        Initialize the ProductReviewer.
        provider: The AI provider to use ('gemini' or 'openai') may add cohere and claude later
        """
        self.provider = AIProvider(provider.lower())
        self.api_key = api_key
        self.model_config = model_config or {}
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the AI model based on the selected provider."""
        try:
            if self.provider.lower() == AIProvider.GEMINI:
                default_config = {
                    "model": "gemini-1.5-pro",
                    "temperature": 0.7,
                    "google_api_key": self.api_key
                }
                config = {**default_config, **self.model_config}
                self.model = ChatGoogleGenerativeAI(**config)
                logger.info("Successfully initialized Gemini model")

            elif self.provider == AIProvider.OPENAI:
                default_config = {
                    "model": "gpt-4o-mini",
                    "temperature": 0.7,
                    "openai_api_key": self.api_key
                }
                config = {**default_config, **self.model_config}
                self.model = ChatOpenAI(**config)
                logger.info("Successfully initialized OpenAI model")

        except Exception as e:
            logger.error(f"Error initializing {self.provider.value} model: {str(e)}")
            raise

    def _generate_system_prompt(self, profile: ReviewerProfile) -> str:
        """Generate system prompt for review generation."""
        return f"""You are an honest {profile.nationality.lower()} in his/her {profile.age}, a {profile.profession.lower()} 
        with an annual salary range of {profile.salary_range}.  
        You prioritize {profile.priorities} when assessing products, considering not just practicality and budget but also how 
        well the product fits into your personal interests, hobbies like {profile.hobbies}, and lifestyle.
        When reviewing, consider the product's strengths, weaknesses, uniqueness, and how it aligns with your daily routine 
        and personal constraints such as {profile.constraints}.
        Provide a comprehensive review with your purchase recommendation and include a confidence percentage.
        Format your response as:
        REVIEW: [Your detailed review with purchase recommendation and percentage]"""

    def _process_message(self, messages: List[Any]) -> dict:
        """Process messages and get AI response."""
        try:
            response = self.model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in processing message: {str(e)}")
            raise

    def _parse_ai_response(self, response: str) -> str:
        """Parse AI response to extract review content."""
        """plan to add hil part here later"""
        return response

    def generate_review(
            self,
            product: Product,
            profile: ReviewerProfile
    ) -> ReviewSession:
        """
        Generate a review for the given product using the prompt given.
        """
        session = ReviewSession()
        messages = [
            SystemMessage(content=self._generate_system_prompt(profile)),
            HumanMessage(content=product.to_review_format())
        ]

        # Get AI review later Hil will be added here
        response = self._process_message(messages)
        review_content = self._parse_ai_response(response)
        session.final_review = review_content
        session.add_message('ai', review_content)
        return session

    @property
    def provider_name(self) -> str:
        """Get the current provider name."""
        return self.provider.value

    def switch_provider(
            self,
            new_provider: AIProvider | str,
            new_api_key: str,
            new_model_config: Optional[dict] = None
    ) -> None:
        """Switch to a different AI provider."""
        self.provider = AIProvider(new_provider.lower())
        self.api_key = new_api_key
        self.model_config = new_model_config or {}
        self._initialize_model()
