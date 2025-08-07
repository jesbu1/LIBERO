# OOD Generation Script

This script generates Out-of-Distribution (OOD) variations of LIBERO BDDL tasks by applying various transformations to both the task logic and visual properties.

## Features

- **Automatic XML Inference**: No need to specify the scene XML path - it's automatically inferred from the BDDL content
- **Goal Consistency**: Maintains task solvability by updating goal predicates when objects are moved
- **Multiple Transformations**: Applies random combinations of object swapping, placement changes, and visual modifications
- **Visual Variations**: Modifies textures, lighting, and background objects in scene XMLs

## Usage

```bash
python ood_generation/generate_ood_bddl.py \
    --input-bddl path/to/task.bddl \
    --output-dir output_directory \
    --num-variations 10
```

### Arguments

- `--input-bddl`: Path to the input BDDL file (required)
- `--input-xml`: Path to the input scene XML file (optional, auto-inferred if not provided)
- `--output-dir`: Directory to save generated files (required)
- `--num-variations`: Number of OOD variations to generate (default: 10)

## Transformations Applied

### 1. Object Distractors (`add_distractors`)
- Adds random distractor objects to the scene
- Places them in random regions
- Updates initial state with new object placements

### 2. Object Swapping (`swap_objects`)
- Replaces existing objects with different types
- Maintains object names but changes their categories
- Ensures swapped objects are of different types

### 3. Placement Changes (`change_placements`)
- Moves objects to different regions
- **Automatically updates goal predicates** to maintain task solvability
- Ensures tasks remain achievable after transformations

### 4. Visual Modifications (`change_visuals`)
- Changes textures, lighting, and background objects
- Modifies scene XML files with randomized visual properties
- Adds/removes background objects like plants, lamps, decorations

## Output Files

For each variation `i`, the script generates:
- `ood_bddl_i_original_name.bddl`: Modified BDDL file with OOD transformations
- `ood_scene_i_original_name.xml`: Modified scene XML with visual changes

## Example

```bash
# Generate 5 variations of a kitchen task
python ood_generation/generate_ood_bddl.py \
    --input-bddl libero/libero/bddl_files/libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl \
    --output-dir ./ood_variations \
    --num-variations 5
```

This will create:
- `ood_bddl_0_KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl`
- `ood_scene_0_libero_kitchen_tabletop_base_style.xml`
- `ood_bddl_1_KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it.bddl`
- `ood_scene_1_libero_kitchen_tabletop_base_style.xml`
- ... (and so on for 5 variations)

## Supported Workspaces

The script automatically infers the correct scene XML for these workspace types:
- `kitchen_table` → `libero_kitchen_tabletop_base_style.xml`
- `living_room_table` → `libero_living_room_tabletop_base_style.xml`
- `study_table` → `libero_study_base_style.xml`
- `coffee_table` → `libero_coffee_table_base_style.xml`
- `main_table` → `libero_tabletop_base_style.xml`
- `floor` → `libero_floor_base_style.xml`

## Notes

- The script maintains task solvability by updating goal predicates when objects are moved
- Visual changes are applied to scene XMLs but don't affect task logic
- Each variation applies 1-5 random transformations to create diverse OOD scenarios
- Generated files can be used directly with LIBERO environments by specifying the custom BDDL and XML paths
