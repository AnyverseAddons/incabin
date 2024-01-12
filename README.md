# Anyverse In-Cabin Add-on
This repo has all the necessary python modules and scripts to generate dataset for an in-cabin use case with the [Anyverse Platform](https://anyverse.ai)

You can find additional documentation and a **series of tutorials** to get you started with the In-Cabin Add-on in out [resources page](https://anyverse.ai/resources/)

## Getting started
To this Anyverse add-on (or any other Anyverse add-on for that matter) you need:

1. An Anyverse Platform account
2. Anyverse Studio installed on your local machine

Clone this repo to your local machine, or if you want to contribute, fork the repo to your github account (you will be able to send pull requests with your contributions) and then clone it to your local machine.

## What's new
**March 2023**
- New configuration for multi-camera datasets with more than one camera enabled at the same time
- New configuration to simulate a pseudo-NIR sensor at night
- New configuration to simulate any RGB sensor

**April 2023**
- New configuration to control character's face expressions
- More advanced child seat configuration capabilities

**May 2023**
- Access to new child seats available in the Anyverse Platform resource database
- Allow variability by dynamically changing the asset's exposed materials
- The add-on randomly picks a suitable material for every child seat it places in the cabin
- The seat belt configuration applies to baby child seat with babies as well (only normal placement)
- New wrong seatbelt place positions: `LapBeltUnder` and `UnderShoulderLapBeltUnder`

**June 2023**
- More car cabin variability: Support for dynamic material in car cabins following a color scheme. No need of specific car cabin assets for different interior colors
- New configuration parameters to adjust front seats in depth and tilt

**October 2023**
- Added 8 new car cabin models from real brands and models. Now the total available car cabins is 16
- New points inside the cabin to configure the gaze of the front occupants. Additionally there is new feature to make the characters reach to the gaze points to force more extreme poses.

## Configure Anyverse Studio the use the add-on
In Anyverse Studio User Settings, set the 'Python addons folder'  to your local repo directory.

![User settings](images/python-scripts-path.png)

## Add-on structure
This add-on has an incabin module and an on-begin-iteration script :

- **incabin.py** - Incabin module with the InCabinUtils class that implements all the functionality you need to generate an in-cabin dataset. The class is used in the on-begin-iteration script.
- **variation-scripts/in-cabin-on-begin-script.py** - Script to use in the generation On Begin Script property. This has all the in-cabin configuration and logic to select a car cabin, camera, environmental conditions and occupancy distribution, including seat belts, and gaze probabilities.

## Using the add-on
The in-cabin add-on allows to generate a varied in-cabin dataset to train and validate different in-cabin monitoring use cases.

As is, the add-on allows to generate static images datasets at scale manipulating the variability with the configuration dictionaries at the beginning of the on-begin-iteration script.

From Anyverse Studio you can test the set up and the on-begin-iteration script using the script console. From the Workspace perspective, open the script console selecting 'Show script console view' from the Views pull down menu.

![Script console](images/script-console.png)

Use the ![Open script](images/open-script.png) to load the on-begin-script in the console and the ![Run script](images/play-script.png) to run the script and see the effects in the 3D viewer and the workspace.

Feel free to change the script configuration if you want to change the behavior of the dataset generation. 

To generate a dataset based on that configuration, import the on-begin-iteration script in the Generator OnBeginIteration property:

![OnBeginIteration](images/on-begin-iteration.png)

Configure the number of iterations property to generate the samples ina  dataset.

Check the tutorials for a step-by-step explanation of the process.

## In-cabin variability configuration
At the beginning of the on-begin-iteration script we define the **`incabin_config`** dictionary with all the variables you can use to configure the variability of the resulting dataset. It has 5 configuration properties: `car_interior_probabilities`, `cameras`, `conditions`, `occupant_confs_probabilities` and `occupancy_distribution`.

The first set of properties, allows to set different probabilities to the different car models[^models] with the `car_interior_probabilities` property. This property is used in with the `use_car_interior_probabilities`. If set to True, the `selectCar` method is called passing the `car_interior_probabilities` probabilities list. If set to False, the `selectCar` is called without parameters for the default behavior selecting a car interior randomly using a uniform distribution.

With the `adjust_front_seats` you control if you want to change the adjust the depth and tilt of the front seats. If set to `True` we will apply a random depth (in meters) and tilt angle (in degrees), specified per car model in the `car_interior_probabilities` properties `max_depth` and `max_tilt`. The randomization will be based on a normal distribution or a uniform distribution in the interval [-value, value] depending if the property `normal_dist` is set to `True` or `False`: 

```
    "use_car_interior_probabilities": True,
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
```
The next set of properties, allow you to configure and control the cameras in the cabin. 
- `multiple_cameras`, when set to `False`, only one camera will be enabled in the cabin based on the cameras defined probabilities. When set to `True`, all cameras will be enabled and positioned in their correspondent locations.
- `use_nir`, when set to `True` it'll set NIR sensor simulation with active illumination for all cameras.
- `rgb_at_day`, when set to `True` it'll override the use of NIR sensor for day light, and will generate a RGB image using the EGB-sensor configured in the workspace (make sure you have an RGB sensor with that name configured).
- `cameras`, defines the probability[^probabilities] to use the correspondent camera when `multiple_cameras`is `False`, a couple of vibration vectors move the camera using a normal or uniform distribution around its initial position and orientation; and the initial position and pitch angle for every car cabin model. 

This is the default configuration for 2 cameras RVM for a rear view mirror position and CC for central console position:

```
    "multiple-cameras": False,
    "use_nir": True,
    "rgb_at_day": False,
    "cameras":{
        "RVM": {
            "probability": 1.0,
            "vibration_traslation": [0,0,0], # in meters
            "vibration_rotation": [0,0,0], # in degrees
            "cam_positions": {
                'Audi_Q5': {'rotation': (0, -50, 0), 'position': (0.435, 0.0, 1.45) }, 
                'Chevrolet_Menlo':  {'rotation': (0, -50, 0), 'position': (0.53, 0.0, 1.26) },
                'Lexus_UX':         {'rotation': (0, -50, 0), 'position': (0.46, 0.005, 1.26) },
                'Porsche_CayenneS': {'rotation': (0, -50, 0), 'position': (0.50, 0.0, 1.45) },
                'Unbranded_GenericSUV':    {'rotation': (0, -50, 0), 'position': (0.485, -0.005, 1.43) },
                'Volkswagen_Passat': {'rotation': (0, -50, 0), 'position': (0.575, -0.027, 1.287)},
                'Hyundai_Ioniq': {'rotation': (0, -50, 0), 'position': (0.45, -0.02, 1.315)},
                'LandRover_Autobiography': {'rotation': (0, -50, 0), 'position': (0.41, 0.0, 1.58)},
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
```
The `conditions`property has to do with the illumination. You can set the probabilities for 4 different  conditions. the last one `interior-lights` sets a night time[^times] and enables in-cabin active illumination and NIR simulation. The default configuration is:

```
    "conditions": [ 
        {'Day': True,  'Cond':'sunny',          'Probability': 0.25},
        {'Day': True,  'Cond':'scattered',      'Probability': 0.25},
        {'Day': True,  'Cond':'overcast',       'Probability': 0.25},
        {'Day': False, 'Cond':'interior-lights','Probability': 0.25}
    ],
```

IF you need empty cabins with no occupants nor objects in you dataset, you can control this with the `occupant_confs_probabilities` property. It allows you to force a percent of samples with completely empty seats instead of relying in the statistical probability of a random empty seats configuration. This is the default:

```
    "occupant_confs_probabilities": [ 
        {'Conf': 'Empty', 'Probability': 0.0},
        {'Conf': 'Normal', 'Probability': 1.0}
    ],
```

The `occupancy_distribution` property is the most complex and allows you to control how every seat is occupied, what you want to do with the child seats and seat belts, if you want to place additional accessories to the characters (`accessories_probabilities`), where are the characters looking at and the character's facial expression. 

```
    "occupancy_distribution": {
        'driver_occupancy_probabilities': [ ...
        'copilot_occupancy_probabilities': [ ...
        'backseat_occupancy_probabilities': [ ...
        'middleseat_occupancy_probabilities': [ ...
        'childseat_config': { ...
        'accessories_probabilities': { 'global': 0.5, 'glasses': 0.5, 'headwear': 0.5, 'mask': 0.5 },
        'seatbelts_distribution': { ...
        'gaze_probabilities': { ...
        'expression_probabilities': [ ...
    }
```
For the driver seat, `driver_occupancy_probabilities`, you can set the probabilities to be empty or occupied. For all other seats, `copilot_occupancy_probabilities`, `backseat_occupancy_probabilities` and `middleseat_occupancy_probabilities` you can set probabilities to be empty, have a child seat, a passenger or an object. 

```
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
```

With the `age_group_probabilities` property you can control the age of the character placed as passengers and drivers. For child seats de characters will always be children or babies depending on the child seat type. Notice that you can configure a probability to place babies (0-3 age group), however, that is not currently supported. In the example below the age group distribution is uniform, bear in mind the distribution of available characters is not homogenous. It is more a gaussian distribution with the center in the 19-30 and 31-50 age groups. SO, you should probably have a higher probability for these if you want more character variability across your dataset.

Additionally now, you can have the passenger to have a baby on their lap. The `baby_on_lap_probability` controls the probability of a character having a baby on his/her lap. Set it to 0 to disable this feature.

```
        'age_group_probabilities': [
            {'age_group': '0-3', 'kind': 'Baby', 'probability': 0.0},
            {'age_group': '4-12', 'kind': 'Child', 'probability': 0.20},
            {'age_group': '13-18', 'kind': 'Child', 'probability': 0.20},
            {'age_group': '19-30', 'kind': 'Adult', 'probability': 0.20},
            {'age_group': '31-50', 'kind': 'Adult', 'probability': 0.20},
            {'age_group': '50+', 'kind': 'Adult', 'probability': 0.20},
        ],
        'baby_on_lap_probability': 0.2,
```

With the `childseat_config` property, you have control on the probabilities for different types of child seats (`childseat_type_probabilities`), the probability that the child seat will be occupied (`childseat_occupancy_probabilities`) with a child or an object, or just leaving it empty. There is further control on the child seat orientation (only for BabyChild type child seats) with the `childseat_orientation property`. And finally you can define a maximum rotation angle (around Z) for the child seat with `childseat_rotation_max`.

```
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
```

For seat belts, `seatbelts_distribution`, on one hand, you can decide the probability that a given passenger (including children in child seats) have a seat belt on. The how is that seat belt placed, normal or with a wrong placement.

```
        'seatbelts_distribution': {
            'belt_on_probability': 0.95, # Probability for seatbelt on when there is a character seated
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
```

For the driver and the copilot, you can control their gaze (`gaze_probabilities`) setting the probabilities they are going to look at and optionally reach to: the road, the exterior rear view mirrors, the interior rear view mirror the other front row passenger, at the rear, at the opposite headrest, at the glove compartment, at the own seat belt or at the floor.

```
        'gaze_probabilities': {
            'driver_gaze_probabilities':  [
                {'name': 'road', 'gaze': 0, 'reach': False, 'probability': 0.09},
                {'name': 'ext_mirror', 'gaze': 1, 'reach': False, 'probability': 0.08},
                {'name': 'int_mirror', 'gaze': 2, 'reach': False, 'probability':  0.08},
                {'name': 'infotainment', 'gaze': 3, 'reach': True, 'probability':  0.08},
                {'name': 'passenger', 'gaze': 4, 'reach': False, 'probability':  0.08},
                {'name': 'rear', 'gaze': 5, 'reach': False, 'probability': 0.09},
                {'name': 'headrest', 'gaze': 6, 'reach': True, 'probability': 0.09},
                {'name': 'glove', 'gaze': 7, 'reach': True, 'probability': 0.09},
                {'name': 'seatbelt', 'gaze': 8, 'reach': True, 'probability': 0.09},
                {'name': 'floor', 'gaze': 9, 'reach': True, 'probability': 0.09},
                {'name': 'free', 'gaze': 10, 'reach': False, 'probability':  0.14}
            ],
            'copilot_gaze_probabilities': [
                {'name': 'road', 'gaze': 0, 'reach': False, 'probability': 0.09},
                {'name': 'ext_mirror', 'gaze': 1, 'reach': False, 'probability': 0.08},
                {'name': 'int_mirror', 'gaze': 2, 'reach': False, 'probability':  0.08},
                {'name': 'infotainment', 'gaze': 3, 'reach': True, 'probability':  0.08},
                {'name': 'passenger', 'gaze': 4, 'reach': False, 'probability':  0.08},
                {'name': 'rear', 'gaze': 5, 'reach': False, 'probability': 0.09},
                {'name': 'headrest', 'gaze': 6, 'reach': True, 'probability': 0.09},
                {'name': 'glove', 'gaze': 7, 'reach': True, 'probability': 0.09},
                {'name': 'seatbelt', 'gaze': 8, 'reach': True, 'probability': 0.09},
                {'name': 'floor', 'gaze': 9, 'reach': True, 'probability': 0.09},
                {'name': 'free', 'gaze': 10, 'reach': False, 'probability':  0.14}
            ]
        },
```

Finally, you can control the facial expression for every character `expression_probabilities`, by setting probabilities for 5 different preset expressions: neutral, sad, happy, angry and surprised; and the probability to have a random expression.

```
        'expression_probabilities': [
            {'name': 'neutral', 'expression': 0, 'probability': 0.20},
            {'name': 'happy', 'expression': 1, 'probability': 0.20},
            {'name': 'sad', 'expression': 2, 'probability': 0.20},
            {'name': 'angry', 'expression': 3, 'probability': 0.15},
            {'name': 'surprised', 'expression': 4, 'probability': 0.15},
            {'name': 'random', 'expression': 5, 'probability': 0.1}
        ]
```
All the above are the default values for all configuration properties.

[^models]: There are 8 different car brands and model, for a total of 26 distinct interiors: Audi Q5, 4 different interior colors; Chevrolet Menlo, 4 different interior colors; Lexus UX, 4 different interior colors; Porsche Cayenne, 4 different interior colors; Unbranded Generic SUV, 4 different interior colors; Volkswagen Passat, 4 different interior colors; Hyundai Ioniq, 1 interior colors; Land Rover Autobiography, 1 interior colors

[^probabilities]: they represent the percentage of samples that will have the correspondent characteristic. 0 is 0% and 1  is 100%.

[^times]: We are assuming an equator location. Day time is between 6 AM to 6 PM and night time the other half of the day.

