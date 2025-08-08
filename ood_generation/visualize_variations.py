"""
Script to visualize variations from task distributions.
"""

import os
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import shutil

from task_distributions import TaskDistribution, AVAILABLE_DISTRIBUTIONS
from libero.libero.envs.env_wrapper import ControlEnv


def visualize_variations(
    distribution: TaskDistribution,
    variations_dir: str,
    output_dir: str,
):
    """
    Create visualizations for all variations in a distribution.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Process each base task's variations by scanning the variations directory
    entries = [
        d for d in os.listdir(variations_dir) if d.startswith(distribution.name + "_")
    ]
    for entry in sorted(entries):
        base_name = entry[len(distribution.name) + 1 :]
        task_dir = os.path.join(variations_dir, f"{distribution.name}_{base_name}")

        if not os.path.exists(task_dir):
            print(f"Warning: Variations directory not found: {task_dir}")
            continue

        # Create a subdirectory for this task's visualizations
        viz_dir = os.path.join(output_dir, f"{distribution.name}_{base_name}")
        os.makedirs(viz_dir, exist_ok=True)

        # Find all variation pairs (BDDL + XML)
        variations = []
        for i in range(distribution.num_variations):
            bddl_file = os.path.join(task_dir, f"variation_{i}.bddl")
            xml_file = os.path.join(task_dir, f"variation_{i}.xml")
            if os.path.exists(bddl_file) and os.path.exists(xml_file):
                variations.append((bddl_file, xml_file))

        if not variations:
            print(f"No variations found in {task_dir}")
            continue

        # Create visualizations
        images = []
        for i, (bddl_file, xml_file) in enumerate(variations):
            try:
                print(f"\nProcessing variation {i}:")
                print(f"  BDDL file: {bddl_file}")
                print(f"  XML file: {xml_file}")

                # Copy XML to assets directory for proper loading
                assets_dir = os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "libero",
                    "libero",
                    "assets",
                    "scenes",
                )
                temp_xml = os.path.join(assets_dir, f"temp_variation_{i}.xml")
                print(f"  Copying XML to: {temp_xml}")
                shutil.copy2(xml_file, temp_xml)

                # Create environment and render
                print("  Creating environment...")
                env = ControlEnv(
                    bddl_file_name=bddl_file,
                    robots=["Panda"],
                    has_renderer=False,
                    has_offscreen_renderer=True,
                    use_camera_obs=True,
                    render_camera="frontview",
                    scene_xml=f"scenes/temp_variation_{i}.xml",
                )
                print("  Resetting environment...")
                env.reset()

                # Render and save image
                print("  Rendering scene...")
                img = env.env.sim.render(
                    camera_name="frontview",
                    width=512,
                    height=512,
                    depth=False,
                )[::-1]

                img_file = os.path.join(viz_dir, f"variation_{i}.png")
                print(f"  Saving image to: {img_file}")
                plt.imsave(img_file, img)
                images.append(img)

                env.close()
                os.remove(temp_xml)
                print("  Success!")

            except Exception as e:
                print(f"Failed to visualize {bddl_file}:")
                print(f"  Error: {e}")
                import traceback

                print(traceback.format_exc())

        # Create comparison grid
        if images:
            fig, axes = plt.subplots(
                1,
                len(images),
                figsize=(4 * len(images), 4),
            )
            if len(images) == 1:
                axes = [axes]

            for i, img in enumerate(images):
                axes[i].imshow(img)
                axes[i].set_title(f"Variation {i}", fontsize=12)
                axes[i].axis("off")

            plt.tight_layout()
            grid_file = os.path.join(viz_dir, "comparison_grid.png")
            plt.savefig(grid_file, dpi=150, bbox_inches="tight")
            plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Visualize variations from task distributions"
    )
    parser.add_argument(
        "--distribution",
        type=str,
        choices=[dist.name for dist in AVAILABLE_DISTRIBUTIONS],
        help="Name of the task distribution to visualize",
    )
    parser.add_argument(
        "--variations-dir",
        type=str,
        required=True,
        help="Directory containing the generated variations",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to save visualizations",
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

    # Generate visualizations
    visualize_variations(distribution, args.variations_dir, args.output_dir)


if __name__ == "__main__":
    main()
