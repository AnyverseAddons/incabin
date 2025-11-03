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
    "use_car_interior_probabilities": True, # set to True with uniform probabilities to avoid new car cabins until we add them to the config
    "adjust_front_seats": False,
    "car_interior_probabilities": [
        {'car_name': 'Audi_Q5', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False }, 
        {'car_name': 'Chevrolet_Menlo', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Lexus_UX', 'probability': 0.0, 'front_seat_max_depth': 0.05, 'front_seat_max_tilt': 0, 'normal_dist': False },
        {'car_name': 'Porsche_CayenneS', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Unbranded_GenericSUV', 'probability': 0.0, 'front_seat_max_depth': 0.07, 'front_seat_max_tilt': 2, 'normal_dist': False },
        {'car_name': 'Volkswagen_Passat', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Hyundai_Ioniq', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'LandRover_Autobiography', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Ford_Escape', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Honda_Jazz', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Kia_EV6_GT', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'MercedesBenz_EQE', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Buick_Lacrosse', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Peugeot_3008', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Tesla_S', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Venucia_Star', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Nio_ES6', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'BMW_X5', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Cadillac_XT5', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Honda_CRV', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Volkswagen_ID3', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'BYD_Atto_3', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Geely_Geometry_E', 'probability': 1.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Jaguar_I_Pace', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Reanult_Austral', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False },
        {'car_name': 'Volvo_EM90', 'probability': 0.0, 'front_seat_max_depth': 0.1, 'front_seat_max_tilt': 5, 'normal_dist': False }
    ],
    "multiple_cameras": True,
    "use_nir": True,
    "rgb_at_day": False, # Override the use of NIR sensor for day light
    "cameras": {
        "APillar-L": {
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (-81, 0, 106), 'position': (0.72, 0.67, 1.19) }, 
                'Chevrolet_Menlo':  {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05) },
                'Lexus_UX':         {'rotation': (-90, 0, 103), 'position': (0.57, 0.64, 1.09) },
                'Porsche_CayenneS': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05) },
                'Unbranded_GenericSUV':    {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05) },
                'Volkswagen_Passat': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Hyundai_Ioniq': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'LandRover_Autobiography': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Ford_Escape': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Honda_Jazz': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Kia_EV6_GT': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'MercedesBenz_EQE': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Buick_LaCrosse': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Peugeot_3008': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Tesla_S': {'rotation': (-88, 0, 107), 'position': (0.77, 0.65, 1.05)},
                'Venucia_Star': {'rotation': (-90, 0, 107), 'position': (0.72, 0.68, 1.18)},
                'Nio_ES6': {'rotation': (-88, 0, 108), 'position': (0.76, 0.75, 1.19)},
                'BMW_X5': {'rotation': (-85, 0, 104), 'position': (0.74, 0.71, 1.21) }, 
                'Cadillac_XT5': {'rotation': (-99, 0, 102), 'position': (0.59, 0.66, 1.35) }, 
                'Honda_CRV': {'rotation': (-89, 0, 104), 'position': (0.64, 0.69, 1.22) }, 
                'Volkswagen_ID3': {'rotation': (-89, 0, 110), 'position': (0.66, 0.67, 1.06) }, 
                'BYD_Atto_3': {'rotation': (-96, 0, 105), 'position': (0.58, 0.64, 1.25) }, 
                'Geely_Geometry_E': {'rotation': (-97, 0, 105), 'position': (0.59, 0.58, 1.22) }, 
                'default':          {'rotation': (-110, 0, 115), 'position': (0.29, 0.60, 1.49)}
            },
        },
        "SColumn": {
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (112, 180, -90), 'position': (0.48, 0.40, 1.10) }, 
                'Chevrolet_Menlo':  {'rotation': (112, 180, -90), 'position': (0.585, 0.38, 0.99) },
                'Lexus_UX':         {'rotation': (110, 180, -90), 'position': (0.41, 0.37, 0.96) },
                'Porsche_CayenneS': {'rotation': (99, 180, -90), 'position': (0.59, 0.42, 1.20) },
                'Unbranded_GenericSUV':    {'rotation': (106, 180, -90), 'position': (0.50, 0.37, 1.095) },
                'Volkswagen_Passat': {'rotation': (112, 180, -90), 'position': (0.68, 0.36, 0.95)},
                'Hyundai_Ioniq': {'rotation': (110, 180, -90), 'position': (0.54, 0.36, 1.035)},
                'LandRover_Autobiography': {'rotation': (110, 180, -90), 'position': (0.57, 0.43, 1.25)},
                'Ford_Escape': {'rotation': (115, 180, -90), 'position': (0.50, 0.36, 1.07)},
                'Honda_Jazz': {'rotation': (112, 180, -90), 'position': (0.50, 0.33, 0.93)},
                'Kia_EV6_GT': {'rotation': (112, 180, -90), 'position': (0.60, 0.39, 1.08)},
                'MercedesBenz_EQE': {'rotation': (112, 180, -90), 'position': (0.52, 0.47, 1.13)},
                'Buick_LaCrosse': {'rotation': (112, 180, -90), 'position': (0.61, 0.43, 1.03)},
                'Peugeot_3008': {'rotation': (120, 180, -90), 'position': (0.50, 0.36, 1.08)},
                'Tesla_S': {'rotation': (112, 180, -90), 'position': (0.51, 0.415, 0.89)},
                'Venucia_Star': {'rotation': (109, 180, -90), 'position': (0.60, 0.39, 1.13)},
                'Nio_ES6': {'rotation': (106, 180, -90), 'position': (0.52, 0.43, 1.12)},
                'BMW_X5': {'rotation': (99, 180, -90), 'position': (0.54, 0.46, 1.16) },
                'Cadillac_XT5': {'rotation': (99, 180, -90), 'position': (0.45, 0.42, 1.12) },
                'Honda_CRV': {'rotation': (100, 180, -90), 'position': (0.43, 0.40, 1.11) },
                'Volkswagen_ID3': {'rotation': (100, 180, -90), 'position': (0.51, 0.335, 1.035) },
                'BYD_Atto_3': {'rotation': (100, 180, -90), 'position': (0.49, 0.36, 1.045) },
                'Geely_Geometry_E': {'rotation': (102, 180, -93), 'position': (0.42, 0.315, 1.01) },
                'default':          {'rotation': (112, 180, -90), 'position': (-0.40, -0.53, 1.35)}
            },
        },
        "BPillar-R": {
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (45, 180, 229), 'position': (-0.46, -0.55, 1.49) }, 
                'Chevrolet_Menlo':  {'rotation': (45, 180, 230), 'position': (-0.31, -0.55, 1.40) },
                'Lexus_UX':         {'rotation': (50, 180, 230), 'position': (-0.50, -0.53, 1.35) },
                'Porsche_CayenneS': {'rotation': (47, 180, 228), 'position': (-0.45, -0.55, 1.57) },
                'Unbranded_GenericSUV':    {'rotation': (46, 180, 230), 'position': (-0.44, -0.58, 1.50) },
                'Volkswagen_Passat': {'rotation': (50, 180, 231), 'position': (-0.33, -0.53, 1.34)},
                'Hyundai_Ioniq': {'rotation': (50, 180, 230), 'position': (-0.38, -0.56, 1.34)},
                'LandRover_Autobiography': {'rotation': (47, 180, 230), 'position': (-0.45, -0.60, 1.70)},
                'Ford_Escape': {'rotation': (50, 180, 230), 'position': (-0.39, -0.55, 1.45)},
                'Honda_Jazz': {'rotation': (44, 180, 230), 'position': (-0.45, -0.50, 1.33)},
                'Kia_EV6_GT': {'rotation': (50, 180, 230), 'position': (-0.42, -0.54, 1.39)},
                'MercedesBenz_EQE': {'rotation': (50, 180, 230), 'position': (-0.405, -0.61, 1.53)},
                'Buick_LaCrosse': {'rotation': (50, 180, 230), 'position': (-0.42, -0.64, 1.39)},
                'Peugeot_3008': {'rotation': (45, 180, 230), 'position': (-0.43, -0.55, 1.49)},
                'Tesla_S': {'rotation': (50, 180, 230), 'position': (-0.46, -0.60, 1.27)},
                'Venucia_Star': {'rotation': (48, 180, 228), 'position': (-0.39, -0.58, 1.54)},
                'Nio_ES6': {'rotation': (50, 180, 230), 'position': (-0.40, -0.56, 1.55)},
                'BMW_X5': {'rotation': (45, 180, 226), 'position': (-0.38, -0.60, 1.62) },
                'Cadillac_XT5': {'rotation': (45, 180, 226), 'position': (-0.38, -0.60, 1.62) },
                'default':          {'rotation': (65, 180, 180), 'position': (-0.40, -0.53, 1.35)}
            },
        },
        "BPillar-L": {
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (45, 180, -49), 'position': (-0.46, 0.55, 1.49) }, 
                'Chevrolet_Menlo':  {'rotation': (45, 180, -50), 'position': (-0.31, 0.55, 1.40) },
                'Lexus_UX':         {'rotation': (50, 180, -50), 'position': (-0.50, 0.53, 1.35) },
                'Porsche_CayenneS': {'rotation': (47, 180, -48), 'position': (-0.45, 0.55, 1.57) },
                'Unbranded_GenericSUV':    {'rotation': (46, 180, -50), 'position': (-0.44, 0.58, 1.50) },
                'Volkswagen_Passat': {'rotation': (50, 180, -51), 'position': (-0.33, 0.53, 1.34)},
                'Hyundai_Ioniq': {'rotation': (50, 180, -50), 'position': (-0.38, 0.56, 1.34)},
                'LandRover_Autobiography': {'rotation': (47, 180, -50), 'position': (-0.45, 0.60, 1.70)},
                'Ford_Escape': {'rotation': (50, 180, -50), 'position': (-0.39, 0.55, 1.45)},
                'Honda_Jazz': {'rotation': (44, 180, -50), 'position': (-0.45, 0.50, 1.33)},
                'Kia_EV6_GT': {'rotation': (50, 180, -50), 'position': (-0.42, 0.54, 1.39)},
                'MercedesBenz_EQE': {'rotation': (50, 180, -50), 'position': (-0.405, 0.61, 1.53)},
                'Buick_LaCrosse': {'rotation': (50, 180, -50), 'position': (-0.42, 0.64, 1.39)},
                'Peugeot_3008': {'rotation': (45, 180, -50), 'position': (-0.43, 0.55, 1.49)},
                'Tesla_S': {'rotation': (50, 180, -50), 'position': (-0.46, 0.60, 1.27)},
                'Venucia_Star': {'rotation': (48, 180, -48), 'position': (-0.39, 0.58, 1.54)},
                'Nio_ES6': {'rotation': (50, 180, -50), 'position': (-0.40, 0.56, 1.55)},
                'BMW_X5': {'rotation': (45, 180, -46), 'position': (-0.38, 0.60, 1.62) },
                'Cadillac_XT5': {'rotation': (45, 180, -46), 'position': (-0.38, 0.60, 1.62) },
                'default':          {'rotation': (65, 180, 0), 'position': (-0.40, 0.53, 1.35)}
            },
        },
        "FRL": {
            "on_for_multicamera": True,
            "probability": 1.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (35, 180, -90), 'position': (0.045, 0.0, 1.54) }, 
                'Chevrolet_Menlo':  {'rotation': (40, 180, -90), 'position': (0.25, 0.0, 1.395) },
                'Lexus_UX':         {'rotation': (40, 180, -90), 'position': (0.08, 0.0, 1.37) },
                'Porsche_CayenneS': {'rotation': (40, 180, -90), 'position': (0.10, 0.0, 1.52) },
                'Unbranded_GenericSUV':    {'rotation': (40, 180, -90), 'position': (0.24, 0, 1.51) },
                'Volkswagen_Passat': {'rotation': (44, 180, -90), 'position': (0.24, 0.0, 1.35)},
                'Hyundai_Ioniq': {'rotation': (40, 180, -90), 'position': (0.21, 0.0, 1.36)},
                'LandRover_Autobiography': {'rotation': (40, 180, -90), 'position': (0.22, 0.0, 1.68)},
                'Ford_Escape': {'rotation': (43, 180, -90), 'position': (0.23, 0.0, 1.478)},
                'Honda_Jazz': {'rotation': (40, 180, -90), 'position': (0.18, 0.0, 1.32)},
                'Kia_EV6_GT': {'rotation': (42, 180, -90), 'position': (0.18, 0.0, 1.43)},
                'MercedesBenz_EQE': {'rotation': (44, 180, -90), 'position': (0.24, 0.0, 1.54)},
                'Buick_LaCrosse': {'rotation': (30, 180, -90), 'position': (0.21, 0.0, 1.40)},
                'Peugeot_3008': {'rotation': (40, 180, -90), 'position': (0.26, 0.0, 1.46)},
                'Tesla_S': {'rotation': (45, 180, -90), 'position': (0.16, 0.0, 1.24)},
                'Venucia_Star': {'rotation': (40, 180, -90), 'position': (0.25, 0.0, 1.53)},
                'Nio_ES6': {'rotation': (25, 180, -90), 'position': (0.21, 0.0, 1.54)},
                'BMW_X5': {'rotation': (40, 180, -90), 'position': (0.17, 0.0, 1.65) },
                'Cadillac_XT5': {'rotation': (40, 180, -90), 'position': (0.17, 0.0, 1.65) },
                'Honda_CRV': {'rotation': (55, 180, -90), 'position': (0.30, 0.0, 1.49) },
                'Volkswagen_ID3': {'rotation': (55, 180, -90), 'position': (0.30, 0.0, 1.49) },
                'default':          {'rotation': (65, 180, -90), 'position': (0.60, 0.0, 1.75)}
            },
        },
        "RVM": {
            "on_for_multicamera": True,
            "probability": 1.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (57, 180, -90), 'position': (0.38, 0.0, 1.42) }, 
                'Chevrolet_Menlo':  {'rotation': (52, 180, -90), 'position': (0.33, 0.0, 1.33) },
                'Lexus_UX':         {'rotation': (55, 180, -90), 'position': (0.35, 0.005, 1.31) },
                'Porsche_CayenneS': {'rotation': (55, 180, -90), 'position': (0.50, 0.0, 1.45) },
                'Unbranded_GenericSUV':    {'rotation': (50, 180, -90), 'position': (0.485, -0.005, 1.43) },
                'Volkswagen_Passat': {'rotation': (50, 180, -90), 'position': (0.44, 0.0, 1.31)},
                'Hyundai_Ioniq': {'rotation': (50, 180, -90), 'position': (0.45, -0.02, 1.315)},
                'LandRover_Autobiography': {'rotation': (50, 180, -90), 'position': (0.41, 0.0, 1.58)},
                'Ford_Escape': {'rotation': (55, 180, -90), 'position': (0.42, 0.0, 1.37)},
                'Honda_Jazz': {'rotation': (50, 180, -90), 'position': (0.35, 0.0, 1.3)},
                'Kia_EV6_GT': {'rotation': (55, 180, -90), 'position': (0.41, 0.0, 1.40)},
                'MercedesBenz_EQE': {'rotation': (52, 180, -90), 'position': (0.395, 0.0, 1.49)},
                'Buick_LaCrosse': {'rotation': (55, 180, -90), 'position': (0.36, 0.0, 1.34)},
                'Peugeot_3008': {'rotation': (50, 180, -90), 'position': (0.30, 0.0, 1.42)},
                'Tesla_S': {'rotation': (50, 180, -90), 'position': (0.32, 0.0, 1.22)},
                'Venucia_Star': {'rotation': (57, 180, -90), 'position': (0.46, 0.0, 1.44)},
                'Nio_ES6': {'rotation': (51, 180, -90), 'position': (0.34, 0.0, 1.50)},
                'BMW_X5': {'rotation': (51, 180, -90), 'position': (0.41, 0.0, 1.53) },
                'Cadillac_XT5': {'rotation': (53, 180, -90), 'position': (0.395, 0.0, 1.48) },
                'Honda_CRV': {'rotation': (56, 180, -90), 'position': (0.46, 0.0, 1.44) },
                'Volkswagen_ID3': {'rotation': (50, 180, -90), 'position': (0.38, 0.0, 1.38) },
                'BYD_Atto_3': {'rotation': (55, 180, -90), 'position': (0.415, 0.0, 1.38) },
                'Geely_Geometry_E': {'rotation': (55, 180, -90), 'position': (0.375, 0.0, 1.42) },
                'default':          {'rotation': (65, 180, -90), 'position': (0.60, 0.0, 1.75)}
            },
        },
        "CC": { 
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (80, 180, -90), 'position': (0.53, 0.0, 1.11)}, 
                'Chevrolet_Menlo':   {'rotation': (80, 180, -90), 'position': (0.64, 0.0, 1.03)},
                'Lexus_UX':          {'rotation': (80, 180, -90), 'position': (0.505, 0.02, 0.95)},
                'Porsche_CayenneS':  {'rotation': (80, 180, -90), 'position': (0.60, 0.0, 1.165)},
                'Unbranded_GenericSUV':     {'rotation': (80, 180, -90), 'position': (0.58, 0.005, 1.085)},
                'Volkswagen_Passat': {'rotation': (80, 180, -90), 'position': (0.70, 0.027, 1.00)},
                'Hyundai_Ioniq': {'rotation': (80, 180, -90), 'position': (0.58, -0.02, 1.09)},
                'LandRover_Autobiography': {'rotation': (80, 180, -90), 'position': (0.63, 0.0, 1.22)},
                'Ford_Escape': {'rotation': (80, 180, -90), 'position': (0.51, 0.0, 1.21)},
                'Honda_Jazz': {'rotation': (80, 180, -90), 'position': (0.58, 0.0, 1.03)},
                'Kia_EV6_GT': {'rotation': (80, 180, -90), 'position': (0.65, 0.0, 1.175)},
                'MercedesBenz_EQE': {'rotation': (80, 180, -90), 'position': (0.63, 0.0, 1.18)},
                'Buick_LaCrosse': {'rotation': (80, 180, -90), 'position': (0.66, 0.0, 1.03)},
                'Peugeot_3008': {'rotation': (70, 180, -90), 'position': (0.58, 0.0, 1.23)},
                'Tesla_S': {'rotation': (80, 180, -90), 'position': (0.61, 0.0, 0.98)},
                'Venucia_Star': {'rotation': (75, 180, -90), 'position': (0.66, 0.0, 1.19)},
                'Nio_ES6': {'rotation': (80, 180, -90), 'position': (0.66, 0.0, 1.17)},
                'BMW_X5':  {'rotation': (80, 180, -90), 'position': (0.71, 0.065, 1.18)},
                'Cadillac_XT5':  {'rotation': (80, 180, -90), 'position': (0.55, 0.065, 1.15)},
                'Honda_CRV':  {'rotation': (73, 180, -90), 'position': (0.58, 0.0, 1.21)},
                'Volkswagen_ID3':  {'rotation': (75, 180, -90), 'position': (0.63, 0.0, 1.08)},
                'BYD_Atto_3':  {'rotation': (76, 180, -90), 'position': (0.64, 0.0, 1.10)},
                'Geely_Geometry_E':  {'rotation': (74, 180, -90), 'position': (0.53, 0.0, 1.065)},
                'default':           {'rotation': (65, -180, -90), 'position': (0.60, 0.0, 1.75)}
            },
        },
        "2ROW": { 
            "on_for_multicamera": True,
            "probability": 0.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (50, 180, 90), 'position': (-1.20, 0.0, 1.50)},
                'default':           {'rotation': (65, -180, -90), 'position': (0.60, 0.0, 1.75)}
            },
        }
    },
    "multiple_radars": True,
    "radars": {
        "FRL": {
            "on_for_multiradar": False,
            "probability": 1.0,
            "radar_positions": {
                'Audi_Q5': {'rotation': (-145,0,90), 'position': (0.045, 0.0, 1.54) }, 
                'Chevrolet_Menlo':  {'rotation': (-140,0,90), 'position': (0.25, 0.0, 1.395) },
                'Venucia_Star':  {'rotation': (-140,0,90), 'position': (0.22, 0.0, 1.53) },
                'Nio_ES6':  {'rotation': (-145,0,90), 'position': (0.10, 0.0, 1.57) },
                'BMW_X5': {'rotation': (-145,0,90), 'position': (0.17, 0.0, 1.65) }, 
                'default':          {'rotation': (0, 0, 0), 'position': (0, 0, 0)}
            },
        },
        "RVM": {
            "on_for_multiradar": False,
            "probability": 1.0,
            "radar_positions": {
                'Audi_Q5': {'rotation': (-140,0,90), 'position': (0.38, 0.0, 1.42) }, 
                'Chevrolet_Menlo':  {'rotation': (-140,0,90), 'position': (0.31, 0.0, 1.315) },
                'Lexus_UX':  {'rotation': (-140,0,90), 'position': (0.35, 0.005, 1.31) },
                'Porsche_CayenneS':  {'rotation': (-140,0,90), 'position': (0.50, 0.0, 1.45) },
                'Volkswagen_Passat':  {'rotation': (-140,0,90), 'position': (0.44, 0.0, 1.31) },
                'Hyundai_Ioniq':  {'rotation': (-140,0,90), 'position': (0.45, -0.02, 1.315) },
                'LandRover_Autobiography':  {'rotation': (-140,0,90), 'position': (0.41, 0.0, 1.58) },
                'Ford_Escape':  {'rotation': (-140,0,90), 'position': (0.42, 0.0, 1.37) },
                'Honda_Jazz':  {'rotation': (-140,0,90), 'position': (0.35, 0.0, 1.3) },
                'Kia_EV6_GT':  {'rotation': (-140,0,90), 'position': (0.41, 0.0, 1.40) },
                'MercedesBenz_EQE':  {'rotation': (-140,0,90), 'position': (0.395, 0.0, 1.49) },
                'Buick_LaCrosse':  {'rotation': (-140,0,90), 'position': (0.36, 0.0, 1.34) },
                'Peugeot_3008':  {'rotation': (-140,0,90), 'position': (0.30, 0.0, 1.42) },
                'Tesla_S':  {'rotation': (-140,0,90), 'position': (0.32, 0.0, 1.22) },
                'Venucia_Star':  {'rotation': (-140,0,90), 'position': (0.44, 0.0, 1.46) },
                'Nio_ES6':  {'rotation': (-140,0,90), 'position': (0.33, 0.0, 1.52) },
                'BMW_X5': {'rotation': (-140,0,90), 'position': (0.41, 0.0, 1.53) }, 
                'Cadillac_XT5': {'rotation': (-140,0,90), 'position': (0.395, 0.0, 1.48) }, 
                'Honda_CRV': {'rotation': (-140,0,90), 'position': (0.40, 0.0, 1.54) }, 
                'Volkswagen_ID3': {'rotation': (-140,0,90), 'position': (0.38, 0.0, 1.38) }, 
                'BYD_Atto_3': {'rotation': (-140,0,90), 'position': (0.375, 0.0, 1.42) }, 
                'Geely_Geometry_E': {'rotation': (-140,0,90), 'position': (0.415, 0.0, 1.38) }, 
                'default': {'rotation': (0, 0, 0), 'position': (0, 0, 0)}
            },
        },
        "Ceiling": { 
            "on_for_multiradar": False,
            "probability": 0.0,
            "radar_positions": {
                'Audi_Q5': {'rotation': (0, 180, -90), 'position': (-0.4, 0.0, 1.605)}, 
                'Chevrolet_Menlo':   {'rotation': (0, 180, -90), 'position': (-0.3, 0.0, 1.49)},
                'Lexus_UX':   {'rotation': (0, 180, -90), 'position': (-0.48, 0.0, 1.45)},
                'Porsche_CayenneS':   {'rotation': (0, 180, -90), 'position': (-0.41, 0.0, 1.61)},
                'Volkswagen_Passat':   {'rotation': (0, 180, -90), 'position': (-0.31, 0.0, 1.47)},
                'Hyundai_Ioniq':   {'rotation': (0, 180, -90), 'position': (-0.33, 0.0, 1.45)},
                'LandRover_Autobiography':   {'rotation': (0, 180, -90), 'position': (-0.37, 0.0, 1.80)},
                'Ford_Escape':   {'rotation': (0, 180, -90), 'position': (-0.34, 0.0, 1.61)},
                'Honda_Jazz':   {'rotation': (0, 180, -90), 'position': (-0.36, 0.0, 1.42)},
                'Kia_EV6_GT':   {'rotation': (0, 180, -90), 'position': (-0.37, 0.0, 1.50)},
                'MercedesBenz_EQE':   {'rotation': (0, 180, -90), 'position': (-0.37, 0.0, 1.69)},
                'Buick_LaCrosse':   {'rotation': (0, 180, -90), 'position': (-0.31, 0.0, 1.50)},
                'Peugeot_3008':   {'rotation': (0, 180, -90), 'position': (-0.31, 0.0, 1.59)},
                'Tesla_S':   {'rotation': (0, 180, -90), 'position': (-0.58, 0.0, 1.35)},
                'Venucia_Star':   {'rotation': (0, 180, -90), 'position': (-0.33, 0.0, 1.65)},
                'Nio_ES6':   {'rotation': (0, 180, -90), 'position': (-0.64, 0.0, 1.67)},
                'BMW_X5': {'rotation': (0, 180, -90), 'position': (0.345, 0.0, 1.72)}, 
                'Cadillac_XT5': {'rotation': (0, 180, -90), 'position': (0.36, 0.0, 1.65)}, 
                'Honda_CRV': {'rotation': (0, 180, -90), 'position': (0.345, 0.0, 1.72)}, 
                'Volkswagen_ID3': {'rotation': (0, 180, -90), 'position': (0.29, 0.0, 1.565)}, 
                'BYD_Atto_3': {'rotation': (0, 180, -90), 'position': (0.37, 0.0, 1.61)}, 
                'Geely_Geometry_E': {'rotation': (0, 180, -90), 'position': (0.37, 0.0, 1.61)}, 
                'default': {'rotation': (0, 0, 0), 'position': (0, 0, 0)}  
            },
        }
    },
    "conditions": [ 
        {'Day': True,  'interior-lights':True,  'probability': 1.0},
        {'Day': False, 'interior-lights':True,  'probability': 0.0}
    ]
}

#__________________________________________
#      
#            ON BEGIN ITERATION
#__________________________________________
import random
import math
import re
import json
import os
import importlib
from incabin import incabin
importlib.reload(incabin)

# Function to place a camera in a car, specified by car_name in the 
# position specified by camera, which is the camera id in the cameras
# dictionary that comes from the incabin_config dictionary.
# The function places the associated active lights in the same position
# and orientation.
# We assume that there is a locator with the key 'LED' and the camera id
# in the name.
#_____________________________________________________________________
def isOMSCamera(cam_name):
    OMS_cameras = ['RVM', 'BPillar', 'CC', 'FRL']
    return cam_name in OMS_cameras

#_____________________________________________________________________
def isDMSCamera(cam_name):
    DMS_cameras = ['SColumn Camera', 'APillar-L Camera']
    return cam_name in DMS_cameras

#_____________________________________________________________________
def isSegmentedCar(car):
    segmented_brands = ['Audi', 'Chevrolet', 'Lexus', 'Porsche', 'Hyundai', 'Land Rover', 'Kia', 'Venucia', 'Nio', 'BMW', 'Volkswagen', 'Cadillac', 'Honda', 'Peugeot', 'Ford', 'MercedesBenz', 'Tesla', 'Buick']
    is_segmented = True if car['brand'] in segmented_brands else False
    return is_segmented

#_____________________________________________________________________
def placeCameraAndLights(car_name, camera, cameras, on = True, interior_lights = True):

    cam_positions = cameras[camera]["cam_positions"]
    if car_name in cam_positions:
        cam_pos = cam_positions[car_name]['position']
        cam_rot = cam_positions[car_name]['rotation']
    else:
        cam_pos = cam_positions["default"]['position']
        cam_rot = cam_positions["default"]['rotation']
    cam_loc_position = anyverse_platform.Vector3D( cam_pos[0], cam_pos[1], cam_pos[2] )
    cam_loc_rotation = anyverse_platform.Vector3D( cam_rot[0], cam_rot[1], cam_rot[2] )

    # place camera locators in the cam position.
    # There should be a locator under the cabin with the key 'CAM' and the camera prefix in the name 
    # with active lights and cameras
    the_cabin = icu.getCars()[0]
    cam_loc_ids = [ li for li in icu.getCabinCameraLocators(the_cabin,'CAM') if re.match(camera, workspace.get_entity_name(li)) ]
    # cam_loc_id = cam_loc_ids[0] if len(cam_loc_ids) >= 1 else 0
    for cam_loc_id in cam_loc_ids:
        cam_loc_pos, _ = icu.setCameraLocatorInPosition(cam_loc_id, cam_loc_position, cam_loc_rotation)
        cam_ids = [ c for c in workspace.get_hierarchy(cam_loc_id) if 'Camera' == workspace.get_entity_type(c) ]
        if len(cam_ids) == 0:
            print('[WARN] No cameras in cam locator {}'.format(workspace.get_entity_name(cam_loc_id)))
        for cam_id in cam_ids:
            workspace.set_entity_property_value(cam_id, 'VisibleComponent','visible', on)

        light_ids = [ li for li in workspace.get_hierarchy(cam_loc_id) if 'Light' == workspace.get_entity_type(li) ]
        if len(light_ids) == 0:
            print('[INFO] No active lights in cam locator {}'.format(workspace.get_entity_name(cam_loc_id)))
        for light_id in light_ids:
            workspace.set_entity_property_value(light_id, 'VisibleComponent','visible', on)
    else:
        print('[WARN] Missing CAM locator for {} camera in workspace'.format(camera))

#_____________________________________________________________________
def placeRadars(car_name, radar, radars, on = True):

    radar_positions = radars[radar]["radar_positions"]
    if car_name in radar_positions:
        radar_pos = radar_positions[car_name]['position']
        radar_rot = radar_positions[car_name]['rotation']
    else:
        radar_pos = radar_positions["default"]['position']
        radar_rot = radar_positions["default"]['rotation']
    radar_position = anyverse_platform.Vector3D( radar_pos[0], radar_pos[1], radar_pos[2] )
    radar_rotation = anyverse_platform.Vector3D( radar_rot[0], radar_rot[1], radar_rot[2] )

    # place radar in the radar position.
    # There should be a radar under the cabin with the key '_Radar' suffix in the name 
    # the_cabin = icu.getCars()[0]
    radar_ids =  [ li for li in workspace.get_entities_by_name_including(radar + '_Radar') ]
    radar_id = radar_ids[0] if len(radar_ids) >= 1 else 0
    if radar_id != 0:
        icu.setSensorInPosition(radar_id, radar_rotation, radar_position)
        workspace.set_entity_property_value(radar_id, 'VisibleComponent','visible', on)
    else:
        print('[WARN] Missing radar {} in workspace'.format(radar))

#__________________________________________
def getCameraProbabilityList(incabin_config):
    return [ x for x in incabin_config["cameras"] ], [ incabin_config["cameras"][x]['probability'] for x in incabin_config["cameras"] ]

#__________________________________________
def getRadarProbabilityList(incabin_config):
    return [ x for x in incabin_config["radars"] ], [ incabin_config["radars"][x]['probability'] for x in incabin_config["radars"] ]

# Create the InCabinUtils object and asign it to the workspace
icu = incabin.InCabinUtils(workspace, resources, script_console)
workspace.icu = icu

if iteration_index == 0:
    if not hasattr(anyverse_platform, 'cars'):
        print('Loading car interiors...')
        anyverse_platform.cars = icu.queryCars(dynamic_material = True)
        #print(anyverse_platform.cars)
        print('Car list loaded!')
    
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

# Find the sensor_rig_locator and save it to the simulation node if the parent is thee_car
try:
    sensor_rig_locator = workspace.get_entities_by_name('sensor_rig_locator')[0]
except IndexError as ie:
    print('[Error] No sensor rig locator found... Exiting.')
    assert False
if the_car == workspace.get_entity_parent(sensor_rig_locator):
    workspace.set_parent_entity(sensor_rig_locator, simulation_id)

# Remove the_cabin completelly until the change of the referenced asset with locators is fixed
print('Deleting current car cabin...')
workspace.delete_entity(the_car)
icu.deleteAllOnBelts()
# print('Deleting current occupants...')
# icu.clearDescendantFixedEntities(the_car)

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
    change_belt_material = False # incabin_config['occupancy_distribution']['seatbelts_distribution']['random_belt_material']
    the_car = workspace.create_fixed_entity('the_cabin', simulation_id, selected_car['entity_id'])
    
    workspace.set_parent_entity(sensor_rig_locator, the_car)

    print(selected_car['name'])
    # if isSegmentedCar(selected_car):
    #     with_parts = True
    # else:
    #     with_parts = False
    icu.buildCar(selected_car, the_car, with_parts = True, dynamic_materials = False, move_seats_conf = move_seats_conf, change_belt_material = change_belt_material)

    # Set car info from car metadata and put it as custom metadata for annotations
    car_info = icu.setCarInfo(selected_car,the_car)
    car_name = '{}_{}'.format(selected_car['brand'].replace(" ",""), selected_car['model'])
else:
    print('[ERROR] Could not find {} in resources'.format(selected_car))
# Set Export Always and exclude from occlusion test properties to the car
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
        placeCameraAndLights(car_name, camera, cameras, on = cameras[camera]['on_for_multicamera'])
    # No particular camera selected, relevant when setting the illumination
    camera_selected = None
# If not multiple cameras,  
# Randomly select the camera to use and place it in the camera position along with
# the associated active lights if the correspondent locator exists, apply vibration 
# as configured (done with the new function placeCamera), an then set the visibility 
# to a single camera
else:
    names, probabilities = getCameraProbabilityList(incabin_config)
    cam_ids_idx = icu.choiceUsingProbabilities(probabilities)
    camera_selected = names[cam_ids_idx]

    placeCameraAndLights(car_name, camera_selected, cameras)

    #__________________________________________________________
    # Set cameras visibility, accordingly with the selected camera
    camera_id, camera_name = icu.setCameraVisibility(camera_selected)
    if not camera_id:
        print('[ERROR] No camera {} in Workspace'.format(camera_selected))
        assert False
    print('Using camera: {}'.format(camera_name))

radars = incabin_config["radars"]
# Global radar settings
multiple_radars = incabin_config["multiple_radars"]
# If multiple radars,  
# place each radar in its position relative to the ego.
if multiple_radars:
    # place each radars in its position
    for radar in radars:
        placeRadars(car_name, radar, radars, on = radars[radar]['on_for_multiradar'])
    # No particular radar selected, relevant when setting the illumination
    radar_selected = None
# If not multiple radars,  
# Randomly select the radar to use and place it in the radar position and then set the visibility 
# to a single Radar
else:
    names, probabilities = getRadarProbabilityList(incabin_config)
    cam_ids_idx = icu.choiceUsingProbabilities(probabilities)
    radar_selected = names[cam_ids_idx]

    placeRadars(car_name, radar_selected, radars)

    #__________________________________________________________
    # Set radars visibility, accordingly with the selected radar
    radar_id, radar_name = icu.setRadarVisibility(radar_selected)
    if not radar_id:
        print('[ERROR] No radar {} in Workspace'.format(radar_selected))
        assert False
    print('Using radar: {}'.format(radar_name))

# Reduce camera resolution while testing
suffix = ''
if workspace.reduce_resolution and iteration_index == 0:
    print('Reducing all cameras resolution for testing')
    # icu.reduceAllCameraResolution(2)
    suffix = '-lowres'
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
day, interior_lights = icu.selectConditions(conditions)
print('Day scene: {}, Interior Lighting : {}'.format(day, interior_lights))

# pick and set a background depending if its day/night
background, bckgnd_id = icu.selectBackground(day)
print('Setting background {}'.format(workspace.get_entity_name(bckgnd_id)))
icu.setBackground(background, simulation_id)

# set a time of day and a ground rotation randomly so the light will come in from variable angles
# and the background seen through the windows changes
sun_elevation, sun_azimuth, ground_rotation = icu.setGroundRotationSunDirection(day, simulation_id)
print('Sun position: elevation {:.2f}, azimuth {:.2f}; Ground rotation: {}'.format(math.degrees(sun_elevation), math.degrees(sun_azimuth), ground_rotation))

print('Setting active lights to {}'.format(interior_lights))
# set the illumination depending on day/night and conditions
intensity = icu.setIllumination(day, background, simulation_id, camera_selected, active_light = interior_lights)
if day:
    print('Sun intensity: {}'.format(intensity))
else:
    print('IBL intensity: {}'.format(intensity))


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

