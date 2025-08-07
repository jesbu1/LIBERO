import argparse
import copy
import os
import random
import sys
import xml.etree.ElementTree as ET

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libero.libero.envs import bddl_utils


class BDDLProblem:
    """
    A simple class to represent a BDDL problem that can be manipulated.
    """

    def __init__(self):
        self.problem_name = ""
        self.domain_name = "robosuite"
        self.language_instruction = ""
        self.objects = {}
        self.fixtures = {}
        self.regions = {}
        self.init = []
        self.goal_state = []
        self.obj_of_interest = []
        self.scene_properties = {}


def read_bddl(bddl_path):
    """
    Read a BDDL file and return a BDDLProblem object.
    """
    parsed = bddl_utils.robosuite_parse_problem(bddl_path)

    problem = BDDLProblem()
    problem.problem_name = parsed["problem_name"]
    problem.domain_name = parsed.get("domain_name", "robosuite")
    problem.language_instruction = parsed.get("language_instruction", "")
    problem.objects = parsed["objects"]
    problem.fixtures = parsed["fixtures"]
    problem.regions = parsed["regions"]
    problem.init = parsed["initial_state"]
    problem.goal_state = parsed["goal_state"]
    problem.obj_of_interest = parsed["obj_of_interest"]
    problem.scene_properties = parsed.get("scene_properties", {})

    return problem


def write_bddl(problem, output_path):
    """
    Write a BDDLProblem object to a BDDL file.
    """
    lines = []
    lines.append(f"(define (problem {problem.problem_name.lower()})")
    lines.append(f"  (:domain {problem.domain_name})")

    if problem.language_instruction:
        lines.append(f"  (:language {' '.join(problem.language_instruction)})")

    # Write regions
    if problem.regions:
        lines.append("  (:regions")
        for region_name, region_data in problem.regions.items():
            # Remove target prefix from region name to avoid double-prefixing by parser
            if "target" in region_data and region_data["target"]:
                target = region_data["target"]
                if region_name.startswith(f"{target}_"):
                    region_name_to_write = region_name[len(f"{target}_") :]
                else:
                    region_name_to_write = region_name
            else:
                region_name_to_write = region_name

            lines.append(f"    ({region_name_to_write}")
            if "target" in region_data and region_data["target"]:
                lines.append(f"        (:target {region_data['target']})")
            if "ranges" in region_data and region_data["ranges"]:
                ranges_str = " ".join(
                    [f"({' '.join(map(str, r))})" for r in region_data["ranges"]]
                )
                lines.append(f"        (:ranges ({ranges_str}))")
            if "yaw_rotation" in region_data and region_data["yaw_rotation"]:
                # yaw_rotation is a list of [min, max] values
                yaw_min, yaw_max = region_data["yaw_rotation"]
                lines.append(f"        (:yaw_rotation (({yaw_min} {yaw_max})))")
            if "rgba" in region_data and region_data["rgba"]:
                rgba_str = " ".join(map(str, region_data["rgba"]))
                lines.append(f"        (:rgba ({rgba_str}))")
            lines.append("      )")
        lines.append("    )")

    # Write fixtures
    if problem.fixtures:
        lines.append("  (:fixtures")
        for fixture_type, fixture_list in problem.fixtures.items():
            if fixture_list:
                fixture_str = " ".join(fixture_list)
                lines.append(f"    {fixture_str} - {fixture_type}")
        lines.append("  )")

    # Write objects
    if problem.objects:
        lines.append("  (:objects")
        for obj_type, obj_list in problem.objects.items():
            if obj_list:
                obj_str = " ".join(obj_list)
                lines.append(f"    {obj_str} - {obj_type}")
        lines.append("  )")

    # Write objects of interest
    if problem.obj_of_interest:
        lines.append("  (:obj_of_interest")
        lines.append(f"    {' '.join(problem.obj_of_interest)}")
        lines.append("  )")

    # Write init state
    if problem.init:
        lines.append("  (:init")
        for init_pred in problem.init:
            if isinstance(init_pred, list):
                # Convert list to string format
                lines.append(f"    ({' '.join(init_pred)})")
            else:
                lines.append(f"    {init_pred}")
        lines.append("  )")

    # Write goal state
    if problem.goal_state:
        lines.append("  (:goal")
        lines.append("    (And")
        for goal_pred in problem.goal_state:
            if isinstance(goal_pred, list):
                goal_str = " ".join(goal_pred)
                lines.append(f"      ({goal_str})")
            else:
                lines.append(f"      {goal_pred}")
        lines.append("    )")
        lines.append("  )")

    lines.append(")")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

# A comprehensive list of objects available for swapping and distraction
AVAILABLE_OBJECTS = [
    "tomato_sauce", "salad_dressing", "popcorn", "orange_juice",
    "new_salad_dressing", "milk", "macaroni_and_cheese", "ketchup",
    "cream_cheese", "cookies", "chocolate_pudding", "butter",
    "bbq_sauce", "alphabet_soup", "plate", "akita_black_bowl", "wine_bottle"
]

AVAILABLE_TEXTURES = [
    "yellow_linen_wall_texture.png", "white_wall.png", "white_marble_floor.png",
    "table_light_wood.png", "tile_grigia_caldera_porcelain_floor.png", "stucco_wall.png",
    "smooth_light_gray_plaster.png", "seamless_wood_planks_floor.png", "rustic_floor.png",
    "new_light_gray_plaster.png", "meeka-beige-plaster.png", "martin_novak_wood_table.png",
    "marble_floor.png", "light_grey_plaster.png", "light_gray_plaster.png", "light_floor.png",
    "light_blue_wall.png", "light-gray-plaster.png", "light-gray-floor-tile.png",
    "grigia_caldera_porcelain_floor.png", "kona_gotham.png", "gray_wall.png",
    "gray_plaster.png", "gray_floor.png", "gray_ceramic_tile.png", "dark_green_plaster_wall.png",
    "dark_floor_texture.png", "dark_gray_plaster.png", "dark_blue_wall.png",
    "dapper_gray_floor.png", "cream-plaster.png", "ceramic.png", "capriccio_sky.png",
    "canvas_sky_blue.png", "brown_ceramic_tile.png"
]

BACKGROUND_OBJECTS = [
    "plant", "floor_lamp", "wall_decoration"
]


def infer_xml_path(bddl_path):
    """
    Infers the default scene XML path associated with a BDDL task file.

    The LIBERO benchmark follows a naming convention where the workspace
    (e.g. ``kitchen_table`` or ``living_room_table``) shows up repeatedly
    in the region names inside the BDDL file.  Each workspace maps to a
    default scene XML that is hard-coded in the corresponding environment
    class (see libre/libero/envs/problems/*).

    This helper replicates that mapping so that users do not have to pass
    ``--input-xml`` explicitly.
    """
    mapping = {
        "kitchen_table": "libero_kitchen_tabletop_base_style.xml",
        "living_room_table": "libero_living_room_tabletop_base_style.xml",
        "study_table": "libero_study_base_style.xml",
        "coffee_table": "libero_coffee_table_base_style.xml",
        "main_table": "libero_tabletop_base_style.xml",
        "floor": "libero_floor_base_style.xml",
    }

    # Read the BDDL once into memory
    try:
        with open(bddl_path, "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Cannot open BDDL file {bddl_path}: {e}")

    for workspace_keyword, scene_filename in mapping.items():
        if workspace_keyword in content:
            base_scene_dir = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "libero",
                    "libero",
                    "assets",
                    "scenes",
                )
            )
            inferred_path = os.path.join(base_scene_dir, scene_filename)
            if not os.path.exists(inferred_path):
                raise FileNotFoundError(
                    f"Inferred scene XML {inferred_path} does not exist. Please check installation."
                )
            return inferred_path

    raise ValueError(
        "Unable to infer scene XML from the BDDL file. Please supply --input-xml explicitly."
    )


def add_distractors(problem, num_distractors=1):
    """
    Adds distractor objects to the problem. This function also adds the new objects to the initial state.
    """
    # Check if there are already many objects to avoid overcrowding
    total_objects = sum(
        len(obj_list) if isinstance(obj_list, list) else 1
        for obj_list in problem.objects.values()
    )
    if total_objects >= 5:  # Limit total objects to avoid placement issues
        return problem

    # Track which regions are already occupied
    occupied_regions = set()
    for init_pred in problem.init:
        if (
            isinstance(init_pred, list)
            and len(init_pred) >= 3
            and init_pred[0].lower() == "on"
        ):
            occupied_regions.add(init_pred[2])
        elif isinstance(init_pred, str) and init_pred.strip().lower().startswith("(on"):
            # Parse string format "(on obj region)"
            parts = (
                init_pred.strip()[1:-1].split()
                if init_pred.strip().endswith(")")
                else init_pred.strip().split()
            )
            if len(parts) >= 3:
                occupied_regions.add(parts[2])

    # Only add distractors if we have available regions
    available_regions = [
        region for region in problem.regions if region not in occupied_regions
    ]
    if not available_regions:
        return problem  # Skip if no available regions

    for _ in range(min(num_distractors, len(available_regions))):
        distractor_type = random.choice(AVAILABLE_OBJECTS)

        # Generate unique object name
        existing_objects = set()
        for obj_list in problem.objects.values():
            if isinstance(obj_list, list):
                existing_objects.update(obj_list)
            else:
                existing_objects.add(obj_list)

        counter = 3  # Start from 3 to avoid conflicts with original objects
        while f"{distractor_type}_{counter}" in existing_objects:
            counter += 1
        distractor_name = f"{distractor_type}_{counter}"

        # Add to objects dictionary with correct structure
        if distractor_type not in problem.objects:
            problem.objects[distractor_type] = []
        elif not isinstance(problem.objects[distractor_type], list):
            # Convert string to list if needed
            problem.objects[distractor_type] = [problem.objects[distractor_type]]
        problem.objects[distractor_type].append(distractor_name)

        # Choose from available regions
        chosen_region = random.choice(available_regions)
        available_regions.remove(chosen_region)  # Remove from available list

        problem.init.append(f"(On {distractor_name} {chosen_region})")
    return problem


def swap_objects(problem):
    """
    Swaps an existing object with a new one of a different type.
    """
    if not problem.objects:
        return problem

    # Find all object names across all types
    all_object_names = []
    for obj_type, obj_names in problem.objects.items():
        if isinstance(obj_names, list):
            all_object_names.extend(obj_names)
        else:
            all_object_names.append(obj_names)

    if not all_object_names:
        return problem

    # Choose a random object to swap
    obj_to_swap = random.choice(all_object_names)
    new_obj_type = random.choice(AVAILABLE_OBJECTS)

    # Find which type the object currently belongs to
    old_obj_type = None
    for obj_type, obj_names in problem.objects.items():
        if isinstance(obj_names, list) and obj_to_swap in obj_names:
            old_obj_type = obj_type
            break
        elif obj_names == obj_to_swap:
            old_obj_type = obj_type
            break

    if old_obj_type is None:
        return problem

    # Ensure we are not swapping with the same type
    while new_obj_type == old_obj_type:
        new_obj_type = random.choice(AVAILABLE_OBJECTS)

    # Remove from old type
    if isinstance(problem.objects[old_obj_type], list):
        problem.objects[old_obj_type].remove(obj_to_swap)
        if not problem.objects[old_obj_type]:  # If list is empty, remove the type
            del problem.objects[old_obj_type]
    else:
        del problem.objects[old_obj_type]

    # Add to new type
    if new_obj_type not in problem.objects:
        problem.objects[new_obj_type] = []
    elif not isinstance(problem.objects[new_obj_type], list):
        problem.objects[new_obj_type] = [problem.objects[new_obj_type]]
    problem.objects[new_obj_type].append(obj_to_swap)

    return problem


def change_placements(problem):
    """
    Randomly move one existing object to a different region *and* update
    any goal predicates that reference that object's placement so the
    task remains solvable.
    """
    if not problem.init or not problem.regions:
        return problem

    # --------------------------
    # 1. Pick a random placement (avoid fixtures)
    # --------------------------
    # Filter out fixture placements to avoid moving them
    movable_init_items = []
    for init_item in problem.init:
        if isinstance(init_item, list) and len(init_item) >= 2:
            obj_name = init_item[1]
        elif isinstance(init_item, str):
            # Parse string format "(on obj region)"
            parts = (
                init_item.strip()[1:-1].split()
                if init_item.strip().endswith(")")
                else init_item.strip().split()
            )
            obj_name = parts[1] if len(parts) >= 2 else ""
        else:
            continue

        # Check if this is a fixture (not a movable object)
        is_fixture = False
        for fixture_type, fixture_list in problem.fixtures.items():
            if obj_name in fixture_list:
                is_fixture = True
                break

        if not is_fixture:
            movable_init_items.append(init_item)

    if not movable_init_items:
        return problem

    old_init_item = random.choice(movable_init_items)

    # Handle both string and list formats
    if isinstance(old_init_item, str):
        # Parse string format: "(On obj_name region_name)"
        clean_str = old_init_item.strip()
        if clean_str.startswith("(") and clean_str.endswith(")"):
            clean_str = clean_str[1:-1]  # Remove outer parentheses
        tokens = clean_str.split()
        if len(tokens) != 3:
            # Unexpected formatting – skip this transformation
            return problem
        predicate, obj_name, old_region = tokens
    elif isinstance(old_init_item, list):
        # List format: ["On", "obj_name", "region_name"]
        if len(old_init_item) != 3:
            # Unexpected formatting – skip this transformation
            return problem
        predicate, obj_name, old_region = old_init_item
    else:
        # Unexpected format – skip this transformation
        return problem

    # --------------------------
    # 2. Sample a *different* region
    # --------------------------
    if len(problem.regions) == 1:
        # Only one region available, nothing to change.
        return problem

    new_region = random.choice(list(problem.regions.keys()))
    while new_region == old_region:
        new_region = random.choice(list(problem.regions.keys()))

    # --------------------------
    # 3. Update the init state
    # --------------------------
    # Remove the specific placement for this object
    problem.init = [
        st
        for st in problem.init
        if not (
            (isinstance(st, str) and f" {obj_name} " in st)
            or (isinstance(st, list) and len(st) >= 2 and st[1] == obj_name)
        )
    ]
    problem.init.append([predicate, obj_name, new_region])

    # --------------------------
    # 4. Keep the goal consistent
    # --------------------------
    if hasattr(problem, "goal_state"):
        updated_goals = []
        for clause in problem.goal_state:
            # Clause is a list such as ["On", "obj", "region"] OR ["In", ...]
            if (
                isinstance(clause, (list, tuple))
                and len(clause) == 3
                and clause[1] == obj_name
                and clause[0].lower() in {"on", "in"}
            ):
                updated_goals.append([clause[0], clause[1], new_region])
            else:
                updated_goals.append(clause)
        problem.goal_state = updated_goals

    return problem


def change_visuals(xml_path, output_xml_path):
    """
    Changes the visual properties of the scene, including textures, lighting, and background objects.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Change textures
    for material in root.findall(".//material"):
        if "texture" in material.attrib:
            texture_name = material.attrib["texture"]
            for texture in root.findall(f".//texture[@name='{texture_name}']"):
                if "file" in texture.attrib:
                    texture.attrib["file"] = (
                        f"../textures/{random.choice(AVAILABLE_TEXTURES)}"
                    )

    # Change lighting
    for light in root.findall(".//light"):
        light.attrib["diffuse"] = (
            f"{random.random()} {random.random()} {random.random()}"
        )
        light.attrib["pos"] = (
            f"{random.uniform(-3, 3)} {random.uniform(-3, 3)} {random.uniform(2, 5)}"
        )

    # Skip background object changes to avoid mesh file path issues
    # This could be re-enabled later with proper mesh file handling

    tree.write(output_xml_path)


def main():
    """
    Main function to generate OOD BDDL and scene files.
    """
    parser = argparse.ArgumentParser(description="Generate OOD BDDL and scene files.")
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
        help="Path to the input scene XML file. If not provided, it will be automatically inferred from the BDDL.",
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
        default=10,
        help="Number of OOD variations to generate.",
    )
    args = parser.parse_args()

    # Automatically infer the XML path if the user did not provide one
    if args.input_xml is None:
        args.input_xml = infer_xml_path(args.input_bddl)
        print(f"[info] Inferred scene XML path: {args.input_xml}")

    os.makedirs(args.output_dir, exist_ok=True)

    problem = read_bddl(args.input_bddl)

    for i in range(args.num_variations):
        new_problem = copy.deepcopy(problem)

        # BDDL variations - apply transformations conservatively
        for _ in range(random.randint(1, 2)):
            transformation = random.choice([add_distractors, change_placements])
            new_problem = transformation(new_problem)

        # Visual variations
        xml_output_filename = os.path.join(
            args.output_dir, f"ood_scene_{i}_{os.path.basename(args.input_xml)}"
        )
        change_visuals(args.input_xml, xml_output_filename)

        # Save the new BDDL file
        output_filename = os.path.join(
            args.output_dir, f"ood_bddl_{i}_{os.path.basename(args.input_bddl)}"
        )
        write_bddl(new_problem, output_filename)
        print(f"Generated OOD BDDL file: {output_filename}")
        print(f"Generated OOD scene file: {xml_output_filename}")
        # Note: You will need to modify the environment loading code to use the new XML file.
        # This is typically done by passing the `scene_xml` argument to the environment constructor.


if __name__ == "__main__":
    main()
