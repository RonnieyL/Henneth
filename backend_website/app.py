from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Tuple

from summary_parser import WebsiteAnalysisParser
from persona_selector import WebsitePersonaSelectionCriteria
from manager import WebsiteManager, WebsiteReviewConfiguration

app = FastAPI(title="Website Analysis API")

class WebsitePersonaCriteria(BaseModel):
    age_range: Tuple[int, int]
    expertise_areas: Optional[List[str]] = None
    experience_range: Optional[Tuple[int, int]] = None
    profession: Optional[List[str]] = None
    industry_focus: Optional[List[str]] = None

class WebsiteAnalysisRequest(BaseModel):
    url: HttpUrl
    age_range: Tuple[int, int] = (25, 45)
    expertise_areas: Optional[List[str]] = ["UX/UI", "Performance"]
    experience_range: Optional[Tuple[int, int]] = (3, 10)
    profession: Optional[List[str]] = ["Web Developer", "UX Designer"]
    industry_focus: Optional[List[str]] = ["E-commerce", "SaaS"]
    num_personas: int = 2
    ai_provider: str = "gemini"

@app.post("/analyze-website")
async def analyze_website(request: WebsiteAnalysisRequest):
    try:
        # Initialize manager with API keys
        manager = WebsiteManager(
            persona_data_path="website_reviewer_personas.xlsx",
            summarizer_api_key="gemini_api_key",
            scraper_api_key="gemini_api_key"
        )

        # Configure the analysis
        config = WebsiteReviewConfiguration(
            persona_criteria=WebsitePersonaSelectionCriteria(
                age_range=request.age_range,
                expertise_areas=request.expertise_areas,
                experience_range=request.experience_range,
                profession=request.profession,
                industry_focus=request.industry_focus
            ),
            num_personas=request.num_personas,
            ai_provider=request.ai_provider,
            reviewer_api_key="gemini_api_key"
        )

        # Run the analysis
        results = await manager.analyze_website(str(request.url), config)

        # Parse results
        parser = WebsiteAnalysisParser()
        parsed_results = parser.parse(data=results)

        return {
            "success": True,
            "results": parsed_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}