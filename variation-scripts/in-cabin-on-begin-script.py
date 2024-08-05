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
    "use_car_interior_probabilities": True, # set to True with uniform probabilities to avoid new car cabins until we add them to the config
    "adjust_front_seats": True,
    "car_interior_probabilities": [
        {'car_name': 'Audi_Q5', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False }, 
        {'car_name': 'Chevrolet_Menlo', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Lexus_UX', 'probability': 0.125, 'front_seat_max_depth': 0.05, 'front_seat_max_tilt': 0, 'normal_dist': False },
        {'car_name': 'Porsche_CayenneS', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Unbranded_GenericSUV', 'probability': 0.125, 'front_seat_max_depth': 0.07, 'front_seat_max_tilt': 2, 'normal_dist': False },
        {'car_name': 'Volkswagen_Passat', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Hyundai_Ioniq', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'LandRover_Autobiography', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Ford_Escape', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Honda_Jazz', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Kia_EV_GT', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Mercedes_Benz_EQE_SUV', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Buick_Lacrosse', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Peugeot_3008', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Tesla_S', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Venucia_Star', 'probability': 0.125, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False }
    ],
    "multiple_cameras": False,
    "use_nir": True,
    "rgb_at_day": False, # Override the use of NIR sensor for day light
    "cameras":{
        "RVM": {
            "probability": 0.5,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (0, -40, 0), 'position': (0.435, 0.0, 1.45) }, 
                'Chevrolet_Menlo':  {'rotation': (0, -35, 0), 'position': (0.53, 0.0, 1.26) },
                'Lexus_UX':         {'rotation': (0, -35, 0), 'position': (0.46, 0.005, 1.26) },
                'Porsche_CayenneS': {'rotation': (0, -40, 0), 'position': (0.50, 0.0, 1.45) },
                'Unbranded_GenericSUV':    {'rotation': (0, -40, 0), 'position': (0.485, -0.005, 1.43) },
                'Volkswagen_Passat': {'rotation': (0, -35, 0), 'position': (0.575, -0.027, 1.287)},
                'Hyundai_Ioniq': {'rotation': (0, -40, 0), 'position': (0.45, -0.02, 1.315)},
                'LandRover_Autobiography': {'rotation': (0, -40, 0), 'position': (0.41, 0.0, 1.58)},
                'Ford_Escape': {'rotation': (0, -35, 0), 'position': (0.42, 0.0, 1.37)},
                'Honda_Jazz': {'rotation': (0, -40, 0), 'position': (0.35, 0.0, 1.3)},
                'Kia_EV_GT': {'rotation': (0, -35, 0), 'position': (0.41, 0.0, 1.40)},
                'Mercedes_Benz_EQE_SUV': {'rotation': (0, -40, 0), 'position': (0.42, 0.0, 1.45)},
                'Buick_LaCrosse': {'rotation': (0, -35, 0), 'position': (0.44, -0.03, 1.31)},
                'Peugeot_3008': {'rotation': (0, -40, 0), 'position': (0.37, 0.0, 1.42)},
                'Tesla_S': {'rotation': (0, -40, 0), 'position': (0.32, 0.0, 1.22)},
                'Venucia_Star': {'rotation': (0, -35, 0), 'position': (0.50, 0.0, 1.46)},
                'default':          {'rotation': (0, -25, 0), 'position': (0.60, 0.0, 1.75)}
            },
        },
        "CC": { 
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (0, -10, 0), 'position': (0.53, 0.0, 1.11)}, 
                'Chevrolet_Menlo':   {'rotation': (0, -10, 0), 'position': (0.64, 0.0, 1.03)},
                'Lexus_UX':          {'rotation': (0, -10, 0), 'position': (0.505, 0.02, 0.95)},
                'Porsche_CayenneS':  {'rotation': (0, -10, 0), 'position': (0.60, 0.0, 1.165)},
                'Unbranded_GenericSUV':     {'rotation': (0, -10, 0), 'position': (0.58, 0.005, 1.085)},
                'Volkswagen_Passat': {'rotation': (0, -10, 0), 'position': (0.70, 0.027, 1.00)},
                'Hyundai_Ioniq': {'rotation': (0, -10, 0), 'position': (0.58, -0.02, 1.09)},
                'LandRover_Autobiography': {'rotation': (0, -10, 0), 'position': (0.63, 0.0, 1.22)},
                'Ford_Escape': {'rotation': (0, -10, 0), 'position': (0.51, 0.0, 1.21)},
                'Honda_Jazz': {'rotation': (0, -10, 0), 'position': (0.58, 0.0, 1.03)},
                'Kia_EV_GT': {'rotation': (0, -10, 0), 'position': (0.65, 0.0, 1.175)},
                'Mercedes_Benz_EQE_SUV': {'rotation': (0, -10, 0), 'position': (0.63, 0.0, 1.18)},
                'Buick_LaCrosse': {'rotation': (0, -10, 0), 'position': (0.66, 0.0, 1.03)},
                'Peugeot_3008': {'rotation': (0, -20, 0), 'position': (0.58, 0.0, 1.23)},
                'Tesla_S': {'rotation': (0, -10, 0), 'position': (0.61, 0.0, 0.98)},
                'Venucia_Star': {'rotation': (0, -15, 0), 'position': (0.66, 0.0, 1.19)},
                'default':           {'rotation': (0, -25, 0), 'position': (0.60, 0.0, 1.75)}
            },
        }
    },
    "conditions": [ 
        {'Day': True,  'Cond':'sunny',          'probability': 0.17},
        {'Day': True,  'Cond':'scattered',      'probability': 0.17},
        {'Day': True,  'Cond':'overcast',       'probability': 0.16},
        {'Day': False, 'Cond':'interior-lights','probability': 0.50}
    ],
    "occupant_confs_probabilities": [ 
        {'Conf': 'Empty', 'probability': 0.1},
        {'Conf': 'Normal', 'probability': 0.9}
    ],
    "occupancy_distribution": {
        'driver_occupancy_probabilities': [
            {'name': 'Empty',  'occupancy': 0, 'probability': 0.1},
            {'name': 'Driver', 'occupancy': 1, 'probability': 0.9} 
        ],
        'copilot_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.1},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.1},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.5},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.3} 
        ],
        'backseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.3},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.2},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.3},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.2}
        ],
        'middleseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.3},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.2},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.3},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.2} 
        ],
        'childseat_config': {
            'childseat_type_probabilities': [
                {'Type': 'BabyChild', 'probability': 0.1},
                {'Type': 'Convertible', 'probability': 0.4},
                {'Type': 'Booster', 'probability': 0.50}
            ],
            'childseat_occupancy_probabilities': [
                {'name': 'Empty', 'occupancy': 0, 'probability': 0.25},
                {'name': 'Child', 'occupancy': 1, 'probability': 0.75},
                {'name': 'Object', 'occupancy': 2, 'probability': 0.0}
            ],
            'childseat_orientation_probabilities': [
                {'Orientation': 'Forward', 'probability': 0.5},
                {'Orientation': 'Backward', 'probability': 0.5}
            ],
            'childseat_rotation_max': 30
        },
        'allow_child_driver': False,
        'age_group_probabilities': [
            {'age_group': '0-3', 'kind': 'Baby', 'probability': 0.0},
            {'age_group': '4-12', 'kind': 'Child', 'probability': 0.20},
            {'age_group': '13-18', 'kind': 'Child', 'probability': 0.20},
            {'age_group': '19-30', 'kind': 'Adult', 'probability': 0.20},
            {'age_group': '31-50', 'kind': 'Adult', 'probability': 0.20},
            {'age_group': '50+', 'kind': 'Adult', 'probability': 0.20},
        ],
        'baby_on_lap_probability': 0.0,
        'accessories_probabilities': { 'global': 0.5, 'glasses': 0.5, 'headwear': 0.0, 'mask': 0.0 },
        'object_types': ['Backpack', 'Baseball_cap', 'Bottle', 'Box', 'Can', 'cat', 'Coffee', 'Consumer_electronics', 'Dog', 'Glasses', 'Handbag', 'Hat', 'Milkshake', 'Mobile Phone', 'Paper_Bag', 'Snack', 'Sunglasses', 'Toy', 'ammunition', 'cloth', 'garbage bag', 'handgun', 'knife', 'paper_bag', 'plastic bag', 'sheath', 'snack', 'wallet'], # All possible object types
        # 'object_types': ['Backpack', 'briefcase', 'cat', 'Consumer_electronics', 'Dog', 'duffle' 'Handbag', 'laptop_case' 'Mobile Phone', 'Paper_Bag', 'garbage bag', 'paper_bag', 'plastic bag', 'snack', 'wallet'],
        'seatbelts_distribution': {
            'random_belt_material': True,
            'differentiate_segments': False,
            'belt_on_probability': 0.875, # Probability for seatbelt on when there is a character seatted on
            'seatbelt_placement_probabilities': {
                'Normal': 0.125,
                'BehindTheBack': 0.125,
                'UnderShoulder': 0.125,
                'WrongSideOfHead': 0.125,
                'CharacterOverSeatbelt': 0.125,
                'LapBeltUnder': 0.125,
                'UnderShoulderLapBeltUnder': 0.125
            },   
            'belt_on_without_character_probability': 0.0, # Probability for seatbelt on when the seat is empty
        },
        'gaze_probabilities': {
            'driver_gaze_probabilities':  [
                {'name': 'road', 'id': 0, 'gaze': 1, 'reach': False, 'probability': 0.09},
                {'name': 'ext_mirror', 'id': 1, 'gaze': 1, 'reach': False, 'probability': 0.08},
                {'name': 'int_mirror', 'id': 2, 'gaze': 1, 'reach': False, 'probability':  0.08},
                {'name': 'infotainment', 'id': 3, 'gaze': 0.5, 'reach': True, 'probability':  0.08},
                {'name': 'passenger', 'id': 4, 'gaze': 1, 'reach': False, 'probability':  0.08},
                {'name': 'rear', 'id': 5, 'gaze': 1, 'reach': False, 'probability': 0.09},
                {'name': 'headrest', 'id': 6, 'gaze': 1, 'reach': True, 'probability': 0.09},
                {'name': 'glove', 'id': 7, 'gaze': 0.5, 'reach': True, 'probability': 0.09},
                {'name': 'seatbelt', 'id': 8, 'gaze': 1, 'reach': True, 'probability': 0.09},
                {'name': 'floor', 'id': 9, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'free', 'id': 10, 'gaze': 1, 'reach': True, 'probability':  0.14}
            ],
            'copilot_gaze_probabilities': [
                {'name': 'road', 'id': 0, 'gaze': 1, 'reach': False, 'probability': 0.09},
                {'name': 'ext_mirror', 'id': 1, 'gaze': 1, 'reach': False, 'probability': 0.08},
                {'name': 'int_mirror', 'id': 2, 'gaze': 1, 'reach': False, 'probability':  0.08},
                {'name': 'infotainment', 'id': 3, 'gaze': 0.5, 'reach': True, 'probability':  0.08},
                {'name': 'passenger', 'id': 4, 'gaze': 1, 'reach': False, 'probability':  0.08},
                {'name': 'rear', 'id': 5, 'gaze': 1, 'reach': False, 'probability': 0.09},
                {'name': 'headrest', 'id': 6, 'gaze': 1, 'reach': True, 'probability': 0.09},
                {'name': 'glove', 'id': 7, 'gaze': 0.5, 'reach': True, 'probability': 0.09},
                {'name': 'seatbelt', 'id': 8, 'gaze': 1, 'reach': True, 'probability': 0.09},
                {'name': 'floor', 'id': 9, 'gaze': 0.5, 'reach': True, 'probability': 0.0},
                {'name': 'free', 'id': 10, 'gaze': 1, 'reach': True, 'probability':  0.14}
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
import sys
import incabin
import importlib
del sys.modules['incabin.incabin']
importlib.reload(incabin)


#__________________________________________
def getCameraProbabilityList(incabin_config):
    return [ x for x in incabin_config["cameras"] ], [ incabin_config["cameras"][x]['probability'] for x in incabin_config["cameras"] ]

# Create the InCabinUtils object and asign it to the workspace
icu = incabin.InCabinUtils(workspace, resources, script_console)
workspace.icu = icu

if iteration_index == 0:
    if not hasattr(anyverse_platform, 'cars'):
        print('Loading car interiors...')
        anyverse_platform.cars = icu.queryCars(dynamic_material = True)
        #print(anyverse_platform.cars)
        print('Car list loaded!')
    
    if not hasattr(anyverse_platform, 'characters'):
        print('Loading characters...')
        # NOTE: anyverse_platform.characters contains all characters.
        #       anyverse_platform.characters_gen9 contains gen9 characters only
        anyverse_platform.characters = icu.queryCharacters()
        anyverse_platform.characters_gen9 = icu.queryCharactersGen9()
        
        anyverse_platform.characters += anyverse_platform.characters_gen9

        #print(anyverse_platform.characters)
        print('Characters list loaded!')

    if not hasattr(anyverse_platform, 'babies'):
        print('Loading babies...')
        anyverse_platform.babies = icu.queryBabies()
        #print(anyverse_platform.babies)
        print('Babies list loaded!')
    
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

    if not hasattr(anyverse_platform, 'backgrounds'):
        print('Loading backgrounds...')
        anyverse_platform.backgrounds = icu.queryBackgrounds()
        #print(anyverse_platform.backgrounds)
        print('Backgrounds list loaded!')

    if not hasattr(anyverse_platform, 'materials'):
        print('Loading materials...')
        anyverse_platform.materials = icu.queryMaterials(color_scheme=True)
        #print(anyverse_platform.materials)
        print('Materials list loaded!')

workspace.cars = anyverse_platform.cars
workspace.characters = anyverse_platform.characters
workspace.characters_gen9 = anyverse_platform.characters_gen9
workspace.babies = anyverse_platform.babies
workspace.childseats = anyverse_platform.childseats
workspace.childseatbelts = anyverse_platform.childseatbelts
workspace.objects = anyverse_platform.objects
workspace.accessories = anyverse_platform.accessories
workspace.backgrounds = anyverse_platform.backgrounds
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
icu.clearDescendantFixedEntities(the_car)
icu.deleteAllOnBelts()

#__________________________________________________________
# Pick a random car with probabilities from list of cars, 
# load it as an asset in the workspace and set it as "the_car" 
# to render. If the car from the list can't be loaded from 
# resources, log an error and keep the current car in the workspace
# To use a uniform distribution of cars instead of probabilities,
# set the 'use_car_interior_probabilities' in the config to False
car_list = incabin_config['car_interior_probabilities']
if incabin_config['use_car_interior_probabilities']:
    car_probabilities = incabin_config['car_interior_probabilities']
    if len(car_list) == total_iteration_count:
        selected_car = icu.selectCar(car_probabilities, car_idx = iteration_index)
    else:
        selected_car = icu.selectCar(car_probabilities)
else:
    selected_car = icu.selectCar() # Uniform car interior distribution
car_name = 'default'
if selected_car['entity_id'] != -1:
    for idx, car in enumerate(car_list):
        if selected_car['brand'].split(' ')[0] in car['car_name']:
            normal_dist = car['normal_dist']
            max_depth = car['front_seat_max_depth']
            max_tilt = car['front_seat_max_tilt']
    move_seats_conf = {'move_seats': incabin_config['adjust_front_seats'],
                       'normal_dist' : normal_dist,
                       'max_depth': max_depth,
                       'max_tilt': max_tilt }
    change_belt_material = incabin_config['occupancy_distribution']['seatbelts_distribution']['random_belt_material']
    icu.buildCar(selected_car, the_car, dynamic_materials = True, move_seats_conf = move_seats_conf, change_belt_material = change_belt_material)

    # Set car info from car metadata and put it as custom metadata for annotations
    car_info = icu.setCarInfo(selected_car,the_car)
    car_name = '{}_{}'.format(selected_car['brand'].replace(" ",""), selected_car['model'])
else:
    print('[ERROR] Could not find {} in resources'.format(selected_car))
# Set Eport Always and exclude from occlusion test properties to the car
icu.setExportAlwaysExcludeOcclusion(the_car)
# Set split action to Split to get the seats segmented for non v0 cabins
# If the assets have the compound tag this would not be necessary 
if selected_car['version'].lower() != 'v0':
    icu.setSplitAction(the_car, 'Split')
# We do the split on all cabins v0 dynamic 
# to segment windows, steering wheel and dashboard 
elif selected_car['dynamic_material']:
    icu.setSplitAction(the_car, 'Split')

#__________________________________________________________
# Reset Ego, cameras and light position at origin with rotations 
icu.resetEgo()
icu.resetCameras()
icu.resetLights()
cameras = incabin_config["cameras"]
# Global camera settings
multiple_cameras = incabin_config["multiple_cameras"]
nir_simulation = incabin_config["use_nir"]
rgb_at_day = incabin_config["rgb_at_day"]
# If multiple cameras,  
# place each camera in its position relative to the ego.
# The workspace needs to have an active light associated to each camera for NIR
# To associate lights to cameras we use a naming convention:
# Each active light has to have the same prefix as the correspondent camera.   
# We try to find each active light and move them to the correspondent cam position.
# If an active light is missing, we log a [WARN] 
# and there will be no active illumination for that camera 
if multiple_cameras:
    # place each cameras in its position
    for camera in cameras:
        cam_positions = cameras[camera]["cam_positions"]
        if car_name in cam_positions:
            cam_pos = cam_positions[car_name]['position']
            cam_rot = cam_positions[car_name]['rotation']
        else:
            cam_pos = cam_positions["default"]['position']
            cam_rot = cam_positions["default"]['rotation']
        cam_position = anyverse_platform.Vector3D( cam_pos[0], cam_pos[1], cam_pos[2] )
        cam_rotation = anyverse_platform.Vector3D( cam_rot[0], cam_rot[1], cam_rot[2] )

        cam_ids = [ ci for ci in workspace.get_camera_entities() if camera in workspace.get_entity_name(ci) ]
        cam_id = cam_ids[0] if len(cam_ids) == 1 else 0
        if cam_id != 0:
            cam_pos, cam_rot = icu.setCameraInPosition(cam_id, cam_rotation, cam_position)
            print('{} initial position: x {}, y {}, z {}'.format(camera, cam_pos.x, cam_pos.y, cam_pos.z))
            print('{} initial rotation: x {}, y {}, z {}'.format(camera, cam_rot.x, cam_rot.y, cam_rot.z))
            pos_intervals = cameras[camera]["vibration_traslation"]
            rot_intervals = cameras[camera]["vibration_rotation"]
            cam_pos, cam_rot, _, _ = icu.setCameraVibration(cam_id, pos_intervals, rot_intervals)
            print('{} final position: x {}, y {}, z {}'.format(camera, cam_pos.x, cam_pos.y, cam_pos.z))
            print('{} final rotation: x {}, y {}, z {}'.format(camera, cam_rot.x, cam_rot.y, cam_rot.z))
            workspace.set_entity_property_value(cam_id, 'VisibleComponent','visible', True)
        else:
            print('[ERROR] Missing {} camera in workspace'.format(camera))
        # place active light in the cam position
        # light_ids = [ li for li in workspace.get_entities_by_type('Light') if camera in workspace.get_entity_name(li) ]
        # light_id = light_ids[0] if len(light_ids) >= 1 else 0
        # if light_id != 0:
        #     light_pos, _ = icu.setActiveLightInPosition(light_id, cam_position, cam_rotation)
        #     if camera == 'RVM':
        #         # Advance the light 10 cm to avoid rvm casted shadows
        #         light_pos.x += 0.1
        #         workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', light_pos)
        # else:
        #     print('[WARN] Missing light for {} camera in workspace'.format(camera))
# If not multiple cameras,  
# Randomly select the camera to use and place the ego in the camera position,
# apply vibration as configured and set the visibility to a single camera
else:
    names, probabilities = getCameraProbabilityList(incabin_config)
    cam_ids_idx = icu.choiceUsingProbabilities(probabilities)
    camera_selected = names[cam_ids_idx]

    cam_positions = cameras[camera_selected]["cam_positions"]

    if car_name in cam_positions:
        cam_pos = cam_positions[car_name]['position']
        cam_rot = cam_positions[car_name]['rotation']
    else:
        cam_pos = cam_positions["default"]['position']
        cam_rot = cam_positions["default"]['rotation']

    cam_position = anyverse_platform.Vector3D( cam_pos[0], cam_pos[1], cam_pos[2] )
    cam_rotation = anyverse_platform.Vector3D( cam_rot[0], cam_rot[1], cam_rot[2] )
    ego_pos, ego_rot = icu.setEgoInPosition(cam_rotation, cam_position)
    print('Ego initial position: x {}, y {}, z {}'.format(ego_pos.x, ego_pos.y, ego_pos.z))
    print('Ego initial rotation: x {}, y {}, z {}'.format(ego_rot.x, ego_rot.y, ego_rot.z))

    # Advance the first light light 10 cm to avoid rvm casted shadows
    # light_ids = [ li for li in workspace.get_entities_by_type('Light') ]
    # light_id = light_ids[0] if len(light_ids) > 0 else 0
    # if light_id != 0:
    #     light_pos = anyverse_platform.Vector3D(-0.1, 0, 0) if camera_selected =='RVM' else anyverse_platform.Vector3D(0, 0, 0)
    #     workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', light_pos)
    # else:
    #     print('[WARN] Missing lights in workspace')

    # Apply camera vibration simulation with normal distribution
    pos_intervals = incabin_config["cameras"][camera_selected]["vibration_traslation"]
    rot_intervals = incabin_config["cameras"][camera_selected]["vibration_rotation"]

    ego_pos, ego_rot, _, _ = icu.setEgoVibration(pos_intervals, rot_intervals)
    print('Ego final position: x {}, y {}, z {}'.format(ego_pos.x, ego_pos.y, ego_pos.z))
    print('Ego final rotation: x {}, y {}, z {}'.format(ego_rot.x, ego_rot.y, ego_rot.z))
    #__________________________________________________________
    # Set cameras visibility, accordingly with the selected camera
    camera_id, camera_name = icu.setCameraVisibility(camera_selected)
    print('Using camera: {}'.format(camera_name))

# Reduce camera resolution while testing
if workspace.reduce_resolution and iteration_index == 0:
    print('Reducing all cameras resolution for testing')
    icu.reduceAllCameraResolution(2)
if workspace.testing:
    print('Setting render quality to Medium for testing')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','render_quality','Medium')
else:
    print('PRODUCTION!!!!')
    print('Setting render quality to Ultra for production')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','render_quality','Ultra')

#__________________________________________________________
# Set background, day/night and conditions for illumination
# The probabilities come from incabin requirements. For day 
# scenes the time of day and ground rotation will be randomly picked when setting illumination
conditions = incabin_config["conditions"]

day, cond = icu.selectConditions(conditions)
print('Day scene: {}, Lighting conditions: {}'.format(day, cond))

# pick and set a background depending if its day/night
background, bckgnd_id = icu.selectBackground(day)
print('Setting background {}'.format(workspace.get_entity_name(bckgnd_id)))
icu.setBackground(background, simulation_id)

# set a time of day and a ground rotation randomly so the light will come in from variable angles
# and the background seen through the windows changes
time_of_day, ground_rotation = icu.setGroundRotationTimeOfDay(day, simulation_id)
print('Time: {}, Ground rotation: {}'.format(time_of_day, ground_rotation))
rvm_left_locator = icu.createRVMLocator(the_car, 'left')
rvm_right_locator = icu.createRVMLocator(the_car, 'right')
rvm_inside_locator = icu.createRVMLocator(the_car, 'inside')
cc_info_locator = icu.createCCLocator(the_car)
glove_locator = icu.createGloveCompLocator(the_car)
floor_left_locator = icu.createFloorLocator(the_car, 'left')
floor_right_locator = icu.createFloorLocator(the_car, 'right')
headrest_left_locator = icu.createHeadrestLocator(the_car, 'left')
headrest_right_locator = icu.createHeadrestLocator(the_car, 'right')
seatbelt_left_locator = icu.createSeatbeltLocator(the_car, 'left')
seatbelt_right_locator = icu.createSeatbeltLocator(the_car, 'right')

# Set NIR sensor and NIR ISP for night scenes. Unset it for the rest
if multiple_cameras:
    camera_ids = workspace.get_camera_entities()
    for camera_id in camera_ids:
        if nir_simulation:
            icu.setSensor(camera_id, 'NIR-Sensor')
            icu.setIsp(camera_id, 'NIR-ISP')
            active_light = True # if not day else False
            analog_gain = 15 if day else 7.5
            icu.setAnalogGain(camera_id, analog_gain)
        else:
            icu.setSensor(camera_id, 'RGB-Sensor')
            icu.setIsp(camera_id, 'RGB-ISP')
            active_light = False
        if day and rgb_at_day:
            icu.setSensor(camera_id, 'RGB-Sensor')
            icu.setIsp(camera_id, 'RGB-ISP')
            active_light = False

else:
    if nir_simulation:
        icu.setSensor(camera_id, 'NIR-Sensor')
        icu.setIsp(camera_id, 'NIR-ISP')
        active_light = True if not day else False
        analog_gain = 15 if day else 7.5
        icu.setAnalogGain(camera_id, analog_gain)
    else:
        icu.setSensor(camera_id, 'RGB-Sensor')
        icu.setIsp(camera_id, 'RGB-ISP')
        active_light = False
    if day and rgb_at_day:
        icu.setSensor(camera_id, 'RGB-Sensor')
        icu.setIsp(camera_id, 'RGB-ISP')
        active_light = False

print('Sensor enabled? {}. Setting active lights to {}'.format(True, active_light))
# set the illumination depending on day/night and conditions
intensity = icu.setIllumination(day, cond, background, simulation_id, multiple_cameras, active_light = active_light)
if day:
    print('Sun intensity: {}'.format(intensity))
else:
    print('IBL intensity: {}'.format(intensity))

#__________________________________________________________
# Pick an occupant distribution based on probabilities and
# call the approriate fuction to place them                          
occupant_confs_probabilities = incabin_config["occupant_confs_probabilities"]

# Production occupancy settings
occupancy_distribution = incabin_config["occupancy_distribution"]

conf_idx = icu.choiceUsingProbabilities([ float(c['probability']) for c in occupant_confs_probabilities])
if occupant_confs_probabilities[conf_idx]['Conf'] == 'Empty':
    icu.EmptyDistribution(the_car, occupancy_distribution)
elif occupant_confs_probabilities[conf_idx]['Conf'] == 'Normal':
    # occupant_dist = icu.AllAdultsDistribution(the_car)
    occupant_dist = icu.NormalOccupantDistribution(the_car, occupancy_distribution)
    # occupant_dist = icu.ChildseatDistribution(the_car)
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
   
print('___________________________________________________')

