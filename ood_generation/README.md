# Out-of-Distribution Environment Generation

This package provides scripts for generating and visualizing out-of-distribution (OOD) environments for testing the robustness of robotic manipulation policies.

## Features

- **Logical Variations (BDDL):**
  - Add distractor objects.
  - Swap task-relevant objects.
  - Change object placements.
- **Visual Variations (XML):**
  - Randomize textures and materials.
  - Alter lighting conditions.
  - Swap background objects.

## Prerequisites

Ensure you have all the necessary dependencies installed by following the main `README.md` of the `libero` project.

## Scripts

### 1. `generate_ood_bddl.py`

This script generates a specified number of OOD variations from a base BDDL and scene XML file.

**Usage:**

```bash
python ood_generation/generate_ood_bddl.py \
    --input-bddl [PATH_TO_INPUT_BDDL] \
    --input-xml [PATH_TO_INPUT_XML] \
    --output-dir [PATH_TO_OUTPUT_DIRECTORY] \
    --num-variations [NUMBER_OF_VARIATIONS]
```

**Arguments:**

- `--input-bddl`: Path to the input BDDL file.
- `--input-xml`: Path to the input scene XML file.
- `--output-dir`: Directory to save the generated BDDL and XML files.
- `--num-variations`: Number of OOD variations to generate (default: 10).

### 2. `visualize_ood.py`

This script first generates a set of OOD environments and then renders an image of the initial state of each one.

**Usage:**

```bash
python ood_generation/visualize_ood.py \
    --input-bddl [PATH_TO_INPUT_BDDL] \
    --input-xml [PATH_TO_INPUT_XML] \
    --output-dir [PATH_TO_OUTPUT_DIRECTORY] \
    --num-variations [NUMBER_OF_VARIATIONS]
```

**Arguments:**

- `--input-bddl`: Path to the input BDDL file.
- `--input-xml`: Path to the input scene XML file.
- `--output-dir`: Directory to save the generated files and visualizations.
- `--num-variations`: Number of OOD variations to generate (default: 5).

## Example

To generate and visualize 5 OOD variations of the `open_the_middle_drawer_of_the_cabinet` task:

```bash
python ood_generation/visualize_ood.py \
    --input-bddl libero/libero/bddl_files/libero_goal/open_the_middle_drawer_of_the_cabinet.bddl \
    --input-xml libero/libero/assets/scenes/libero_tabletop_base_style.xml \
    --output-dir tmp/ood_output \
    --num-variations 5
```

This will create a `tmp/ood_output` directory with the generated BDDL files, XML scene files, and the rendered images of each variation.
