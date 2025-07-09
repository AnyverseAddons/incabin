#__________________________________________
#             
#          InCabin Configuration
#__________________________________________

#__________________________________________
# Change this attribute to False when for production
workspace.reduce_resolution = False
# iteration_index = 1
# Change this attribute to False when for production
workspace.testing = False
# Flag to use fixed random seed or not
workspace.fixed_seed = False
# Flag to generate a json file with the occupancy generated for a batch
workspace.generate_occupancy_file = False
#__________________________________________
# Check if running from script console and pass it to the incabin utils constructor
script_console = False
try:
    total_iteration_count
except NameError:
    script_console = True
    iteration_index = 0
    total_iteration_count = 1
print('Script Console: {}'.format(script_console))

#__________________________________________
# Global config: Cameras, environmental conditions, Occupant distribution, childseats, seat belts, additional props, gaze
incabin_config = {
    "use_gen9_characters": True,
    "use_legacy_characters": False,
    "occupant_confs_probabilities": [ 
        {'Conf': 'Empty', 'probability': 0.0},
        {'Conf': 'Normal', 'probability': 1.0}
    ],
    "occupancy_distribution": {
        "use_gemini_distribution": False,
        "from_file": False, 
        'driver_occupancy_probabilities': [
            {'name': 'Empty',  'occupancy': 0, 'probability': 0.0},
            {'name': 'Driver', 'occupancy': 1, 'probability': 1.0} 
        ],
        'copilot_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.25},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.375},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.375},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.0} 
        ],
        'backseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 1.0},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.0},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.0},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.0}
        ],
        'middleseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.25},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.375},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.375},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.0} 
        ],
        'childseat_config': {
            'childseat_type_probabilities': [
                {'Type': 'BabyChild', 'probability': 0.33},
                {'Type': 'Convertible', 'probability': 0.33},
                {'Type': 'Booster', 'probability': 0.33}
            ],
            'childseat_occupancy_probabilities': [
                {'name': 'Empty', 'occupancy': 0, 'probability': 0.0},
                {'name': 'Child', 'occupancy': 1, 'probability': 1.0},
                {'name': 'Object', 'occupancy': 2, 'probability': 0.0}
            ],
            'childseat_orientation_probabilities': [
                {'Orientation': 'Forward', 'probability': 1.0},
                {'Orientation': 'Backward', 'probability': 0.0}
            ],
            'childseat_rotation_max': 30
        },
        'allow_child_driver': False,
        'age_group_probabilities': [
            {'age_group': '0-3', 'kind': 'Baby', 'probability': 0.0},
            {'age_group': '4-8', 'kind': 'Child', 'probability': 0.0},
            {'age_group': '9-16', 'kind': 'Child', 'probability': 0.0},
            {'age_group': '17-30', 'kind': 'Adult', 'probability': 0.33},
            {'age_group': '31-50', 'kind': 'Adult', 'probability': 0.33},
            {'age_group': '50+', 'kind': 'Adult', 'probability': 0.33},
        ],
        'baby_on_lap_probability': 0.0,
        'accessories_probabilities': { 'global': 0.0, 'glasses': 0.5, 'headwear': 0.0, 'mask': 0.0 },
        'object_types': ['Backpack', 'Baseball_cap', 'Bottle', 'Box', 'Can', 'cat', 'Coffee', 'Consumer_electronics', 'Dog', 'Glasses', 'Handbag', 'Hat', 'Milkshake', 'Mobile Phone', 'Paper_Bag', 'Snack', 'Sunglasses', 'Toy', 'ammunition', 'cloth', 'garbage bag', 'handgun', 'knife', 'paper_bag', 'plastic bag', 'sheath', 'snack', 'wallet'], # All possible object types
        # 'object_types': ['Backpack', 'briefcase', 'cat', 'Consumer_electronics', 'Dog', 'duffle' 'Handbag', 'laptop_case' 'Mobile Phone', 'Paper_Bag', 'garbage bag', 'paper_bag', 'plastic bag', 'snack', 'wallet'],
        'seatbelts_distribution': {
            'random_belt_material': True,
            'differentiate_segments': False,
            'belt_on_probability': 0.5, # Probability for seatbelt on when there is a character seatted on
            'seatbelt_placement_probabilities': {
                'Normal': 0.125,
                'BehindTheBack': 0.0,
                'UnderShoulder': 0.0,
                'WrongSideOfHead': 0.0,
                'CharacterOverSeatbelt': 0.0,
                'LapBeltUnder': 0.0,
                'UnderShoulderLapBeltUnder': 0.0
            },   
            'belt_on_without_character_probability': 0.0, # Probability for seatbelt on when the seat is empty
        },
        'gaze_probabilities': {
            'driver_gaze_probabilities':  [
                {'name': 'road', 'id': 0, 'gaze': 1, 'reach': False, 'probability': 1.0},
                {'name': 'ext_mirror', 'id': 1, 'gaze': 1, 'reach': False, 'probability': 1.0},
                {'name': 'int_mirror', 'id': 2, 'gaze': 1, 'reach': False, 'probability':  1.0},
                {'name': 'infotainment', 'id': 3, 'gaze': 0.5, 'reach': True, 'probability':  1.0},
                {'name': 'passenger', 'id': 4, 'gaze': 1, 'reach': False, 'probability':  1.0},
                {'name': 'rear', 'id': 5, 'gaze': 1, 'reach': False, 'probability': 0.0},
                {'name': 'headrest', 'id': 6, 'gaze': 1, 'reach': True, 'probability': 0.0},
                {'name': 'glove', 'id': 7, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'seatbelt', 'id': 8, 'gaze': 1, 'reach': True, 'probability': 0.0},
                {'name': 'floor', 'id': 9, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'free', 'id': 10, 'gaze': 1, 'reach': True, 'probability':  1.0}
            ],
            'copilot_gaze_probabilities': [
                {'name': 'road', 'id': 0, 'gaze': 1, 'reach': False, 'probability': 1.0},
                {'name': 'ext_mirror', 'id': 1, 'gaze': 1, 'reach': False, 'probability': 1.0},
                {'name': 'int_mirror', 'id': 2, 'gaze': 1, 'reach': False, 'probability':  1.0},
                {'name': 'infotainment', 'id': 3, 'gaze': 0.5, 'reach': True, 'probability':  1.0},
                {'name': 'passenger', 'id': 4, 'gaze': 1, 'reach': False, 'probability':  1.0},
                {'name': 'rear', 'id': 5, 'gaze': 1, 'reach': False, 'probability': 0.0},
                {'name': 'headrest', 'id': 6, 'gaze': 1, 'reach': True, 'probability': 0.0},
                {'name': 'glove', 'id': 7, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'seatbelt', 'id': 8, 'gaze': 1, 'reach': True, 'probability': 0.0},
                {'name': 'floor', 'id': 9, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'free', 'id': 10, 'gaze': 1, 'reach': True, 'probability':  1.0}
            ]
        },
        'expression_probabilities': [
            {'name': 'neutral', 'expression': 0, 'probability': 0.20},
            {'name': 'happy', 'expression': 1, 'probability': 0.20},
            {'name': 'sad', 'expression': 2, 'probability': 0.20},
            {'name': 'angry', 'expression': 3, 'probability': 0.15},
            {'name': 'surprised', 'expression': 4, 'probability': 0.15},
            {'name': 'random', 'expression': 5, 'probability': 0.1}
        ]
    }
}

#__________________________________________
#      
#            ON BEGIN ITERATION
#__________________________________________
import random
import re
import json
import os
import importlib
from incabin import incabin
importlib.reload(incabin)


# Create the InCabinUtils object and asign it to the workspace
icu = incabin.InCabinUtils(workspace, resources, script_console)
workspace.icu = icu

if iteration_index == 0:
   
    if not hasattr(anyverse_platform, 'characters_gen9') or not hasattr(anyverse_platform, 'characters_legacy') :
        print('Loading characters...')
        # NOTE: anyverse_platform.characters contains all characters.
        #       anyverse_platform.characters_gen9 contains gen9 characters only
        anyverse_platform.characters_legacy = icu.queryCharacters()
        anyverse_platform.characters_gen9 = icu.queryCharactersGen9()
        
        #print(anyverse_platform.characters)
        print('Characters list loaded!')

    if not hasattr(anyverse_platform, 'childseats'):
        print('Loading childseats...')
        anyverse_platform.childseats = icu.queryChildSeats()
        #print(anyverse_platform.childseats)
        print('Childseat list loaded!')
    
    if not hasattr(anyverse_platform, 'childseatbelts'):
        print('Loading childseatbelts...')
        anyverse_platform.childseatbelts = icu.queryChildSeatBelts()
        #print(anyverse_platform.childseatbelts)
        print('Childseatbelts list loaded!')

    if not hasattr(anyverse_platform, 'objects'):
        print('Loading objects...')
        anyverse_platform.objects = icu.queryObjects()
        #print(anyverse_platform.objects)
        print('Objects list loaded!')
    
    if not hasattr(anyverse_platform, 'accessories'):
        print('Loading accessories...')
        anyverse_platform.accessories = icu.queryAccessories()
        #print(anyverse_platform.accessories)
        print('Accessories list loaded!')

    if not hasattr(anyverse_platform, 'materials'):
        print('Loading materials...')
        anyverse_platform.materials = icu.queryMaterials(color_scheme=True)
        #print(anyverse_platform.materials)
        print('Materials list loaded!')


anyverse_platform.characters = []
if incabin_config["use_gen9_characters"]:
    anyverse_platform.characters += anyverse_platform.characters_gen9
if incabin_config["use_legacy_characters"]:
    anyverse_platform.characters += anyverse_platform.characters_legacy

workspace.characters = anyverse_platform.characters
workspace.characters_legacy = anyverse_platform.characters_legacy
workspace.characters_gen9 = anyverse_platform.characters_gen9
workspace.childseats = anyverse_platform.childseats
workspace.childseatbelts = anyverse_platform.childseatbelts
workspace.objects = anyverse_platform.objects
workspace.accessories = anyverse_platform.accessories
workspace.materials = anyverse_platform.materials
    

#__________________________________________________________
# Get the workspace simulation id
simulation_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Simulation)[0]
generator_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Batch)[0]

#__________________________________________________________
# Set the random seed to whatever is in the seed field in
# the WS depending on the boll variable fixed_seed
# This useful to make the generation deterministic and be
# able to reproduce problems 
if workspace.fixed_seed:
    ws_seed = workspace.get_entity_property_value(generator_id, 'BatchPropertiesComponent','seed')
    if iteration_index % 10 == 0 and ws_seed != 0:
        seed = ws_seed + iteration_index
        print( "Using fixed seed: {}".format( seed ) )
        random.seed( seed )
# elif iteration_index == 0:
#     random_seed = random.randrange(sys.maxsize)
#     print( "Using random seed: {}".format( random_seed ) )
#     random.seed( random_seed )

#__________________________________________________________
# Star setting up the scene for an iteration
print('Iteration: {}'.format(iteration_index))
icu.setGroundRotation(0, simulation_id)

#__________________________________________________________
# Get the car in the workspace id and delete all its occupants
# We assume there is one and only one car in the workspace. It may
# work with more but we have to make sure only one is visible (and
# all its descendents) at rendering time
the_car = icu.getCars()[0]

print('Deleting current occupants...')
# TODO: icu.clearDescendantFixedEntities(the_car)
# entity_type_set = anyverse_platform.WorkspaceEntityTypeSet()
# entity_type_set.add(anyverse_platform.WorkspaceEntityType.AnimatedEntity)

# occupants = workspace.get_hierarchy(the_car, entity_type_set, include_deep_children=True)
# for occupant in occupants:
#     workspace.delete_entity(occupant)

seat_locators = icu.getSeatLocators(the_car)
childseat_locators = icu.getChildseatLocators(the_car)
locators_to_clear = seat_locators + childseat_locators

for loc in locators_to_clear:
    entities_to_clear = [ e for e in workspace.get_hierarchy(loc, include_deep_children=False) if 'FixedEntity' == workspace.get_entity_type(e) or 'AnimatedEntity' == workspace.get_entity_type(e) ]
    for ent in entities_to_clear:
        workspace.delete_entity(ent)

#__________________________________________________________
# Set background, day/night and conditions for illumination
# The probabilities come from incabin requirements. For day 
# scenes the time of day and ground rotation will be randomly picked when setting illumination
# conditions = incabin_config["conditions"]
# if incabin_config['occupancy_distribution']['use_gemini_distribution']: 
#     if gemini_distribution['day']:   
#         day, interior_lights = True, False
#     else:
#         day, interior_lights = False, True
# else:
#     day, interior_lights = icu.selectConditions(conditions)
# print('Day scene: {}, Interior Lighting : {}'.format(day, interior_lights))

# # pick and set a background depending if its day/night
# background, bckgnd_id = icu.selectBackground(day)
# print('Setting background {}'.format(workspace.get_entity_name(bckgnd_id)))
# icu.setBackground(background, simulation_id)

# # set a time of day and a ground rotation randomly so the light will come in from variable angles
# # and the background seen through the windows changes
# sun_elevation, sun_azimuth, ground_rotation = icu.setGroundRotationSunDirection(day, simulation_id)
# print('Sun position: elevation {}, azimuth {}; Ground rotation: {}'.format(sun_elevation, sun_azimuth, ground_rotation))
day = True

#__________________________________________________________
# Pick an occupant distribution based on probabilities and
# call the appropriate function to place them                          
occupant_confs_probabilities = incabin_config["occupant_confs_probabilities"]

# Production occupancy settings
occupancy_distribution = incabin_config["occupancy_distribution"]

if occupancy_distribution['use_gemini_distribution']:
    print('Applying a fixed distribution...')
    print(gemini_distribution)
    icu.applyOccupantDistributionFromGemini(the_car, occupancy_distribution, gemini_distribution)
else:
    conf_idx = icu.choiceUsingProbabilities([ float(c['probability']) for c in occupant_confs_probabilities])
    if occupant_confs_probabilities[conf_idx]['Conf'] == 'Empty':
        occupant_dist = icu.EmptyDistribution(the_car, occupancy_distribution, day)
    elif occupant_confs_probabilities[conf_idx]['Conf'] == 'Normal':
        occupant_dist, _ = icu.NormalOccupantDistribution(the_car, occupancy_distribution, day)
    print('Occupant_dist: {}'.format(occupant_dist))



# Set entities visualization mode to Mesh if testing
if workspace.testing or script_console:
    fixed_entities = workspace.get_fixed_entities()
    animated_entities = workspace.get_entities_by_type("AnimatedEntity")
    fixed_entities.extend(animated_entities)
        
    for entity_id in fixed_entities:
        if workspace.get_entity_type(entity_id) != 'Locator' and workspace.has_entity_component(entity_id, "Viewport3DEntityConfigurationComponent"):
            print(workspace.get_entity_name(entity_id))
            workspace.set_entity_property_value(entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")
   
# Save every iteration occupancy in a global anyverse_platform property
if iteration_index == 0:
    anyverse_platform.batch_occupancy_list = []
if workspace.generate_occupancy_file:
    anyverse_platform.batch_occupancy_list.append(occupant_dist)
    if iteration_index == total_iteration_count - 1:
        batch_out_file_dir = os.path.join(os.path.abspath(os.path.dirname(incabin.__file__)), 'batches_occupancy')
        if not os.path.exists(batch_out_file_dir):
            os.makedirs(batch_out_file_dir)
        try:
            batch_out_file_name = workspace.dataset.get_batch_name() + '_occupancy_output.json'
        except RuntimeError as rt:
            batch_out_file_name = 'dryrun_occupancy_output.json'
        batch_out_file_path = os.path.join(batch_out_file_dir, batch_out_file_name)

        print('Writing occupancy distribution to {}...'.format(batch_out_file_path))
        with open(batch_out_file_path, 'w') as file:
            batch_distribution = json.dump(anyverse_platform.batch_occupancy_list, file, indent = 4)
print('___________________________________________________')

