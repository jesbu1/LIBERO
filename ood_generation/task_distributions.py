"""
Task distribution definitions for OOD generation.
Each distribution defines a specific type of variation and its parameters.
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class VariationType(Enum):
    DISTRACTORS = "distractors"
    SWAPPED_OBJECTS = "swapped_objects"
    VISUAL = "visual"


@dataclass
class TaskDistribution:
    name: str
    variation_type: VariationType
    base_bddl_files: List[str]  # List of base BDDL files to apply variations to
    num_variations: int  # Number of variations to generate per base file
    parameters: Optional[Dict[str, Any]] = (
        None  # Additional parameters specific to this distribution
    )

    def __post_init__(self):
        # Validate that all BDDL files exist
        for bddl_file in self.base_bddl_files:
            if not os.path.exists(bddl_file):
                raise FileNotFoundError(f"BDDL file not found: {bddl_file}")


# Example task distributions
DISTRACTOR_DISTRIBUTION = TaskDistribution(
    name="distractor_variations",
    variation_type=VariationType.DISTRACTORS,
    base_bddl_files=[
        "libero/libero/bddl_files/libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl",
        "libero/libero/bddl_files/libero_spatial/pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate.bddl",
    ],
    num_variations=5,
    parameters={
        "min_distractors": 1,
        "max_distractors": 3,
    },
)

SWAPPED_OBJECTS_DISTRIBUTION = TaskDistribution(
    name="swapped_objects_variations",
    variation_type=VariationType.SWAPPED_OBJECTS,
    base_bddl_files=[
        "libero/libero/bddl_files/libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl",
        "libero/libero/bddl_files/libero_spatial/pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate.bddl",
    ],
    num_variations=5,
    parameters={
        "swap_probability": 0.7,  # Probability of swapping each object
    },
)

VISUAL_DISTRIBUTION = TaskDistribution(
    name="visual_variations",
    variation_type=VariationType.VISUAL,
    base_bddl_files=[
        "libero/libero/bddl_files/libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl",
        "libero/libero/bddl_files/libero_spatial/pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate.bddl",
    ],
    num_variations=5,
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
