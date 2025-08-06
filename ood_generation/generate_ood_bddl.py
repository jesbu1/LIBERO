import argparse
import copy
import os
import random
import sys
import xml.etree.ElementTree as ET

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libero.libero.utils import bddl_utils

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

def add_distractors(problem, num_distractors=2):
    """
    Adds distractor objects to the problem. This function also adds the new objects to the initial state.
    """
    for _ in range(num_distractors):
        distractor_type = random.choice(AVAILABLE_OBJECTS)
        distractor_name = f"{distractor_type}_{len(problem.objects) + 1}"
        problem.objects[distractor_name] = distractor_type

        # Add the new object to a random region in the initial state
        regions = [region for region in problem.regions]
        if regions:
            chosen_region = random.choice(regions)
            problem.init.append(f"(On {distractor_name} {chosen_region})")
    return problem

def swap_objects(problem):
    """
    Swaps an existing object with a new one of a different type.
    """
    if not problem.objects:
        return problem

    obj_to_swap = random.choice(list(problem.objects.keys()))
    new_obj_type = random.choice(AVAILABLE_OBJECTS)

    # Ensure we are not swapping with the same type
    while new_obj_type == problem.objects[obj_to_swap]:
        new_obj_type = random.choice(AVAILABLE_OBJECTS)

    # Replace the object type
    problem.objects[obj_to_swap] = new_obj_type
    return problem

def change_placements(problem):
    """
    Changes the placement of objects by reassigning them to different regions.
    """
    if not problem.init or not problem.regions:
        return problem

    # Choose a random object from the initial state to move
    obj_to_move_init = random.choice(problem.init)
    obj_name = obj_to_move_init.split(" ")[1]

    # Choose a new random region for the object
    new_region = random.choice(list(problem.regions.keys()))

    # Update the initial state
    problem.init = [
        init for init in problem.init if not init.startswith(f"(On {obj_name}")
    ]
    problem.init.append(f"(On {obj_name} {new_region})")
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
                if 'file' in texture.attrib:
                    texture.attrib["file"] = f"../textures/{random.choice(AVAILABLE_TEXTURES)}"

    # Change lighting
    for light in root.findall(".//light"):
        light.attrib["diffuse"] = f"{random.random()} {random.random()} {random.random()}"
        light.attrib["pos"] = f"{random.uniform(-3, 3)} {random.uniform(-3, 3)} {random.uniform(2, 5)}"

    # Add/swap background objects
    worldbody = root.find("worldbody")
    if worldbody is not None:
        # Remove existing background objects for simplicity
        for body in worldbody.findall("body"):
            if body.get("name") in BACKGROUND_OBJECTS:
                worldbody.remove(body)
        
        # Add a new background object
        bg_object_name = random.choice(BACKGROUND_OBJECTS)
        bg_object_body = ET.SubElement(worldbody, "body", name=bg_object_name, pos=f"{random.uniform(-2, 2)} {random.uniform(-2, 2)} 0")
        ET.SubElement(bg_object_body, "geom", type="mesh", mesh=bg_object_name, contype="0", conaffinity="0", group="1")

        # Also add the mesh to assets
        asset = root.find("asset")
        if asset is not None:
            ET.SubElement(asset, "mesh", file=f"scenes/{bg_object_name}/{bg_object_name}.obj", name=bg_object_name)


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
        default=10,
        help="Number of OOD variations to generate.",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    problem = bddl_utils.read_bddl(args.input_bddl)

    for i in range(args.num_variations):
        new_problem = copy.deepcopy(problem)
        
        # BDDL variations
        for _ in range(random.randint(1, 5)):
            transformation = random.choice([add_distractors, swap_objects, change_placements])
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
        bddl_utils.write_bddl(new_problem, output_filename)
        print(f"Generated OOD BDDL file: {output_filename}")
        print(f"Generated OOD scene file: {xml_output_filename}")
        # Note: You will need to modify the environment loading code to use the new XML file.
        # This is typically done by passing the `scene_xml` argument to the environment constructor.


if __name__ == "__main__":
    main()
