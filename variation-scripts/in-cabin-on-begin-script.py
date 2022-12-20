#__________________________________________
#             
#          InCabin Configuration
#__________________________________________

#__________________________________________
# Change this attribute to False when for production
workspace.reduce_resolution = False
# iteration_index = 1
# Change this attribute to False when for production
workspace.testing = True
#__________________________________________
# Check if running from script console and pass it to the incabin utils constructor
script_console = False
try:
    total_iteration_count
except NameError:
    script_console = True
    iteration_index = 0
print('Script Console: {}'.format(script_console))

#__________________________________________
# Global config: Cameras, environmental conditions, Occupant distribution, childseats, seat belts, additional props, gaze
incabin_config = {
    "cameras":{
        "RVM": {
            "probability": 0.75,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [5,5,5], # in degrees
            "cam_positions": {
                'Audi_Q5': {'EGO': (0.385, 0.0, 1.44), 'position': (0.52, 0.0, 1.45, 30) }, 
                'Chevrolet_Menlo':  {'EGO': (0.41, 0.0, 1.315), 'position': (0.61, 0.0, 1.31, 30) },
                'Lexus_UX':         {'EGO': (0.3198521, 0.0, 1.3166237), 'position': (0.53, 0.005, 1.29, 30) },
                'Porsche_Cayenne': {'EGO': (0.39, 0.0, 1.495), 'position': (0.60, 0.0, 1.45, 25) },
                'Unbranded_GenericSUV':    {'EGO': (0.3510127, 0.0, 1.46), 'position': (0.52, -0.005, 1.43, 25) },
                'Volkswagen_Passat':{'EGO': (0.45, 0.025, 1.3), 'position': (0.60, -0.027, 1.287, 30)},
                'default':          {'EGO': (0.39, 0.0, 1.495), 'position': (0.60, 0.0, 1.75, 25)}
            },
        },
        "CC": { 
            "probability": 0.25,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [5,5,5], # in degrees
            "cam_positions": {
                'Audi_Q5': {'EGO': (0.385, 0.0, 1.44), 'position': (0.53, 0.0, 1.11, 10)}, 
                'Chevrolet_Menlo':   {'EGO': (0.41, 0.0, 1.315), 'position': (0.64, 0.0, 1.03, 10)},
                'Lexus_UX':          {'EGO': (0.3198521, 0.0, 1.3166237), 'position': (0.505, 0.02, 0.95, 10)},
                'Porsche_Cayenne':  {'EGO': (0.39, 0.0, 1.495), 'position': (0.60, 0.0, 1.165, 10)},
                'Unbranded_GenericSUV':     {'EGO': (0.3510127, 0.0, 1.46), 'position': (0.58, 0.005, 1.085, 10)},
                'Volkswagen_Passat': {'EGO': (0.45, 0.025, 1.3), 'position': (0.70, 0.027, 1.00, 10)},
                'default':           {'EGO': (0.39, 0.0, 1.495), 'position': (0.60, 0.0, 1.75, 25)}
            },
        }
    },
    "conditions": [ 
        {'Day': True,  'Cond':'sunny',          'Probability': 0.25},
        {'Day': True,  'Cond':'scattered',      'Probability': 0.25},
        {'Day': True,  'Cond':'overcast',       'Probability': 0.25},
        {'Day': False, 'Cond':'interior-lights','Probability': 0.25}
    ],
    "occupant_confs_probabilities": [ 
        {'Conf': 'Empty', 'Probability': 0.0},
        {'Conf': 'Normal', 'Probability': 1.0}
    ],
    "occupancy_distribution": {
        'driver_occupancy_probabilities': [
            {'name': 'Empty',  'occupancy': 0, 'probability': 0.15},
            {'name': 'Driver', 'occupancy': 1, 'probability': 0.85} 
        ],
        'copilot_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.25},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.25},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.25},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.25} 
        ],
        'backseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.25},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.25},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.25},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.25}
        ],
        'middleseat_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.25},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.25},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.25},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.25} 
        ],
        'childseat_type_probabilities': [
            {'Type': 'BabyChild',   'Probability': 0.3},
            {'Type': 'Convertible', 'Probability': 0.3},
            {'Type': 'Booster',     'Probability': 0.3}
        ],
        'childseat_occupied_probability':  0.3,
        'accessories_probabilities': { 'global': 0.5, 'glasses': 0.5, 'headwear': 0.5, 'mask': 0.5 },
        'seatbelts_distribution': {
            'belt_on_probability': 0.95, # Probability for seatbelt on when there is a character seatted on
            'seatbelt_placement_probabilities': {
                'Normal': 0.80,
                'BehindTheBack': 0.05,
                'UnderShoulder': 0.05,
                'WrongSideOfHead': 0.05,
                'CharacterOverSeatbelt': 0.05
            },   
            'belt_on_without_character_probability': 0.2, # Probability for seatbelt on when the seat is empty
        },
        'gaze_probabilities': {
            'driver_gaze_probabilities':  [
                {'name': 'road', 'gaze': 0, 'probability': 0.7},
                {'name': 'ext_mirror', 'gaze': 1, 'probability': 0.1},
                {'name': 'int_mirror', 'gaze': 2, 'probability': 0.05},
                {'name': 'infotainment', 'gaze': 3, 'probability': 0.05},
                {'name': 'passenger', 'gaze': 4, 'probability': 0.1},
                {'name': 'rear', 'gaze': 5, 'probability': 0.0}
            ],
            'copilot_gaze_probabilities': [
                {'name': 'road', 'gaze': 0, 'probability': 0.50},
                {'name': 'ext_mirror', 'gaze': 1, 'probability': 0.05},
                {'name': 'int_mirror', 'gaze': 2, 'probability': 0.1},
                {'name': 'infotainment', 'gaze': 3, 'probability': 0.1},
                {'name': 'passenger', 'gaze': 4, 'probability': 0.2},
                {'name': 'rear', 'gaze': 5, 'probability': 0.05}
            ]
        }
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
icu = incabin.InCabinUtils(workspace, script_console)
workspace.icu = icu

if not hasattr(workspace, 'cars'):
    print('Loading car interiors...')
    workspace.cars = icu.queryCars()
    #print(workspace.cars)
    print('Car list loaded!')
    
if not hasattr(workspace, 'characters'):
    print('Loading characters...')
    workspace.characters = icu.queryCharacters()
    #print(workspace.characters)
    print('Characters list loaded!')

if not hasattr(workspace, 'babies'):
    print('Loading babies...')
    workspace.babies = icu.queryBabies()
    #print(workspace.babies)
    print('Babies list loaded!')
    
if not hasattr(workspace, 'childseats'):
    print('Loading childseats...')
    workspace.childseats = icu.queryChildSeats()
    #print(workspace.childseats)
    print('Childseat list loaded!')
    
if not hasattr(workspace, 'objects'):
    print('Loading objects...')
    workspace.objects = icu.queryObjects()
    #print(workspace.objects)
    print('Objects list loaded!')
    
if not hasattr(workspace, 'accessories'):
    print('Loading accessories...')
    workspace.accessories = icu.queryAccessories()
    #print(workspace.accessories)
    print('Accessories list loaded!')

if not hasattr(workspace, 'backgrounds'):
    print('Loading backgrounds...')
    workspace.backgrounds = icu.queryBackgrounds()
    #print(workspace.backgrounds)
    print('Backgrounds list loaded!')


#__________________________________________________________
# Get the workspace simulation id
simulation_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Simulation)[0]

#__________________________________________________________
# Star setting up the scene for an iteration
print('Iteration: {}'.format(iteration_index))

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
# Pick a ramdom car with preobabilities from list of cars, 
# load it as an asset in the workspace and set it as "the_car" 
# to render. If the car from the list can't be loaded from 
# resources, log an error and keep the current car in the workspace
selected_car = icu.selectCar(use_probs = False)
# selected_car = icu.ï¿¼selectCar(use_probs = False, idx = 0) # picking the Audi Q5
car_name = 'default'
if selected_car['Entity_id'] != -1:
    icu.buildCar(selected_car, the_car)

    # Set car info from car metadata and put it as custom metadata for annotations
    car_info = icu.setCarInfo(selected_car,the_car)
    car_name = '{}_{}'.format(selected_car['brand'], selected_car['model'])
else:
    print('[ERROR] Could not find {} in resources'.format(selected_car))
# Set Eport Always and exclude from occlusion test properties to the car
icu.setExportAlwaysExcludeOcclusion(the_car)
# Set split action to Split to get the seats segmented
icu.setSplitAction(the_car, 'Split')

#__________________________________________________________
# Randomly select the camera to use and place the ego in the camera position

names, probabilities = getCameraProbabilityList(incabin_config)
cam_ids_idx = icu.choiceUsingProbabilities(probabilities)
camera_selected = names[cam_ids_idx]

cam_positions = incabin_config["cameras"][camera_selected]["cam_positions"]

if car_name in cam_positions:
    cam_pos = cam_positions[car_name]['position']
else:
    cam_pos = cam_positions["default"]['position']

cam_position = anyverse_platform.Vector3D( cam_pos[0], cam_pos[1], cam_pos[2] )

# Set an optional initial pitch delta
cam_pitch_delta = cam_pos[3]
ego_pos, ego_rot = icu.setEgoInPosition(cam_pitch_delta, cam_position)
print('Ego initial position: x {}, y {}, z {}'.format(ego_pos.x, ego_pos.y, ego_pos.z))
print('Ego initial rotation: x {}, y {}, z {}'.format(ego_rot.x, ego_rot.y, ego_rot.z))

# Apply caemra vibration simulation with normal distribution
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
Generator_BatchId = workspace.get_entities_by_name('Generator')[0]
if workspace.reduce_resolution and iteration_index == 0:
    print('Reducing all cameras resolution for testing')
    icu.reduceAllCameraResolution(2)
if workspace.testing:
    print('Setting render quality to Medium and denoiser off for testing')
    workspace.set_entity_property_value(Generator_BatchId, 'BatchPropertiesComponent','render_quality','Medium')
    workspace.set_entity_property_value(Generator_BatchId, 'BatchPropertiesComponent','enable_denosier', False)
else:
    print('PRODUCTION!!!!')
    print('Setting render quality to Ultra and denoiser on for production')
    workspace.set_entity_property_value(Generator_BatchId, 'BatchPropertiesComponent','render_quality','Ultra')
    workspace.set_entity_property_value(Generator_BatchId, 'BatchPropertiesComponent','enable_denosier', True)

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
cc_info_locator = icu.createCCLocator(the_car)

# set the illumination depending on day/night and conditions
intensity = icu.setIllumination(day, cond, background, simulation_id, active_light = False)
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

conf_idx = icu.choiceUsingProbabilities([ float(c['Probability']) for c in occupant_confs_probabilities])
if occupant_confs_probabilities[conf_idx]['Conf'] == 'Empty':
    icu.EmptyDistribution(the_car)
elif occupant_confs_probabilities[conf_idx]['Conf'] == 'Normal':
    # occupant_dist = icu.AllAdultsDistribution(the_car)
    occupant_dist = icu.NormalOccupantDistribution(the_car, occupancy_distribution)
    # occupant_dist = icu.ChildseatDistribution(the_car)
    print('Occupant_dist: {}'.format(occupant_dist))

# Set entities visualization mode to Mesh if testing
if workspace.testing:
    fixed_entities = workspace.get_fixed_entities()
        
    for entity_id in fixed_entities:
        if workspace.get_entity_type(entity_id) != 'Locator' and workspace.has_entity_component(entity_id, "Viewport3DEntityConfigurationComponent"):
            print(workspace.get_entity_name(entity_id))
            workspace.set_entity_property_value(entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")
   
print('___________________________________________________')

