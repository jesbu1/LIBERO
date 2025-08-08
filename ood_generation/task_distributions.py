"""
Task distribution definitions for OOD generation.
Each distribution defines a specific type of variation and its parameters.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class VariationType(Enum):
    DISTRACTORS = "distractors"
    SWAPPED_OBJECTS = "swapped_objects"
    VISUAL = "visual"


@dataclass
class TaskDistribution:
    name: str
    variation_type: VariationType
    num_variations: int  # Number of variations to generate per base file
    parameters: Optional[Dict[str, Any]] = (
        None  # Additional parameters specific to this distribution
    )


# Example task distributions
DISTRACTOR_DISTRIBUTION = TaskDistribution(
    name="distractor_variations",
    variation_type=VariationType.DISTRACTORS,
    num_variations=1,
    parameters={
        "min_distractors": 1,
        "max_distractors": 3,
    },
)

SWAPPED_OBJECTS_DISTRIBUTION = TaskDistribution(
    name="swapped_objects_variations",
    variation_type=VariationType.SWAPPED_OBJECTS,
    num_variations=1,
    parameters={
        "swap_probability": 0.7,  # Probability of swapping each object
    },
)

VISUAL_DISTRIBUTION = TaskDistribution(
    name="visual_variations",
    variation_type=VariationType.VISUAL,
    num_variations=1,
    parameters={
        "change_textures": True,
        "change_lighting": True,
    },
)

# List of all available distributions
AVAILABLE_DISTRIBUTIONS = [
    DISTRACTOR_DISTRIBUTION,
    SWAPPED_OBJECTS_DISTRIBUTION,
    VISUAL_DISTRIBUTION,
]
