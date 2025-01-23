from typing import TypedDict, List, Optional, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import logging
from website import Website
from utils import AIProvider, ReviewerProfile, AnalysisSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: List[AIMessage | HumanMessage | SystemMessage]


class WebsiteReviewer:
    """A class to handle website review generation using AI providers and web scraping."""

    def __init__(
            self,
            provider: AIProvider | str,
            api_key: str,
            model_config: Optional[dict] = None
    ):
        """Initialize the WebsiteReviewer."""
        self.provider = AIProvider(provider.lower())
        self.api_key = api_key
        self.model_config = model_config or {}
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the AI model based on the selected provider."""
        try:
            if self.provider == AIProvider.GEMINI:
                default_config = {
                    "model": "gemini-1.5-flash",
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
        return f"""You are an experienced web developer/designer working as a {profile.profession} 
        with {profile.years_experience} years of experience in {profile.specialization}.

        Your expertise includes: {', '.join(profile.expertise_areas)}
        Technical skills: {', '.join(profile.technical_skills)}
        Industry focus: {profile.industry_focus}

        When reviewing, analyze the provided visual and content analyses to evaluate:
        1. Design & Layout
        2. User Experience
        3. Content Quality
        4. Technical Implementation
        5. Recommendations for Improvement

        Format your response as:
        REVIEW: [Your detailed review with recommendations]"""

    def _process_message(self, messages: List[Any]) -> str:
        """Process messages and get AI response."""
        try:
            response = self.model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in processing message: {str(e)}")
            raise

    async def generate_review(
            self,
            url: str,
            profile: ReviewerProfile,
            website: Website
    ) -> AnalysisSession:
        """Generate a review for the given website URL using the provided profile."""
        session = AnalysisSession()

        messages = [
            SystemMessage(content=self._generate_system_prompt(profile)),
            HumanMessage(content=website.to_review_format())
        ]

        # Get AI review
        response = self._process_message(messages)
        session.update_analysis(url, website.visual_analyses, response)
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