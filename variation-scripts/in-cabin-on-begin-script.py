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
    "use_car_interior_probabilities": False,
    "car_interior_probabilities": [
        {'car_name': 'Audi_Q5', 'probability': 0.125 }, 
        {'car_name': 'Chevrolet_Menlo', 'probability': 0.125 },
        {'car_name': 'Lexus_UX', 'probability': 0.125 },
        {'car_name': 'Porsche_Cayenne', 'probability': 0.125 },
        {'car_name': 'Unbranded_GenericSUV', 'probability': 0.125 },
        {'car_name': 'Volkswagen_Passat', 'probability': 0.125 },
        {'car_name': 'Hyundai_Ioniq', 'probability': 0.125 },
        {'car_name': 'LandRover_Autobiography', 'probability': 0.125 }
    ],
    "multiple_cameras": False,
    "nir_at_night": True,
    "rgb_sensor_sim": False,
    "cameras":{
        "RVM": {
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (0, -30, 0), 'position': (0.52, 0.0, 1.45) }, 
                'Chevrolet_Menlo':  {'rotation': (0, -30, 0), 'position': (0.61, 0.0, 1.31) },
                'Lexus_UX':         {'rotation': (0, -30, 0), 'position': (0.53, 0.005, 1.29) },
                'Porsche_Cayenne': {'rotation': (0, -25, 0), 'position': (0.60, 0.0, 1.45) },
                'Unbranded_GenericSUV':    {'rotation': (0, -25, 0), 'position': (0.52, -0.005, 1.43) },
                'Volkswagen_Passat': {'rotation': (0, -30, 0), 'position': (0.60, -0.027, 1.287)},
                'Hyundai_Ioniq': {'rotation': (0, -35, 0), 'position': (0.58, -0.02, 1.315)},
                'LandRover_Autobiography': {'rotation': (0, -30, 0), 'position': (0.50, 0.0, 1.6)},
                'default':          {'rotation': (0, -25, 0), 'position': (0.60, 0.0, 1.75)}
            },
        },
        "CC": { 
            "probability": 1.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (0, -10, 0), 'position': (0.53, 0.0, 1.11)}, 
                'Chevrolet_Menlo':   {'rotation': (0, -10, 0), 'position': (0.64, 0.0, 1.03)},
                'Lexus_UX':          {'rotation': (0, -10, 0), 'position': (0.505, 0.02, 0.95)},
                'Porsche_Cayenne':  {'rotation': (0, -10, 0), 'position': (0.60, 0.0, 1.165)},
                'Unbranded_GenericSUV':     {'rotation': (0, -10, 0), 'position': (0.58, 0.005, 1.085)},
                'Volkswagen_Passat': {'rotation': (0, -10, 0), 'position': (0.70, 0.027, 1.00)},
                'Hyundai_Ioniq': {'rotation': (0, -10, 0), 'position': (0.58, -0.02, 1.09)},
                'LandRover_Autobiography': {'rotation': (0, -10, 0), 'position': (0.63, 0.0, 1.22)},
                'default':           {'rotation': (0, -25, 0), 'position': (0.60, 0.0, 1.75)}
            },
        }
    },
    "conditions": [ 
        {'Day': True,  'Cond':'sunny',          'probability': 0.25},
        {'Day': True,  'Cond':'scattered',      'probability': 0.25},
        {'Day': True,  'Cond':'overcast',       'probability': 0.25},
        {'Day': False, 'Cond':'interior-lights','probability': 0.25}
    ],
    "occupant_confs_probabilities": [ 
        {'Conf': 'Empty', 'probability': 0.0},
        {'Conf': 'Normal', 'probability': 1.0}
    ],
    "occupancy_distribution": {
        'driver_occupancy_probabilities': [
            {'name': 'Empty',  'occupancy': 0, 'probability': 0.0},
            {'name': 'Driver', 'occupancy': 1, 'probability': 1.0} 
        ],
        'copilot_occupancy_probabilities': [
            {'name': 'Empty',     'occupancy': 0, 'probability': 0.1},
            {'name': 'ChildSeat', 'occupancy': 2, 'probability': 0.2},
            {'name': 'Passenger', 'occupancy': 3, 'probability': 0.6},
            {'name': 'Object',    'occupancy': 4, 'probability': 0.1} 
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
        'childseat_config': {
            'childseat_type_probabilities': [
                {'Type': 'BabyChild', 'probability': 0.75},
                {'Type': 'Convertible', 'probability': 0.25},
                {'Type': 'Booster', 'probability': 0.0}
            ],
            'childseat_occupancy_probabilities': [
                {'name': 'Empty', 'occupancy': 0, 'probability': 0.25},
                {'name': 'Child', 'occupancy': 1, 'probability': 0.5},
                {'name': 'Object', 'occupancy': 2, 'probability': 0.25}
            ],
            'childseat_orientation_probabilities': [
                {'Orientation': 'Forward', 'probability': 0.5},
                {'Orientation': 'Backward', 'probability': 0.5}
            ],
            'childseat_rotation_max': 30
        },
        'accessories_probabilities': { 'global': 0.5, 'glasses': 0.5, 'headwear': 0.5, 'mask': 0.5 },
        'seatbelts_distribution': {
            'belt_on_probability': 0.95, # Probability for seatbelt on when there is a character seatted on
            'seatbelt_placement_probabilities': {
                'Normal': 0.70,
                'BehindTheBack': 0.05,
                'UnderShoulder': 0.05,
                'WrongSideOfHead': 0.05,
                'CharacterOverSeatbelt': 0.05,
                'LapBeltUnder': 0.05,
                'UnderShoulderLapBeltUnder': 0.05
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
icu = incabin.InCabinUtils(workspace, script_console)
workspace.icu = icu

if not hasattr(anyverse_platform, 'cars'):
    print('Loading car interiors...')
    anyverse_platform.cars = icu.queryCars()
    #print(anyverse_platform.cars)
    print('Car list loaded!')
workspace.cars = anyverse_platform.cars
    
if not hasattr(anyverse_platform, 'characters'):
    print('Loading characters...')
    anyverse_platform.characters = icu.queryCharacters()
    #print(anyverse_platform.characters)
    print('Characters list loaded!')
workspace.characters = anyverse_platform.characters

if not hasattr(anyverse_platform, 'babies'):
    print('Loading babies...')
    anyverse_platform.babies = icu.queryBabies()
    #print(anyverse_platform.babies)
    print('Babies list loaded!')
workspace.babies = anyverse_platform.babies
    
if not hasattr(anyverse_platform, 'childseats'):
    print('Loading childseats...')
    anyverse_platform.childseats = icu.queryChildSeats()
    #print(anyverse_platform.childseats)
    print('Childseat list loaded!')
workspace.childseats = anyverse_platform.childseats
    
if not hasattr(anyverse_platform, 'childseatbelts'):
    print('Loading childseatbelts...')
    anyverse_platform.childseatbelts = icu.queryChildSeatBelts()
    #print(anyverse_platform.childseatbelts)
    print('Childseatbelts list loaded!')
workspace.childseatbelts = anyverse_platform.childseatbelts
    
if not hasattr(anyverse_platform, 'objects'):
    print('Loading objects...')
    anyverse_platform.objects = icu.queryObjects()
    #print(anyverse_platform.objects)
    print('Objects list loaded!')
workspace.objects = anyverse_platform.objects
    
if not hasattr(anyverse_platform, 'accessories'):
    print('Loading accessories...')
    anyverse_platform.accessories = icu.queryAccessories()
    #print(anyverse_platform.accessories)
    print('Accessories list loaded!')
workspace.accessories = anyverse_platform.accessories

if not hasattr(anyverse_platform, 'backgrounds'):
    print('Loading backgrounds...')
    anyverse_platform.backgrounds = icu.queryBackgrounds()
    #print(anyverse_platform.backgrounds)
    print('Backgrounds list loaded!')
workspace.backgrounds = anyverse_platform.backgrounds

if not hasattr(anyverse_platform, 'materials'):
    print('Loading materials...')
    anyverse_platform.materials = icu.queryMaterials()
    #print(anyverse_platform.materials)
    print('Materials list loaded!')
workspace.materials = anyverse_platform.materials

#__________________________________________________________
# Get the workspace simulation id
simulation_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Simulation)[0]
generator_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Batch)[0]

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
if incabin_config['use_car_interior_probabilities']:
    car_probabilities = incabin_config['car_interior_probabilities']
    selected_car = icu.selectCar(car_probabilities)
else:
    selected_car = icu.selectCar() # Uniform car interior distribution
car_name = 'default'
if selected_car['entity_id'] != -1:
    icu.buildCar(selected_car, the_car)

    # Set car info from car metadata and put it as custom metadata for annotations
    car_info = icu.setCarInfo(selected_car,the_car)
    car_name = '{}_{}'.format(selected_car['brand'].replace(" ",""), selected_car['model'])
else:
    print('[ERROR] Could not find {} in resources'.format(selected_car))
# Set Eport Always and exclude from occlusion test properties to the car
icu.setExportAlwaysExcludeOcclusion(the_car)
# Set split action to Split to get the seats segmented
icu.setSplitAction(the_car, 'Split')

#__________________________________________________________
# Reset Ego, cameras and light position at origin with rotations 
icu.resetEgo()
icu.resetCameras()
icu.resetLights()
cameras = incabin_config["cameras"]
# Global camera settings
multiple_cameras = incabin_config["multiple_cameras"]
nir_simulation = incabin_config["nir_at_night"]
rgb_sensor_sim = incabin_config["rgb_sensor_sim"]
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
        light_ids = [ li for li in workspace.get_entities_by_type('Light') if camera in workspace.get_entity_name(li) ]
        light_id = light_ids[0] if len(light_ids) == 1 else 0
        if light_id != 0:
            light_pos, _ = icu.setActiveLightInPosition(light_id, cam_position, cam_rotation)
            if camera == 'RVM':
                # Advance the light 10 cm to avoid rvm casted shadows
                light_pos.x += 0.1
                workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', light_pos)
        else:
            print('[WARN] Missing light for {} camera in workspace'.format(camera))
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

    # Advance the light 10 cm to avoid rvm casted shadows
    light_pos = anyverse_platform.Vector3D(0.1, 0, 0)
    incabin_lights = workspace.get_entities_by_type('Light')
    if len(incabin_lights) > 0:
        incabin_light = incabin_lights[0]
    workspace.set_entity_property_value(incabin_light, 'RelativeTransformToComponent','position', light_pos)

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
    print('Setting render quality to Medium and denoiser off for testing')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','render_quality','Medium')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','enable_denosier', False)
else:
    print('PRODUCTION!!!!')
    print('Setting render quality to Ultra and denoiser on for production')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','render_quality','Ultra')
    workspace.set_entity_property_value(generator_id, 'BatchPropertiesComponent','enable_denosier', True)

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

# Set NIR sensor and NIR ISP for night scenes. Unset it for the rest
if multiple_cameras:
    camera_ids = workspace.get_camera_entities()
    for camera_id in camera_ids:
        if not day and nir_simulation:
            icu.setSensor(camera_id, 'NIR-Sensor')
            icu.setIsp(camera_id, 'NIR-ISP')
            active_light = True
            sensor_enabled = True
        elif rgb_sensor_sim:
            icu.setSensor(camera_id, 'RGB-Sensor')
            icu.setIsp(camera_id, 'RGB-ISP')
            active_light = False
            sensor_enabled = True
        else:
            icu.setSensor(camera_id, None)
            icu.setIsp(camera_id, None)
            active_light = False
            sensor_enabled = False
else:
    if not day and nir_simulation:
        icu.setSensor(camera_id, 'NIR-Sensor')
        icu.setIsp(camera_id, 'NIR-ISP')
        active_light = True
        sensor_enabled = True
    elif rgb_sensor_sim:
        icu.setSensor(camera_id, 'RGB-Sensor')
        icu.setIsp(camera_id, 'RGB-ISP')
        active_light = False
        sensor_enabled = True
    else:
        icu.setSensor(camera_id, None)
        icu.setIsp(camera_id, None)
        active_light = False
        sensor_enabled = False

print('Sensor enabled? {}. Setting active lights to {}'.format(sensor_enabled, active_light))
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
    icu.EmptyDistribution(the_car)
elif occupant_confs_probabilities[conf_idx]['Conf'] == 'Normal':
    # occupant_dist = icu.AllAdultsDistribution(the_car)
    occupant_dist = icu.NormalOccupantDistribution(the_car, occupancy_distribution)
    # occupant_dist = icu.ChildseatDistribution(the_car)
    print('Occupant_dist: {}'.format(occupant_dist))

# Set entities visualization mode to Mesh if testing
if workspace.testing or script_console:
    fixed_entities = workspace.get_fixed_entities()
        
    for entity_id in fixed_entities:
        if workspace.get_entity_type(entity_id) != 'Locator' and workspace.has_entity_component(entity_id, "Viewport3DEntityConfigurationComponent"):
            print(workspace.get_entity_name(entity_id))
            workspace.set_entity_property_value(entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")
   
print('___________________________________________________')

