import argparse
import os
import subprocess
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libero.libero.envs.env_wrapper import ControlEnv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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
        required=False,
        default=None,
        help="Path to the input scene XML file.",
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
    cmd = [
        "python",
        generation_script_path,
        "--input-bddl",
        args.input_bddl,
        "--output-dir",
        args.output_dir,
        "--num-variations",
        str(args.num_variations),
    ]
    if args.input_xml:
        cmd.extend(["--input-xml", args.input_xml])

    subprocess.run(cmd)

    # Step 2: Visualize the original environment for comparison
    try:
        # Create environment for original BDDL
        original_env = ControlEnv(
            bddl_file_name=args.input_bddl,
            robots=["Panda"],
            has_renderer=False,
            has_offscreen_renderer=True,
            use_camera_obs=True,
            render_camera="frontview",
        )
        original_env.reset()

        # Render the original image using offscreen renderer
        original_img = original_env.env.sim.render(
            camera_name="frontview", width=512, height=512, depth=False
        )[::-1]

        # Save the original image
        original_img_filename = os.path.join(
            args.output_dir, "original_visualization.png"
        )
        plt.imsave(original_img_filename, original_img)
        print(f"Saved original visualization to {original_img_filename}")

        original_env.close()
    except Exception as e:
        print(f"Failed to visualize original BDDL: {e}")

    # Step 3: Visualize the generated environments
    for i in range(args.num_variations):
        bddl_filename = os.path.join(
            args.output_dir, f"ood_bddl_{i}_{os.path.basename(args.input_bddl)}"
        )

        # Find the corresponding XML file
        xml_filename = None
        for file in os.listdir(args.output_dir):
            if file.startswith(f"ood_scene_{i}_") and file.endswith(".xml"):
                xml_filename = os.path.join(args.output_dir, file)
                break

        if xml_filename is None:
            print(f"Could not find XML file for variation {i}")
            continue

        try:
            # Create environment with rendering capabilities
            # Use default XML to avoid mesh file path issues for now
            env = ControlEnv(
                bddl_file_name=bddl_filename,
                robots=["Panda"],
                has_renderer=False,
                has_offscreen_renderer=True,
                use_camera_obs=True,
                render_camera="frontview",
            )
            env.reset()

            # Render the image using offscreen renderer
            img = env.env.sim.render(
                camera_name="frontview", width=512, height=512, depth=False
            )[::-1]

            # Save the image
            img_filename = os.path.join(args.output_dir, f"ood_visualization_{i}.png")
            plt.imsave(img_filename, img)
            print(f"Saved visualization to {img_filename}")
            
            env.close()
        except Exception as e:
            print(f"Failed to visualize {bddl_filename}: {e}")

    # Step 4: Create comparison grid
    try:
        create_comparison_grid(args.output_dir, args.num_variations)
    except Exception as e:
        print(f"Failed to create comparison grid: {e}")


def create_comparison_grid(output_dir, num_variations):
    """
    Create a comparison grid showing original vs OOD variations.
    """
    # Check if original image exists
    original_path = os.path.join(output_dir, "original_visualization.png")
    if not os.path.exists(original_path):
        print("Original visualization not found, skipping comparison grid")
        return

    # Load original image
    original_img = mpimg.imread(original_path)

    # Load OOD images
    ood_images = []
    for i in range(num_variations):
        ood_path = os.path.join(output_dir, f"ood_visualization_{i}.png")
        if os.path.exists(ood_path):
            ood_images.append(mpimg.imread(ood_path))

    if not ood_images:
        print("No OOD visualizations found, skipping comparison grid")
        return

    # Create comparison grid
    fig, axes = plt.subplots(
        1, len(ood_images) + 1, figsize=(4 * (len(ood_images) + 1), 4)
    )

    # Plot original
    axes[0].imshow(original_img)
    axes[0].set_title("Original", fontsize=12)
    axes[0].axis("off")

    # Plot OOD variations
    for i, img in enumerate(ood_images):
        axes[i + 1].imshow(img)
        axes[i + 1].set_title(f"OOD Variation {i}", fontsize=12)
        axes[i + 1].axis("off")

    plt.tight_layout()
    comparison_path = os.path.join(output_dir, "comparison_grid.png")
    plt.savefig(comparison_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved comparison grid to {comparison_path}")

if __name__ == "__main__":
    main()
