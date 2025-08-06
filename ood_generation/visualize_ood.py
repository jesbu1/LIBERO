import argparse
import os
import subprocess
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libero.libero.envs import bddl_base_domain
from libero.libero.envs.robots import UR5e
import matplotlib.pyplot as plt

def main():
    """
    Main function to generate and visualize OOD environments.
    """
    parser = argparse.ArgumentParser(description="Generate and visualize OOD environments.")
    parser.add_argument(
        "--input-bddl",
        type=str,
        required=True,
        help="Path to the input BDDL file.",
    )
    parser.add_argument(
        "--input-xml",
        type=str,
        required=True,
        help="Path to the input scene XML file."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to save the generated files.",
    )
    parser.add_argument(
        "--num-variations",
        type=int,
        default=5,
        help="Number of OOD variations to generate.",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Step 1: Generate OOD BDDL and XML files
    generation_script_path = os.path.join(os.path.dirname(__file__), "generate_ood_bddl.py")
    subprocess.run([
        "python", generation_script_path,
        "--input-bddl", args.input_bddl,
        "--input-xml", args.input_xml,
        "--output-dir", args.output_dir,
        "--num-variations", str(args.num_variations)
    ])

    # Step 2: Visualize the generated environments
    for i in range(args.num_variations):
        bddl_filename = os.path.join(
            args.output_dir, f"ood_bddl_{i}_{os.path.basename(args.input_bddl)}"
        )
        xml_filename = os.path.join(
            args.output_dir, f"ood_scene_{i}_{os.path.basename(args.input_xml)}"
        )

        try:
            # Initialize the environment
            env = bddl_base_domain.BDDLBaseDomain(
                bddl_file_name=bddl_filename,
                scene_xml=xml_filename,
                robots=[UR5e()],
                render_camera="frontview",
                has_renderer=True,
                has_offscreen_renderer=False,
                use_camera_obs=True,
            )
            env.reset()
            img = env.render("rgb_array", height=512, width=512)

            # Save the image
            img_filename = os.path.join(args.output_dir, f"ood_visualization_{i}.png")
            plt.imsave(img_filename, img)
            print(f"Saved visualization to {img_filename}")
            
            env.close()
        except Exception as e:
            print(f"Failed to visualize {bddl_filename} with {xml_filename}: {e}")

if __name__ == "__main__":
    main()
