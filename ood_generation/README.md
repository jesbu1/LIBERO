## OOD generation and visualization (minimal guide)

This directory contains tools to generate and visualize Out-of-Distribution (OOD) variations for LIBERO tasks.

### Environment

If you use fish or a non-interactive shell, prefer running with conda-run (no activation needed):

```bash
conda run -n libero python --version
```

Alternatively, in fish:

```fish
eval (conda shell.fish hook)
conda activate libero
```

### Generate variations for ALL tasks

Two distributions are provided out of the box:
- distractor_variations: adds on-table distractor objects with collision-aware placement
- visual_variations: randomizes scene textures and lighting

Run generation across all tasks in `libero_10`, `libero_spatial`, `libero_goal`, `libero_object`:

```bash
# Distractors for all tasks
conda run -n libero python /home/jessez/LIBERO/ood_generation/generate_variations.py \
  --distribution distractor_variations \
  --output-dir /home/jessez/LIBERO/test_all_tasks_distractors/

# Visual variations for all tasks
conda run -n libero python /home/jessez/LIBERO/ood_generation/generate_variations.py \
  --distribution visual_variations \
  --output-dir /home/jessez/LIBERO/test_all_tasks_visual/
```

Output structure example:

```
/home/jessez/LIBERO/test_all_tasks_distractors/
  distractor_variations_<TASK_NAME>/
    variation_0.bddl
    variation_0.xml
```

To increase how many variations per task are generated, edit `num_variations` in `ood_generation/task_distributions.py` for the corresponding distribution.

### Visualize generated scenes

The visualizer loads each `(BDDL, XML)` pair, renders a frame, and saves it.

```bash
# Visualize distractor variations
conda run -n libero python /home/jessez/LIBERO/ood_generation/visualize_variations.py \
  --distribution distractor_variations \
  --variations-dir /home/jessez/LIBERO/test_all_tasks_distractors/ \
  --output-dir /home/jessez/LIBERO/test_all_tasks_distractors_viz/

# Visualize visual variations
conda run -n libero python /home/jessez/LIBERO/ood_generation/visualize_variations.py \
  --distribution visual_variations \
  --variations-dir /home/jessez/LIBERO/test_all_tasks_visual/ \
  --output-dir /home/jessez/LIBERO/test_all_tasks_visual_viz/
```

Each task folder in the output will also include a `comparison_grid.png`.

### Notes & troubleshooting

- If you see robosuite macro warnings, they are safe to ignore.
- We filter out a problematic texture (`table_light_wood.png`) that can cause Mujoco PNG grid errors.
- If you’re in fish and `conda activate` fails, use `conda run -n libero …` as shown above.
- Distractor placement respects existing placements via bounding-box collision checks and caps oversized “occupied” regions to keep the table usable.

### Advanced: single-task OOD (optional)

For single-task experimentation, you can still use `generate_ood_bddl.py` directly. It infers the scene XML and can apply per-file OOD changes.

```bash
conda run -n libero python /home/jessez/LIBERO/ood_generation/generate_ood_bddl.py \
  --input-bddl /home/jessez/LIBERO/libero/libero/bddl_files/libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl \
  --output-dir /home/jessez/LIBERO/one_off_out/
```
