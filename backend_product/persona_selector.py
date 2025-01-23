import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import random
import logging
from product_reviewer import ReviewerProfile
from product import Product

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PersonaSelectionCriteria:
    """Class to hold the selection criteria for personas"""
    age_range: Optional[Tuple[int, int]] = None
    professions: Optional[List[str]] = None
    nationalities: Optional[List[str]] = None
    salary_ranges: Optional[List[str]] = None
    desired_hobbies: Optional[List[str]] = None
    desired_priorities: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    min_matching_hobbies: int = 1
    min_matching_priorities: int = 1


@dataclass
class SelectedPersona:
    """Class to represent a selected persona with review capabilities"""
    name: str
    age: int
    profession: str
    nationality: str
    salary_range: str
    hobbies: List[str]
    priorities: List[str]
    constraints: List[str]

    def to_reviewer_profile(self) -> ReviewerProfile:
        """Convert to ReviewerProfile format for ProductReviewer"""
        return ReviewerProfile(
            profession=self.profession,
            age=self.age,
            nationality=self.nationality,
            salary_range=self.salary_range,
            priorities=", ".join(self.priorities),
            hobbies=", ".join(self.hobbies),
            constraints=", ".join(self.constraints)
        )

    @classmethod
    def from_series(cls, series: pd.Series) -> 'SelectedPersona':
        """Create SelectedPersona from pandas Series"""
        return cls(
            name=series['name'],
            age=series['age'],
            profession=series['profession'],
            nationality=series['nationality'],
            salary_range=series['salary_range'],
            hobbies=series['hobbies'],
            priorities=series['priorities'],
            constraints=series['constraints']
        )


class PersonaSelector:
    """Class to select and modify personas from a DataFrame based on given criteria"""

    def __init__(self, excel_path: str):
        """
        Initialize the PersonaSelector with a path to the Excel file containing personas.

        Args:
            excel_path: Path to Excel file containing personas
        """
        try:
            self.df = pd.read_excel(excel_path)
            self.prepare_dataframe()
            self._cache_unique_values()
            logger.info("Successfully initialized PersonaSelector")
        except Exception as e:
            logger.error(f"Error initializing PersonaSelector: {str(e)}")
            raise

    def _cache_unique_values(self):
        """Cache unique values for random generation"""
        try:
            self.unique_values = {
                'professions': self.df['profession'].unique().tolist(),
                'nationalities': self.df['nationality'].unique().tolist(),
                'salary_ranges': self.df['salary_range'].unique().tolist(),
                'hobbies': list(set([hobby for hobbies in self.df['hobbies'] for hobby in hobbies])),
                'priorities': list(set([priority for priorities in self.df['priorities'] for priority in priorities])),
                'constraints': list(
                    set([constraint for constraints in self.df['constraints'] for constraint in constraints]))
            }
            logger.debug("Cached unique values for persona generation")
        except Exception as e:
            logger.error(f"Error caching unique values: {str(e)}")
            raise

    def prepare_dataframe(self):
        """Validate and prepare the DataFrame structure"""
        required_columns = [
            'name', 'age', 'profession', 'nationality',
            'salary_range', 'hobbies', 'priorities', 'constraints'
        ]

        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Convert string lists to actual lists if they're stored as strings
        list_columns = ['hobbies', 'priorities', 'constraints']
        for col in list_columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].apply(self._convert_string_to_list)

    @staticmethod
    def _convert_string_to_list(value: str) -> List[str]:
        """Convert string representation of list to actual list"""
        if isinstance(value, list):
            return value
        if pd.isna(value) or value == '':
            return []
        if isinstance(value, str):
            cleaned = value.strip('[]\'\"').replace('\'', '').replace('\"', '')
            return [item.strip() for item in cleaned.split(',') if item.strip()]
        return []

    def _generate_random_persona(self, criteria: PersonaSelectionCriteria) -> pd.Series:
        """Generate a completely random persona that respects given criteria"""
        try:
            random_name = f"RandomPersona_{random.randint(1000, 9999)}"

            age = (random.randint(criteria.age_range[0], criteria.age_range[1])
                   if criteria.age_range else random.randint(18, 80))

            profession = random.choice(
                criteria.professions if criteria.professions
                else self.unique_values['professions']
            )

            nationality = random.choice(
                criteria.nationalities if criteria.nationalities
                else self.unique_values['nationalities']
            )

            salary_range = random.choice(
                criteria.salary_ranges if criteria.salary_ranges
                else self.unique_values['salary_ranges']
            )

            # Generate hobbies with minimum matches
            hobbies = []
            if criteria.desired_hobbies:
                min_matches = min(criteria.min_matching_hobbies, len(criteria.desired_hobbies))
                hobbies.extend(random.sample(criteria.desired_hobbies, min_matches))
            remaining_hobbies = random.sample(
                [h for h in self.unique_values['hobbies'] if h not in hobbies],
                random.randint(1, 3)
            )
            hobbies.extend(remaining_hobbies)

            # Generate priorities with minimum matches
            priorities = []
            if criteria.desired_priorities:
                min_matches = min(criteria.min_matching_priorities, len(criteria.desired_priorities))
                priorities.extend(random.sample(criteria.desired_priorities, min_matches))
            remaining_priorities = random.sample(
                [p for p in self.unique_values['priorities'] if p not in priorities],
                random.randint(1, 2)
            )
            priorities.extend(remaining_priorities)

            # Generate constraints
            constraints = random.sample(self.unique_values['constraints'], random.randint(1, 2))

            return pd.Series({
                'name': random_name,
                'age': age,
                'profession': profession,
                'nationality': nationality,
                'salary_range': salary_range,
                'hobbies': hobbies,
                'priorities': priorities,
                'constraints': constraints
            })
        except Exception as e:
            logger.error(f"Error generating random persona: {str(e)}")
            raise

    def _filter_personas(
            self,
            criteria: PersonaSelectionCriteria,
            num_personas: int,
            randomize_if_insufficient: bool
    ) -> pd.DataFrame:
        """Filter personas based on criteria"""
        try:
            filtered_df = self.df.copy()

            # Apply filters
            if criteria.age_range:
                filtered_df = filtered_df[
                    (filtered_df['age'] >= criteria.age_range[0]) &
                    (filtered_df['age'] <= criteria.age_range[1])
                    ]

            if criteria.professions:
                filtered_df = filtered_df[filtered_df['profession'].isin(criteria.professions)]

            if criteria.nationalities:
                filtered_df = filtered_df[filtered_df['nationality'].isin(criteria.nationalities)]

            if criteria.salary_ranges:
                filtered_df = filtered_df[filtered_df['salary_range'].isin(criteria.salary_ranges)]

            # Apply complex filters
            if criteria.desired_hobbies:
                filtered_df['hobby_match_count'] = filtered_df['hobbies'].apply(
                    lambda x: len(set(x) & set(criteria.desired_hobbies))
                )
                filtered_df = filtered_df[
                    filtered_df['hobby_match_count'] >= criteria.min_matching_hobbies
                    ]

            if criteria.desired_priorities:
                filtered_df['priority_match_count'] = filtered_df['priorities'].apply(
                    lambda x: len(set(x) & set(criteria.desired_priorities))
                )
                filtered_df = filtered_df[
                    filtered_df['priority_match_count'] >= criteria.min_matching_priorities
                    ]

            # Generate random personas if needed
            if len(filtered_df) < num_personas and randomize_if_insufficient:
                num_random_needed = num_personas - len(filtered_df)
                random_personas = []
                for _ in range(num_random_needed):
                    random_personas.append(self._generate_random_persona(criteria))
                random_df = pd.DataFrame(random_personas)
                filtered_df = pd.concat([filtered_df, random_df], ignore_index=True)

            # Ensure we don't exceed requested number of personas
            if len(filtered_df) > num_personas:
                if criteria.desired_hobbies or criteria.desired_priorities:
                    score_columns = []
                    if criteria.desired_hobbies:
                        score_columns.append('hobby_match_count')
                    if criteria.desired_priorities:
                        score_columns.append('priority_match_count')
                    filtered_df['total_score'] = filtered_df[score_columns].sum(axis=1)
                    filtered_df = filtered_df.nlargest(num_personas, 'total_score')
                else:
                    filtered_df = filtered_df.sample(num_personas)

            logger.info(f"Successfully filtered and generated {len(filtered_df)} personas")
            return filtered_df

        except Exception as e:
            logger.error(f"Error filtering personas: {str(e)}")
            raise

    def get_selected_personas(
            self,
            criteria: PersonaSelectionCriteria,
            num_personas: int,
            randomize_if_insufficient: bool = True
    ) -> List[SelectedPersona]:
        """Get selected personas based on criteria"""
        try:
            filtered_df = self._filter_personas(criteria, num_personas, randomize_if_insufficient)
            return [SelectedPersona.from_series(row) for _, row in filtered_df.iterrows()]
        except Exception as e:
            logger.error(f"Error getting selected personas: {str(e)}")
            raise

    def get_unique_values(self) -> Dict[str, List]:
        """Get unique values for each categorical field"""
        return self.unique_values.copy()

    def generate_reviews(
            self,
            product: Product,
            criteria: PersonaSelectionCriteria,
            num_personas: int,
            provider: str,
            api_key: str,
            model_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate product reviews using selected personas"""
        try:
            from product_reviewer import ProductReviewer

            selected_personas = self.get_selected_personas(criteria, num_personas)
            reviewer = ProductReviewer(
                provider=provider,
                api_key=api_key,
                model_config=model_config
            )

            reviews = []
            for persona in selected_personas:
                try:
                    review_session = reviewer.generate_review(
                        product=product,
                        profile=persona.to_reviewer_profile()
                    )

                    reviews.append({
                        'persona_name': persona.name,
                        'persona_info': {
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

            logger.info(f"Successfully generated {len(reviews)} reviews")
            return reviews

        except Exception as e:
            logger.error(f"Error in generate_reviews: {str(e)}")
            raise