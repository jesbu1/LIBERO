"""
Export short example videos for generated variations.

Usage example:
  conda run -n libero python /home/jessez/LIBERO/ood_generation/export_videos.py \
    --distribution distractor_variations \
    --variations-dir /home/jessez/LIBERO/test_all_tasks_distractors/ \
    --output-dir /home/jessez/LIBERO/test_videos_distractors/

  conda run -n libero python /home/jessez/LIBERO/ood_generation/export_videos.py \
    --distribution visual_variations \
    --variations-dir /home/jessez/LIBERO/test_all_tasks_visual/ \
    --output-dir /home/jessez/LIBERO/test_videos_visual/
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import Iterator, Tuple

import numpy as np
import imageio

from libero.libero.envs.env_wrapper import ControlEnv
import libero.libero as libero_pkg


def iter_variations(
    variations_dir: str, distribution_name: str
) -> Iterator[Tuple[str, int, str, str]]:
    root = Path(variations_dir)
    entries = [
        d
        for d in root.iterdir()
        if d.is_dir() and d.name.startswith(distribution_name + "_")
    ]
    for task_dir in sorted(entries):
        i = 0
        while True:
            bddl = task_dir / f"variation_{i}.bddl"
            xml = task_dir / f"variation_{i}.xml"
            if not (bddl.exists() and xml.exists()):
                break
            yield task_dir.name, i, str(bddl), str(xml)
            i += 1


def load_env_with_temp_xml(bddl_file: str, xml_file: str) -> Tuple[ControlEnv, str]:
    assets_dir = os.path.join(os.path.dirname(libero_pkg.__file__), "assets", "scenes")
    os.makedirs(assets_dir, exist_ok=True)
    temp_xml_name = f"temp_{os.getpid()}_{os.path.basename(xml_file)}"
    temp_xml_path = os.path.join(assets_dir, temp_xml_name)
    shutil.copy2(xml_file, temp_xml_path)

    env = ControlEnv(
        bddl_file_name=bddl_file,
        robots=["Panda"],
        has_renderer=False,
        has_offscreen_renderer=True,
        use_camera_obs=False,
        render_camera="frontview",
        scene_xml=f"scenes/{temp_xml_name}",
    )
    env.reset()
    return env, temp_xml_path


def record_video(
    env: ControlEnv,
    out_path: str,
    num_frames: int = 120,
    fps: int = 20,
    width: int = 512,
    height: int = 512,
):
    # Determine action shape
    try:
        low, high = env.env.action_spec
        action = np.zeros_like(high)
    except Exception:
        # Fallback: try action_dim
        action_dim = getattr(env.env, "action_dim", None)
        if action_dim is None:
            action = 0.0
        else:
            action = np.zeros(action_dim)

    writer = imageio.get_writer(out_path, fps=fps)
    try:
        for _ in range(num_frames):
            # render returns HxWx3 RGB in mujoco / robosuite, often upside-down
            frame = env.env.sim.render(
                camera_name="frontview", width=width, height=height, depth=False
            )[::-1]
            writer.append_data(frame)
            env.env.step(action)
    finally:
        writer.close()


def main():
    parser = argparse.ArgumentParser(description="Export short videos for variations")
    parser.add_argument("--distribution", type=str, required=True)
    parser.add_argument("--variations-dir", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--num-tasks", type=int, default=5)
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--fps", type=int, default=20)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    picked = 0
    for task_folder, idx, bddl, xml in iter_variations(
        args.variations_dir, args.distribution
    ):
        if picked >= args.num_tasks:
            break

        env = None
        temp_xml_path = None
        try:
            env, temp_xml_path = load_env_with_temp_xml(bddl, xml)
            task_out_dir = os.path.join(args.output_dir, task_folder)
            os.makedirs(task_out_dir, exist_ok=True)
            out_path = os.path.join(task_out_dir, f"variation_{idx}.mp4")
            record_video(env, out_path, num_frames=args.frames, fps=args.fps)
            print(f"Saved video: {out_path}")
            picked += 1
        except Exception as e:
            print(f"Failed to export video for {task_folder}/variation_{idx}: {e}")
        finally:
            if env is not None:
                env.close()
            if temp_xml_path and os.path.exists(temp_xml_path):
                os.remove(temp_xml_path)


if __name__ == "__main__":
    main()
