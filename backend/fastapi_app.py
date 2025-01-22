from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from manager import Manager, ReviewConfiguration
from persona_selector import PersonaSelectionCriteria
from product import Product
from summary_parser import Summary_parser
import asyncio

# Define the FastAPI app
app = FastAPI()

# Pydantic models for request validation
class ProductInput(BaseModel):
    name: str
    price: str
    description: str
    strengths: list[str]
    weaknesses: list[str]
    unique_features: list[str]

class PersonaCriteriaInput(BaseModel):
    age_range: tuple[int, int]
    professions: list[str]
    min_matching_hobbies: int

class ReviewConfigInput(BaseModel):
    persona_criteria: PersonaCriteriaInput
    num_personas: int
    ai_provider: str
    api_key: str

class ReviewRequest(BaseModel):
    product: ProductInput
    config: ReviewConfigInput

# FastAPI route
@app.post("/generate-reviews")
async def generate_reviews(request: ReviewRequest):
    try:
        # Initialize the manager
        manager = Manager(
            persona_data_path="sample_personas.xlsx",
            summarizer_api_key="" ### enter api key here
        )

        # Prepare configuration and product
        config = ReviewConfiguration(
            persona_criteria=PersonaSelectionCriteria(
                age_range=request.config.persona_criteria.age_range,
                professions=request.config.persona_criteria.professions,
                min_matching_hobbies=request.config.persona_criteria.min_matching_hobbies
            ),
            num_personas=request.config.num_personas,
            ai_provider=request.config.ai_provider,
            api_key=request.config.api_key
        )

        product = Product(
            name=request.product.name,
            price=request.product.price,
            description=request.product.description,
            strengths=request.product.strengths,
            weaknesses=request.product.weaknesses,
            unique_features=request.product.unique_features
        )

        # Generate product reviews
        results = await manager.generate_product_reviews(product, config)

        # Parse the results
        parser = Summary_parser()
        parsed_summary = parser.parse(data=results)

        # Return the parsed summary
        return {"success": True, "reviews": parsed_summary}

    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))
