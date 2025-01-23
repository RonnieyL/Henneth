import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import random
import logging
import os
from utils import ReviewerProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebsitePersonaSelectionCriteria:
    """Class to hold the selection criteria for website reviewer personas"""
    age_range: Optional[Tuple[int, int]] = None
    expertise_areas: Optional[List[str]] = None
    experience_range: Optional[Tuple[int, int]] = None
    profession: Optional[List[str]] = None
    industry_focus: Optional[List[str]] = None
    min_matching_specializations: int = 1
    min_matching_focus: int = 1


class WebsitePersonaSelector:
    """Class to select and modify website reviewer personas based on criteria"""

    def __init__(self, excel_path: str):
        """Initialize with path to Excel file containing website reviewer personas"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), excel_path)
            self.df = pd.read_excel(file_path)
            self.prepare_dataframe()
            self._cache_unique_values()
            logger.info("Successfully initialized WebsitePersonaSelector")
        except Exception as e:
            logger.error(f"Error initializing WebsitePersonaSelector: {str(e)}")
            raise

    def _cache_unique_values(self):
        """Cache unique values for random generation"""
        try:
            self.unique_values = {
                'expertise_areas': self.df['expertise_areas'].explode().unique().tolist(),
                'profession': self.df['profession'].unique().tolist(),
                'industry_focus': self.df['industry_focus'].unique().tolist(),
                'specializations': list(set([spec for specs in self.df['specializations'] for spec in specs])),
            }
        except Exception as e:
            logger.error(f"Error caching unique values: {str(e)}")
            raise

    def prepare_dataframe(self):
        """Validate and prepare the DataFrame structure"""
        required_columns = [
            'name', 'age', 'profession', 'expertise_areas', 'years_experience',
            'specializations', 'industry_focus'
        ]

        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Convert string lists to actual lists
        list_columns = ['expertise_areas', 'specializations']
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

    def _filter_personas(
            self,
            criteria: WebsitePersonaSelectionCriteria,
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

            if criteria.experience_range:
                filtered_df = filtered_df[
                    (filtered_df['years_experience'] >= criteria.experience_range[0]) &
                    (filtered_df['years_experience'] <= criteria.experience_range[1])
                    ]

            if criteria.profession:
                filtered_df = filtered_df[filtered_df['profession'].isin(criteria.profession)]

            if criteria.industry_focus:
                filtered_df = filtered_df[filtered_df['industry_focus'].isin(criteria.industry_focus)]

            # Apply expertise areas filter
            if criteria.expertise_areas:
                filtered_df['expertise_match_count'] = filtered_df['expertise_areas'].apply(
                    lambda x: len(set(x) & set(criteria.expertise_areas))
                )
                filtered_df = filtered_df[
                    filtered_df['expertise_match_count'] >= criteria.min_matching_specializations
                    ]

            # Generate random personas if needed
            if len(filtered_df) < num_personas and randomize_if_insufficient:
                missing_count = num_personas - len(filtered_df)
                random_personas = []
                for _ in range(missing_count):
                    random_persona = self._generate_random_persona(criteria)
                    random_personas.append(random_persona)
                if random_personas:
                    random_df = pd.DataFrame(random_personas)
                    filtered_df = pd.concat([filtered_df, random_df], ignore_index=True)

            # Sort by match score and select top personas
            if len(filtered_df) > num_personas:
                if criteria.expertise_areas:
                    filtered_df = filtered_df.nlargest(num_personas, 'expertise_match_count')
                else:
                    filtered_df = filtered_df.sample(num_personas)

            return filtered_df

        except Exception as e:
            logger.error(f"Error filtering personas: {str(e)}")
            raise

    def _generate_random_persona(self, criteria: WebsitePersonaSelectionCriteria) -> Dict[str, Any]:
        """Generate a random persona that meets the criteria"""
        try:
            age = random.randint(
                criteria.age_range[0] if criteria.age_range else 25,
                criteria.age_range[1] if criteria.age_range else 65
            )

            years_experience = random.randint(
                criteria.experience_range[0] if criteria.experience_range else 2,
                criteria.experience_range[1] if criteria.experience_range else 20
            )

            profession = random.choice(
                criteria.profession if criteria.profession
                else self.unique_values['profession']
            )

            # Ensure minimum matching expertise areas
            expertise_areas = []
            if criteria.expertise_areas:
                min_matches = min(
                    criteria.min_matching_specializations,
                    len(criteria.expertise_areas)
                )
                expertise_areas.extend(random.sample(criteria.expertise_areas, min_matches))

            # Add additional random expertise areas
            remaining_areas = [
                area for area in self.unique_values['expertise_areas']
                if area not in expertise_areas
            ]
            additional_areas = random.sample(
                remaining_areas,
                random.randint(1, 3)
            )
            expertise_areas.extend(additional_areas)

            industry_focus = random.choice(
                criteria.industry_focus if criteria.industry_focus
                else self.unique_values['industry_focus']
            )

            return {
                'name': f"Reviewer_{random.randint(1000, 9999)}",
                'age': age,
                'profession': profession,
                'expertise_areas': expertise_areas,
                'years_experience': years_experience,
                'specializations': random.sample(self.unique_values['specializations'], 3),
                'industry_focus': industry_focus
            }

        except Exception as e:
            logger.error(f"Error generating random persona: {str(e)}")
            raise

    def get_selected_personas(
            self,
            criteria: WebsitePersonaSelectionCriteria,
            num_personas: int,
            randomize_if_insufficient: bool = True
    ) -> List[ReviewerProfile]:
        """Get selected personas based on criteria"""
        try:
            filtered_df = self._filter_personas(criteria, num_personas, randomize_if_insufficient)

            # Convert to ReviewerProfile objects
            profiles = []
            for _, row in filtered_df.iterrows():
                profile = ReviewerProfile(
                    profession=row['profession'],
                    age=row['age'],
                    years_experience=row['years_experience'],
                    expertise_areas=row['expertise_areas'],
                    technical_skills=row['specializations'],
                    industry_focus=row['industry_focus']
                )
                profiles.append(profile)

            return profiles

        except Exception as e:
            logger.error(f"Error getting selected personas: {str(e)}")
            raise

    def get_unique_values(self) -> Dict[str, List]:
        """Get unique values for each categorical field"""
        return self.unique_values.copy()