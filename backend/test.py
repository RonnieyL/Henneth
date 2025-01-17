from manger import Manager,ReviewConfiguration
from persona_selector import PersonaSelectionCriteria
from product import Product
from summary_parser import Summary_parser
import asyncio

async def main():
    manager = Manager(
        persona_data_path="sample_personas.xlsx",
        summarizer_api_key=""
    )
    config = ReviewConfiguration(
        persona_criteria=PersonaSelectionCriteria(
            age_range=(25, 35),
            professions=["Software engineer"],
            min_matching_hobbies=1
        ),
        num_personas=3,
        ai_provider="gemini",
        api_key=""
    )
    product = Product(
        name="HP 24mh FHD Computer Monitor",
        price="$179",
        description="The HP 24mh 23.8-inch FHD monitor combines stunning clarity, sleek design, and ergonomic comfort, perfect for both work and leisure. Its vibrant IPS display offers wide viewing angles and vivid visuals, while its slim profile and adjustable stand make it ideal for any workspace. Whether for productivity, entertainment, or gaming, this monitor delivers an exceptional experience.",
        strengths=[
            "Clear Full HD resolution with IPS technology for vibrant, true-to-life colors with 150hz refresh rate",
            "Slim, space-saving design with a micro-edge display for a sleek, modern look",
            "Fully adjustable stand with height, tilt, and swivel options for ergonomic comfort",
            "Low blue light mode reduces eye strain during extended use, ideal for long working hours",
            "Multiple connectivity options including HDMI, DisplayPort, and VGA for flexibility",
            "Built-in speakers offer decent sound quality for casual viewing without external speakers"
        ],
        weaknesses=[
            "Built-in speakers are sufficient for casual use but may not match the quality of external sound systems",
        ],
        unique_features=[
            "Ultra-slim design and micro-edge display for a seamless multi-monitor setup",
            "Low blue light filter to protect eyes during long hours of use",
            "Easily adjustable stand ensures personalized ergonomic viewing angles for enhanced comfort"
        ]
    )

    results = await manager.generate_product_reviews(product, config)
    parser = Summary_parser()
    print(parser.parse(data=results))

if __name__ == "__main__":
    asyncio.run(main())