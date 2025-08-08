"""
Script to generate OOD variations from defined task distributions.
"""

import os
import argparse
from pathlib import Path
import shutil
from typing import List, Optional

from task_distributions import TaskDistribution, AVAILABLE_DISTRIBUTIONS, VariationType
from generate_ood_bddl import (
    read_bddl,
    write_bddl,
    add_distractors,
    swap_objects,
    change_visuals,
    infer_xml_path,
)

def generate_variations_for_distribution(
    distribution: TaskDistribution,
    output_dir: str,
    base_dir: Optional[str] = None,
) -> List[str]:
    """
    Generate variations for a specific task distribution.
    Returns a list of generated file paths (both BDDL and XML).
    """
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []

    # Process each base BDDL file
    for base_bddl in distribution.base_bddl_files:
        if base_dir:
            base_bddl = os.path.join(base_dir, base_bddl)
        
        # Create a subdirectory for this base task
        base_name = Path(base_bddl).stem
        task_dir = os.path.join(output_dir, f"{distribution.name}_{base_name}")
        os.makedirs(task_dir, exist_ok=True)

        # Read the base BDDL
        problem = read_bddl(base_bddl)
        base_xml = infer_xml_path(base_bddl)

        # Generate variations
        for i in range(distribution.num_variations):
            # Create variation based on distribution type
            if distribution.variation_type == VariationType.DISTRACTORS:
                # Apply distractor variations
                min_dist = distribution.parameters.get("min_distractors", 1)
                max_dist = distribution.parameters.get("max_distractors", 3)
                num_distractors = min(max_dist, max(min_dist, i + 1))
                
                variation = problem.copy()
                for _ in range(num_distractors):
                    variation = add_distractors(variation, num_distractors=1)

            elif distribution.variation_type == VariationType.SWAPPED_OBJECTS:
                # Apply object swapping variations
                variation = problem.copy()
                variation = swap_objects(variation)

            elif distribution.variation_type == VariationType.VISUAL:
                # Apply visual variations only
                variation = problem.copy()

            # Save BDDL variation
            bddl_output = os.path.join(task_dir, f"variation_{i}.bddl")
            write_bddl(variation, bddl_output)
            generated_files.append(bddl_output)

            # Generate and save XML variation if needed
            if distribution.variation_type == VariationType.VISUAL:
                xml_output = os.path.join(task_dir, f"variation_{i}.xml")
                change_visuals(base_xml, xml_output)
                generated_files.append(xml_output)
            else:
                # For non-visual variations, just copy the base XML
                xml_output = os.path.join(task_dir, f"variation_{i}.xml")
                shutil.copy2(base_xml, xml_output)
                generated_files.append(xml_output)

    return generated_files

def main():
    parser = argparse.ArgumentParser(description="Generate OOD variations from task distributions")
    parser.add_argument(
        "--distribution",
        type=str,
        choices=[dist.name for dist in AVAILABLE_DISTRIBUTIONS],
        help="Name of the task distribution to use",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to save generated variations",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base directory for BDDL files (if not using absolute paths)",
    )
    args = parser.parse_args()

    # Find the requested distribution
    distribution = next(
        (dist for dist in AVAILABLE_DISTRIBUTIONS if dist.name == args.distribution),
        None,
    )
    if not distribution:
        print(f"Error: Distribution '{args.distribution}' not found")
        print("Available distributions:")
        for dist in AVAILABLE_DISTRIBUTIONS:
            print(f"  - {dist.name}")
        return

    # Generate variations
    generated_files = generate_variations_for_distribution(
        distribution,
        args.output_dir,
        args.base_dir,
    )

    print(f"\nGenerated {len(generated_files)} files:")
    for f in generated_files:
        print(f"  {f}")

if __name__ == "__main__":
    main()
