from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    """
    A class representing the product with its details
    """
    name: str
    price: str
    description: str
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    unique_features: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """
        Create a Product instance from a dictionary .
        """
        return cls(
            name=data['name'],
            price=data['price'],
            description=data['description'],
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            unique_features=data.get('unique_features', [])
        )

    def to_review_format(self) -> str:
        """
        Convert product information to the format expected by the product reviewer.
        """
        base_info = f"""Review this product: {self.name}
        {self.description} price: {self.price}"""

        optional_sections = []

        if self.strengths:
            strengths_text = "\n".join(self.strengths)
            optional_sections.append(f"\n\nStrengths:\n{strengths_text}")

        if self.weaknesses:
            weaknesses_text = "\n".join(self.weaknesses)
            optional_sections.append(f"\n\nWeaknesses:\n{weaknesses_text}")

        if self.unique_features:
            uniqueness_text = "\n".join(self.unique_features)
            optional_sections.append(f"\n\nUniqueness:\n{uniqueness_text}")

        return base_info + "".join(optional_sections)

