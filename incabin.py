import anyverse_platform
import city_builder
import json
import csv
import random
import math
import re
import sys
import anyverseaux as aux

class InCabinUtils:
    def __init__(self, workspace, resources, script_console, iteration_index = None, total_iteration_count = None, seat_collision = False):
        self._iteration_index = iteration_index
        self._workspace = workspace
        self._resources = resources
        self._simulation_id = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Simulation)[0]
        self._no_entry = anyverse_platform.invalid_entity_id
        self._ego_id = self._workspace.get_entities_by_name("Ego")[0]
        self._already_used_characters = []
        self._car_brand = ""
        self._car_model = ""
        self._clip_asset_name = "ConvertibleChildSeat_ClipOn"
        self._car_color_schemes = ['black', 'brown', 'darkgrey', 'lightgrey']
        self._excluded_objects = [ 'duffle_bag_01_handle', 'duffle_bag_02_handle', 'duffle_bag_03_handle', 'Beagle', '0076_20220809_v0' ]
        if not self.isAssetAlreadyCreated(self._clip_asset_name):
            clip_asset = self.getConvertibleClipAsset(self._clip_asset_name, self.getAssetsByTag('belts', self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset)))
            self._clip_asset = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, clip_asset.id)
        else:
            self._clip_asset = self._workspace.get_entities_by_name( self._clip_asset_name )[0]
        self._script_console = script_console

        self._beltOptions = {
                'Normal': anyverse_platform.SeatBeltPlacement.Normal,
                'BehindTheBack': anyverse_platform.SeatBeltPlacement.BehindTheBack,
                'UnderShoulder': anyverse_platform.SeatBeltPlacement.UnderShoulder,
                'WrongSideOfHead': anyverse_platform.SeatBeltPlacement.WrongSideOfHead,
                'CharacterOverSeatbelt': anyverse_platform.SeatBeltPlacement.WithoutCharacter,
                'LapBeltUnder': anyverse_platform.SeatBeltPlacement.LapBeltUnder,
                'UnderShoulderLapBeltUnder': anyverse_platform.SeatBeltPlacement.UnderShoulderLapBeltUnder
            }
        self._belt_material_id = anyverse_platform.invalid_entity_id
        self._look_and_reach_positions = {
                'cc': {'center': (0.6, 0.0, 1.04)},
                'glove': {'right': (0.6, -0.5, 0.84)},
                'rvm': {'inside': (0.44, 0.0, 1.44), 'right': (0.7, -1.0, 1.1), 'left': (0.7, 1.0, 1.1)},
                'floor': {'right': (0.65, -0.4, 0.3), 'left': (0.65, 0.4, 0.3)},
                'headrest': {'right': (-0.2, -0.28, 1.30), 'left': (-0.2, 0.28, 1.30)},
                'seatbelt': {'right': (-0.1, -0.6, 1.19), 'left': (-0.1, 0.6, 1.19)}
        }
        self._seat_collision = seat_collision

    #________________________________________________________________________________________
    # update_progress() : Displays or updates a console progress bar
    ## Accepts a float between 0 and 1. Any int will be converted to a float.
    ## A value under 0 represents a 'halt'.
    ## A value at 1 or bigger represents 100%
    def update_progress(self, progress):
        barLength = 20 # Modify this to change the length of the progress bar
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), round(progress*100, 2), status)
        sys.stdout.write(text)
        sys.stdout.flush()

    #_______________________________________________________________
    def validateConfig( self, config ):
        assert config.entity_id_using_belt != anyverse_platform.invalid_entity_id, "Child seat belt configuration: entity_id_using_belt not set"
        assert config.clip_entity_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_entity_id not set"

        assert config.second_up_left_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: second_up_left_locator_id not set"
        assert config.first_up_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: first_up_right_locator_id not set"
        assert config.second_up_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: second_up_right_locator_id not set"
        assert config.first_down_left_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: first_down_left_locator_id not set"
        assert config.second_down_left_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: second_down_left_locator_id not set"
        assert config.first_down_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: first_down_right_locator_id not set"
        assert config.second_down_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: second_down_right_locator_id not set"
        assert config.first_central_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: first_central_locator_id not set"
        assert config.second_central_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: second_central_locator_id not set"

        assert config.clip_second_up_left_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_second_up_left_locator_id not set"
        assert config.clip_first_up_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_first_up_right_locator_id not set"
        assert config.clip_second_up_right_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_second_up_right_locator_id not set"
        assert config.clip_first_central_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_first_central_locator_id not set"
        assert config.clip_second_central_locator_id != anyverse_platform.invalid_entity_id, "Child seat belt configuration: clip_second_central_locator_id not set"

    #_______________________________________________________________
    def getParent(self, entity_id):
        try:
            return self._workspace.get_entity_property_value( entity_id, "RelativeTransformToComponent", "entity_id" )
        except:
            return anyverse_platform.invalid_entity_id

    #_______________________________________________________________
    def isDay(self):
        time_of_day = self._workspace.get_entity_property_value(self._simulation_id, 'SimulationEnvironmentComponent','time_of_day' )
        return time_of_day >= 6.00 and time_of_day <= 18.00

    #_______________________________________________________________
    def vectorToList(self, vector):
        l = []
        for m in vector:
            l.append(m)
        return l

    #_______________________________________________________________
    def deleteAllOnBelts(self):
        if not self._script_console:
            self._workspace.delete_all_seat_belt()
            if hasattr(anyverse_platform, 'entitiesToClear'):
                for entity in anyverse_platform.entitiesToClear:
                    if self._workspace.has_entity(entity):
                        self._workspace.delete_entity(entity)

            anyverse_platform.entitiesToClear = []

            if hasattr( anyverse_platform, "iteration_entities" ):
                for entityId in anyverse_platform.iteration_entities:
                    if self._workspace.has_entity( entityId ):
                        self._workspace.delete_entity( entityId )

            anyverse_platform.iteration_entities = []
            # self._workspace.delete_all_seat_belt()


    #_______________________________________________________________
    def deleteChildren(self, entity_id):
        for child_id in self._workspace.get_hierarchy(entity_id)[1:]:
            self._workspace.delete_entity(child_id)

    #_______________________________________________________________
    def clearDescendantFixedEntities(self, entity_id):
        descendant_fixed_entities_list = [ fe for fe in self._workspace.get_hierarchy(entity_id) if 'FixedEntity' == self._workspace.get_entity_type(fe) ]
        descendant_fixed_entities_list.reverse()

        for fixed_entity_id in descendant_fixed_entities_list:
            if fixed_entity_id != entity_id:
                self._workspace.delete_entity(fixed_entity_id)

    #_______________________________________________________________
    def getDelta(self, center, interval, normal = True):
        if normal:
            mu, sigma = center, interval/3.6
            delta = random.normalvariate(mu, sigma)
        else:
            delta = random.uniform(center - interval,center + interval)

        if delta > interval:
            delta = interval
        if delta < -interval:
            delta = -interval
        
        return delta

    #_______________________________________________________________
    def isVisible(self, entityId):
        return self._workspace.get_entity_property_value(entityId, 'VisibleComponent','visible')

    #_______________________________________________________________
    def setCustomMetadata(self, entityId, key, value, replace = False):
        old_metadata = self._workspace.get_entity_property_value(entityId, 'UserMetadataComponent','json_metadata')
        if not old_metadata or replace:
            old_metadata = "{}"
        metadata_dict = json.loads(old_metadata)
        metadata_dict[key] = value
        new_metadata = json.dumps(metadata_dict)
        self._workspace.set_entity_property_value(entityId, 'UserMetadataComponent','json_metadata', new_metadata)

    #_______________________________________________________________
    def removeMotionBlur(self, entity_id):
        self._workspace.set_entity_property_value(entity_id, 'MotionBlurComponent','deformation', False)
        self._workspace.set_entity_property_value(entity_id, 'MotionBlurComponent','transformation', False)

    #_______________________________________________________________
    def setSplitAction(self, entity_id, action):
        self._workspace.set_entity_property_value(entity_id, 'AssetReferenceConfigurationComponent','asset_reference_split_action', action)

    #_______________________________________________________________
    def setInstanceIfPossible(self, entity_id, instance):
        self._workspace.set_entity_property_value(entity_id, 'ExportPolicyComponent','instance_if_possible', instance)

    #_______________________________________________________________
    def setExportAlwaysExcludeOcclusion(self, entity_id):
        self._workspace.set_entity_property_value(entity_id, 'ExportConfigurationComponent','export_always', True)
        self._workspace.set_entity_property_value(entity_id, 'ExportConfigurationComponent','exclude_from_occlusion_tests', True)
        self._workspace.set_entity_property_value(entity_id, 'VisibleComponent','visible', True)

    #_______________________________________________________________
    def setAvoidArmsAutoCollision(self, entity_id, avoid):
        self._workspace.set_entity_property_value(entity_id, 'CharacterBodyRestrictionsComponent','avoid_arms_auto_collision', avoid)

    #_______________________________________________________________
    def setSeatCollision(self, entity_id, mode = 'Nothing', collision_entity_id = None):
        if collision_entity_id:
            mode = 'SeatEntity'

        try:
            self._workspace.set_entity_property_value(entity_id, 'CharacterBodyRestrictionsComponent','SeatCollision.SeatCollisionMode', mode)
            if mode ==  'SeatEntity':
                self._workspace.set_entity_property_value(entity_id, 'CharacterBodyRestrictionsComponent','SeatCollision.SeatCollisionEntityId', collision_entity_id)
        except RuntimeError as rune:
            print('[WARN] Avoid collision with seats not supported: {}'.format(rune))

    #_______________________________________________________________
    def setExportAlwaysExcludeOcclusionToAllEntities(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        for fx in fixed:
            self.setExportAlwaysExcludeOcclusion(fx)

    #_______________________________________________________________
    def getCars(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        cars = []
        for entity in fixed:
            asset_id = self._workspace.get_entity_property_value(entity, 'AssetEntityReferenceComponent','asset_entity_id')
            tags = self._workspace.get_tags_from_entity(asset_id)
            if ('car-interior' in tags) and self.isVisible(entity):
                cars.append(entity)
        return cars

    #_______________________________________________________________
    def getAnimIdByName(self, anim_name):
        anims = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation)
        for anim in anims:
            if self._workspace.get_entity_name(anim) == anim_name or anim_name in self._workspace.get_entity_name(anim):
                return anim
        return -1

    #_______________________________________________________________
    def scaleEntity(self, entity_id, factor):
        scale = self._workspace.get_entity_property_value(entity_id, 'RelativeTransformToComponent','scale')
        new_scale = anyverse_platform.Vector3D(scale.x*factor, scale.y*factor, scale.z*factor)
        self._workspace.set_entity_property_value(entity_id, 'RelativeTransformToComponent','scale', new_scale)

        return new_scale

    #_______________________________________________________________
    def getEntityLocators(self, entity_id):
        descendents = self._workspace.get_hierarchy(entity_id)
        locators = [ l for l in descendents if self._workspace.get_entity_type(l) == 'Locator' ]
        return locators

    #_______________________________________________________________
    def getWheelLocators(self, entity_id):
        ret = {}
        locators_list = self._workspace.get_hierarchy(entity_id)
        wheel_locators = [ l for l in locators_list if re.search("^wheel?._locator$", self._workspace.get_entity_name(l)) ]
        for locator in wheel_locators:
            if 'wheelL' in self._workspace.get_entity_name(locator):
                ret['left'] = locator
            if 'wheelR' in self._workspace.get_entity_name(locator):
                ret['right'] = locator
        return ret

    #_______________________________________________________________
    def getSeatLocators(self, entity_id):
        locators_list = self._workspace.get_hierarchy(entity_id)
        seat_locators = [ l for l in locators_list if re.search("^seat0?._locator$", self._workspace.get_entity_name(l)) and self.isVisible(l) ]
        return seat_locators

    #_______________________________________________________________
    def getChildseatLocators(self, entity_id):
        locators_list = self._workspace.get_hierarchy(entity_id)
        seat_locators = [ l for l in locators_list if re.search("^childSeat0?._locator$", self._workspace.get_entity_name(l)) ]
        return seat_locators

    #_______________________________________________________________
    def getChildLocatorInChildSeat(self, entity_id):
        locators_list = self._workspace.get_hierarchy(entity_id)
        seat_locators = [ l for l in locators_list if 'child' in self._workspace.get_entity_name(l).lower() and '_locator' in self._workspace.get_entity_name(l).lower() ]
        seat_locator = -1
        if len(seat_locators) == 0:
            print('[ERROR] No locators found for child in child seat {}'.format(self._workspace.get_entity_name(entity_id)))
        elif len(seat_locators) > 1:
            print('[WARN] Found more than 1 child locator in child seat {}. Using the first one found.'.format(self._workspace.get_entity_name(entity_id)))
            seat_locator = seat_locators[0]
        else:
            seat_locator = seat_locators[0]
            
        return seat_locator

    #_______________________________________________________________
    def applyCharacterOffset(self, character):
        position = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'RelativeTransformToComponent','position')
        position.z += float(character['root_offset'].replace(',','.'))/100
        self._workspace.set_entity_property_value(character['fixed_entity_id'], 'RelativeTransformToComponent','position', position)
    #_______________________________________________________________
    # def applyCharacterOffset(self, character):
    #     # Apply the  offset to the locator instead of the character
    #     parent_id = self.getParent(character['fixed_entity_id'])
    #     position = self._workspace.get_entity_property_value(parent_id, 'RelativeTransformToComponent','position')
    #     position.z += float(character['root_offset'].replace(',','.'))/100
    #     self._workspace.set_entity_property_value(parent_id, 'RelativeTransformToComponent','position', position)

    #_______________________________________________________________
    def getSeatPos(self, seat_locator):
        return int(self._workspace.get_entity_name(seat_locator).split("_")[0][-2:])

    #_______________________________________________________________
    def isDriverSeat(self, seat_locator):
        return '01' in self._workspace.get_entity_name(seat_locator)

    #_______________________________________________________________
    def isCopilotSeat(self, seat_locator):
        return '02' in self._workspace.get_entity_name(seat_locator)

    #_______________________________________________________________
    def isLeftBackSeat(self, seat_locator):
        return '03' in self._workspace.get_entity_name(seat_locator)

    #_______________________________________________________________
    def isMiddleBackSeat(self, seat_locator):
        return '04' in self._workspace.get_entity_name(seat_locator)

    #_______________________________________________________________
    def isRightBackSeat(self, seat_locator):
        return '05' in self._workspace.get_entity_name(seat_locator)

    #_______________________________________________________________
    def wiggleChildseatRandom(self, childseat_id, yaw, pitch):
        childseat_rotation = self._workspace.get_entity_property_value(childseat_id, 'RelativeTransformToComponent','rotation')

        childseat_rotation.z += yaw
        childseat_rotation.y += pitch

        self._workspace.set_entity_property_value(childseat_id, 'RelativeTransformToComponent','rotation', childseat_rotation)

    #_______________________________________________________________
    def wiggleBabyRandom(self, baby_id, up_down, shift, rotation):
        baby_position = self._workspace.get_entity_property_value(baby_id, 'RelativeTransformToComponent','position')
        baby_rotation = self._workspace.get_entity_property_value(baby_id, 'RelativeTransformToComponent','rotation')

        baby_position.y += shift / 100
        baby_position.z += up_down / 100
        baby_rotation.z += rotation

        self._workspace.set_entity_property_value(baby_id, 'RelativeTransformToComponent','position', baby_position)
        self._workspace.set_entity_property_value(baby_id, 'RelativeTransformToComponent','rotation', baby_rotation)

    #_______________________________________________________________
    def decideSeatOccupancy(self, seat_locator, ocuppancy_distribution):
        # 0: Empty
        # 1: Driver
        # 2: Childseat
        # 3: Passenger
        # 4: Object
        driver_occupancy = ocuppancy_distribution['driver_occupancy_probabilities']
        copilot_occupancy = ocuppancy_distribution['copilot_occupancy_probabilities']
        backseat_occupancy = ocuppancy_distribution['backseat_occupancy_probabilities']
        middleseat_ocupancy = ocuppancy_distribution['middleseat_occupancy_probabilities']
        ret = 0
        if self.isDriverSeat(seat_locator):
            idx = self.choiceUsingProbabilities([ float(o['probability']) for o in driver_occupancy ])
            ret = driver_occupancy[idx]['occupancy']
        elif self.isCopilotSeat(seat_locator):
            idx = self.choiceUsingProbabilities([ float(o['probability']) for o in copilot_occupancy ])
            ret = copilot_occupancy[idx]['occupancy']
        elif self.isMiddleBackSeat(seat_locator):
            idx = self.choiceUsingProbabilities([ float(o['probability']) for o in middleseat_ocupancy ])
            ret = middleseat_ocupancy[idx]['occupancy']
        elif self.isRightBackSeat(seat_locator):
            idx = self.choiceUsingProbabilities([ float(o['probability']) for o in backseat_occupancy ])
            ret = backseat_occupancy[idx]['occupancy']
            # ret = 0
        elif self.isLeftBackSeat(seat_locator):
            idx = self.choiceUsingProbabilities([ float(o['probability']) for o in backseat_occupancy ])
            ret = backseat_occupancy[idx]['occupancy']
            # ret = 0

        return ret

    #_______________________________________________________________
    def decideChildSeatOccupancy(self, ocuppancy_probabilities):
        # 0: Empty
        # 1: Child
        # 2: Object

        idx = self.choiceUsingProbabilities([ float(o['probability']) for o in ocuppancy_probabilities ])
        ret = ocuppancy_probabilities[idx]['occupancy']

        return ret

    #_______________________________________________________________
    def decideFastenSeatbelt(self, character, belt_on_probability):
        ret = False
        # Adults below this height threshold never have the seatbelt fastened
        height_threshold = 150
        if character['kind'] == 'Adult' and int(character['height']) <= height_threshold:
            print('[WARN] Character too short, not seat belt...')
            return ret

        if belt_on_probability == None:
            belt_on_probability = 0.5
        if random.uniform(0,1) < belt_on_probability:
            ret = True
        return ret

    #_______________________________________________________________
    def doNothing(self, seat_locator):
        print('[INFO] Leaving seat {} empty'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))

    #_______________________________________________________________
    def grabSteeringWheel(self, character_id):
        the_car = self.getCars()[0]
        wheel_locators = self.getWheelLocators(the_car)

        self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent','left_hand_config.locator_entity_id', wheel_locators['left'])
        self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent','right_hand_config.locator_entity_id', wheel_locators['right'])

    #_______________________________________________________________
    def setAnimation(self, anim_type, animation, weight, character_id):
        if anim_type == 'base':
            anim_config = 'base_anim_config'
        elif anim_type == 'spine':
            anim_config = 'spine_anim_config'
        elif anim_type == 'left_arm':
            anim_config = 'arm_l_anim_config'
        elif anim_type == 'right_arm':
            anim_config = 'arm_r_anim_config'
        elif anim_type == 'head':
            anim_config = 'head_anim_config'

        self._workspace.set_entity_property_value(character_id, 'CharacterAnimationConfigurationComponent', anim_config + '.animation_entity_id',animation)
        self._workspace.set_entity_property_value(character_id, 'CharacterAnimationConfigurationComponent', anim_config + '.weight',weight)

    #_______________________________________________________________
    def selectAdultAnimation(self, anim_type, min_weight, max_weight, name = None):
        animations = [ a for a in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation) if 'child' not in self._workspace.get_entity_name(a).lower() ]
        if name is not None:
            filtered_animations = [ a for a in animations if name in self._workspace.get_entity_name(a).lower() ]
        elif anim_type == 'base':
            filtered_animations = [ ba for ba in animations if self._workspace.get_entity_name(ba).lower() in ['sitting_straight', 'arms_on_the_body']]
        elif anim_type == 'spine':
            if self._seat_collision:
                filtered_animations = [ ba for ba in animations if 'leaning' in self._workspace.get_entity_name(ba).lower() ] # TESTING and self._workspace.get_entity_name(ba).lower() != 'leaning_backward' ]
            else:
                filtered_animations = [ ba for ba in animations if 'leaning' in self._workspace.get_entity_name(ba).lower() and self._workspace.get_entity_name(ba).lower() != 'leaning_backward' ]
        elif anim_type == 'left_arm':
            filtered_animations = [ laa for laa in animations if re.search("^Arms_.*_body_L|_head_L$", self._workspace.get_entity_name(laa)) ]
            # filtered_animations = [ laa for laa in animations if re.search("^Arms_stretched_above_.*_L$", self._workspace.get_entity_name(laa)) ]
        elif anim_type == 'right_arm':
            filtered_animations = [ raa for raa in animations if re.search("^Arms_.*_body_R|_head_R$", self._workspace.get_entity_name(raa)) ]
            # filtered_animations = [ raa for raa in animations if re.search("^Arms_stretched_above_.*_R$", self._workspace.get_entity_name(raa)) ]
        elif anim_type == 'head':
            filtered_animations1 = [ ha for ha in animations if re.search("^Pose_Face_.*_0|50|45|90degrees$", self._workspace.get_entity_name(ha)) ]
            # Removing animations that may break the character
            filtered_animations = [ ha for ha in filtered_animations1 if 'turned_up' not in self._workspace.get_entity_name(ha).lower() ]

        weight= random.uniform(min_weight, max_weight)

        # TODO: Protect empty filtered_animations 

        animation_idx = random.randrange(len(filtered_animations))
        animation = filtered_animations[animation_idx]

        return animation, weight

    #_______________________________________________________________
    def getAdultSittingStraightAnimation(self, seat_locator):
        # animations = [ a for a in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation) if 'child' not in self._workspace.get_entity_name(a).lower() and self._workspace.get_entity_name(a).lower() in ['sitting_straight', 'arms_on_the_body']]
        if self.isCopilotSeat(seat_locator):
            animation_key = 'sitting_straight_adult_copilot_op_script'
        else:
            animation_key = 'sitting_straight'
        animations = [ a for a in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation) if 'child' not in self._workspace.get_entity_name(a).lower() and self._workspace.get_entity_name(a).lower() in [animation_key]]
        idx = random.randint(0, len(animations) - 1)
        return animations[idx], 1

    #_______________________________________________________________
    def getChildSittingStraightAnimation(self, seat_locator):
        animation = 'sitting_straight_child_extended-legs' if self.isMiddleBackSeat(seat_locator) else 'sitting_straight_child'
        animations = [ a for a in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation) if animation == self._workspace.get_entity_name(a).lower() ]
        return animations[0], 1

    #_______________________________________________________________
    def selectChildAnimation(self, seat_locator, anim_type, min_weight, max_weight):
        animations = [ a for a in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Animation) if 'child' in self._workspace.get_entity_name(a).lower() or 'pose_face' in self._workspace.get_entity_name(a).lower() ]

        if anim_type == 'base':
            if self.isMiddleBackSeat(seat_locator):
                filtered_animations = [ ba for ba in animations if 'extended-legs' in self._workspace.get_entity_name(ba).lower()  ]
            else:
                filtered_animations = [ ba for ba in animations if self._workspace.get_entity_name(ba).lower() in ['sitting_straight_child', 'arms_on_the_body'] ]
        elif anim_type == 'spine':
            filtered_animations = [ ba for ba in animations if 'leaning' in self._workspace.get_entity_name(ba).lower() ]
        elif anim_type == 'left_arm':
            filtered_animations = [ laa for laa in animations if re.search("^Arms_.*_L_Child$", self._workspace.get_entity_name(laa)) ]
        elif anim_type == 'right_arm':
            filtered_animations = [ raa for raa in animations if re.search("^Arms_.*_R_Child$", self._workspace.get_entity_name(raa)) ]
        elif anim_type == 'head':
            filtered_animations = [ ha for ha in animations if re.search("^Pose_Face_.*_50|45|90degrees$", self._workspace.get_entity_name(ha)) ]

        weight= random.uniform(min_weight, max_weight)

        animation_idx = random.randrange(len(filtered_animations))
        animation = filtered_animations[animation_idx]

        return animation, weight

    #_______________________________________________________________
    def selectBaby(self, key, value, for_backseat, name = None):
        # list of babies dictionaries
        babies = self._workspace.babies
        if name == None:
            baby_characters = self.filterCharacters(babies, key, value, check_twins=False)
        else:
            baby_characters = self.filterCharacters(babies, 'name', name, check_twins=False)
        
        # pick one randomly taking into account the type of baby that goes in each place
        baby_idx = random.randrange(len(baby_characters))
        baby = baby_characters[baby_idx]
        if for_backseat:
            baby_name = 'Baby02'
        else:
            baby_name = 'Baby01'

        tries = 0
        while baby_name not in baby['resource_name'] and tries <= 50:
            baby_idx = random.randrange(len(baby_characters))
            baby = baby_characters[baby_idx]
            tries += 1

        baby_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, baby['resource_id'])

        baby['Face'] = 'neutral'

        return baby_asset_id, baby

    #_______________________________________________________________
    def getBigBabyAssets(self):
        person_assets = self.getAssetsByTag('person', self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset))

        big_baby_assets = [ p for p in person_assets if 'baby02' in p.name.lower() ]

        return big_baby_assets

    #_______________________________________________________________
    def selectCharacter(self, key, value, name = None):
        # list of characters dictionaries from CSV file
        characters = self._workspace.characters
        # filter characters from CSV by characteristic and discard if already been used
        if name == None:
            filtered_characters = self.filterCharacters(characters, key, value)
        else:
            filtered_characters = self.filterCharacters(characters, 'resource_name', name)

        if len(filtered_characters) > 0:
            # pick one randomly
            character_idx = random.randrange(len(filtered_characters))
            character = filtered_characters[character_idx]
            character_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, character['resource_id'])
            # print('[INFO] Selected character: {}'.format(character['resource_name']))
        else:
            character_asset_id = -1
            character = None

        return character_asset_id, character

    #_______________________________________________________________
    def checkCharacter(self, name = None):
        ret = None
        # list of all character assets from resources
        character_assets = self.getAssetsByTag('character', self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset))
        # List of big babies that could be eligeble for convertible seats

        # list of characters dictionaries from CSV file
        characters = self._workspace.characters
        filtered_characters = self.filterCharacters(characters, 'name', name)

        character = filtered_characters[0]
        print('[INFO] Selected character: {}'.format(character['resource_name']))
        for character_asset in character_assets:
            if character['resource_name'] in character_asset.name and '_OP' in character_asset.name:
                ret = character
                break
            if 'baby' in character['resource_name'].lower():
                break
        return ret

    #_______________________________________________________________
    def selectObject(self, name = None, version = None, object_types = None, big_object = None):
        objects = self._workspace.objects
        print('[INFO] Selecting object types: {}'.format(object_types))

        if name == None:
            if object_types:
                filtered_objects = [ o for o in objects if o['class'] in object_types ]
            else:
                filtered_objects = objects

            if big_object:
                filtered_objects = [ o for o in filtered_objects if 'big_object' in o and o['big_object']  ]
            else:
                filtered_objects = [ o for o in filtered_objects if 'big_object' in o and not o['big_object'] ]

            picked_object = filtered_objects[random.randrange(len(filtered_objects))] if len(filtered_objects) > 0 else None
        else:
            for idx, object in enumerate(objects):
                if name == object['name'] and version == object['version']:
                    picked_object = objects[idx]
                    break

        if picked_object:
            entity_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_object['resource_id'])
            picked_object['entity_id'] = entity_id

        return picked_object

    #_______________________________________________________________
    def selectHumanAccessory(self, type, values, name = None):
        accessories = self._workspace.accessories

        if name == None:
            filtered_accessories = self.filterObjects(accessories, type, values)
        else:
            filtered_accessories = self.filterObjects(accessories, 'resource_name', name)

        if len(filtered_accessories) > 0:
            picked_accessory = filtered_accessories[random.randrange(len(filtered_accessories))]
            picked_accessory['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_accessory['resource_id'])
            # print('[INFO] Picked Accessory: {}'.format(picked_accessory["resource_name"]))
        else:
            picked_accessory = {}
            picked_accessory['entity_id'] = -1

        return picked_accessory

    #_______________________________________________________________
    def placeAccessories(self, character, accessories_probabilities = None):
        ret = []
        zero_probs = False
        if accessories_probabilities == None:
            glasses_prob, headwear_prob, mask_prob = 0.5, 0.5, 0.5
        else:
            glasses_prob, headwear_prob, mask_prob = accessories_probabilities['glasses'], accessories_probabilities['headwear'], accessories_probabilities['mask']
            if glasses_prob == 0 and headwear_prob == 0 and mask_prob == 0:
                zero_probs = True


        character_id = character['fixed_entity_id']
        can_glasses, can_cap, can_hat, can_mask = character['glasses'], character['cap'], character['hat'], character['facemask']
        can_headwear = can_cap or can_hat

        accessories_locators = self.getEntityLocators(character_id)

        if not zero_probs:
            if can_glasses:
                put_glasses = True if random.uniform(0,1) < glasses_prob else False
                if put_glasses:
                    glasses = self.selectHumanAccessory('class', ['Sunglasses', 'Glasses'])
                    glasses_locs = [ gl for gl in accessories_locators if 'glasses' in self._workspace.get_entity_name(gl).lower() ]
                    if len(glasses_locs) > 0 and glasses['entity_id'] != -1:
                        glasses_loc = glasses_locs[0]
                        glasses_id = self._workspace.create_fixed_entity(glasses['resource_name'], glasses_loc, glasses['entity_id'])
                        glasses['fixed_entity_id'] = glasses_id
                        glasses['Character'] = character['resource_name']
                        self.setInstanceIfPossible(glasses_id, False)
                        self.setExportAlwaysExcludeOcclusion(glasses_id)
                        self.setAccessoryInfo(glasses)
                        ret.append(glasses)
                    else:
                        print('[WARN] Could NOT find accessories of class Sunglasses or Glasses')
            if can_headwear:
                put_hat = True if random.uniform(0,1) < headwear_prob else False
                if put_hat:
                    if can_hat and can_cap:
                        hat = self.selectHumanAccessory('class', ['Hat', 'Baseball_cap'])
                    elif can_cap:
                        hat = self.selectHumanAccessory('class', ['Baseball_cap'])
                    elif can_hat:
                        hat = self.selectHumanAccessory('class', ['Hat'])
                    hat_locs = [ hl for hl in accessories_locators if 'headwear' in self._workspace.get_entity_name(hl).lower() ]
                    if len(hat_locs) > 0 and hat['entity_id'] != -1:
                        hat_loc = hat_locs[0]
                        hat_id = self._workspace.create_fixed_entity(hat['resource_name'], hat_loc, hat['entity_id'])
                        hat['fixed_entity_id'] = hat_id
                        hat['Character'] = character['resource_name']
                        self.setInstanceIfPossible(hat_id, False)
                        self.setExportAlwaysExcludeOcclusion(hat_id)
                        self.setAccessoryInfo(hat)
                        ret.append(hat)
                    else:
                        print('[WARN] Could NOT find accessories of class Hat or Baseball_cap')
            if can_mask:
                put_mask = True if random.uniform(0,1) < mask_prob else False
                if put_mask:
                    mask = self.selectHumanAccessory('class', ['Facemask'])
                    mask_locs = [ ml for ml in accessories_locators if 'facemask' in self._workspace.get_entity_name(ml).lower() ]
                    if len(mask_locs) > 0 and mask['entity_id'] != -1:
                        mask_loc = mask_locs[0]
                        mask_id = self._workspace.create_fixed_entity(mask['resource_name'], mask_loc, mask['entity_id'])
                        mask['fixed_entity_id'] = mask_id
                        mask['Character'] = character['resource_name']
                        self.setInstanceIfPossible(mask_id, False)
                        self.setExportAlwaysExcludeOcclusion(mask_id)
                        self.setAccessoryInfo(mask)
                        ret.append(mask)
                    else:
                        print('[WARN] Could NOT find accessories of class Facemask')

        return ret

    #_______________________________________________________________
    def placeObjectOnCharacter(self, seat_locator, character_id, name = None, version = None):
        print('[INFO] Placing object on {}'.format(self._workspace.get_entity_name(character_id)))

        big_object = False

        # select a named object from resoures
        object = self.selectObject(name, version, big_object)
        print('[INFO] Object to place {}'.format(object['resource_name']))
        print('[INFO] Baby on character {}'.format(object['resource_name']))
        
        if object['entity_id'] != -1:
            # Create the object fixed entity
            try:
                object_entity_name = object['resource_name']+'_'+object['version'] if 'version' in object else object['resource_name']
                object_entity_id = self._workspace.create_fixed_entity(object_entity_name, seat_locator, object['entity_id'])
                scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))
            except KeyError as ke:
                print('[WARN] wrong asset {}: {}'.format(object['resource_name'], ke))
                if 'scale' in str(ke):
                    print('[WARN] Scale attributes missing')
                    scale_factor = 1
            
            if scale_factor != 1:
                print('[INFO] Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['fixed_entity_id'] = object_entity_id

            # Delete existing region if it exists
            existing_landing_region = self._workspace.get_entities_by_name('landing_region')
            if len(existing_landing_region) > 0:
                self._workspace.delete_entity(existing_landing_region[0])

            # Create a reagion around the seat locator. Default 1x1x1 meters
            landing_region_id = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Region, 'landing_region', seat_locator)

            # Resize the region to 70x70x70 cm
            width = 0.5
            depth = 0.4
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','width', width)
            # self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','height', 0.7)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','depth', depth)

            # Apply position offset to separate from the back of the seat to avoid "flying" objects
            pos_offset_y = 0
            pos_offset_x = 0.25
            landing_region_pos = self._workspace.get_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position')
            landing_region_pos.x += pos_offset_x
            landing_region_pos.y += pos_offset_y
            self._workspace.set_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position',landing_region_pos)

            # Get the car id and insert it in the set of port entities
            # The car is goign to be the only one for the time being
            the_car = self._workspace.get_entities_by_name('The_Car')[0]
            port_entities = city_builder.core.EntitySet()
            # port_entities.insert(the_car)
            port_entities.insert(character_id)

            # place the object in the in the region and land it in the car seat
            # For next version to control lander orientation and position 
            # self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id, -1, True, False, 10)
            self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id)
            self._workspace.set_entity_property_value(object_entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")

            # WORKAROUND: Set instance if possible ALWAYS to False so custom metadata
            # for identical objects is always exported. Until ANYS-3660 is fixed
            self.setInstanceIfPossible(object_entity_id, False)

            # Set custom meta data for the object
            self.setExportAlwaysExcludeOcclusion(object_entity_id)
            object['Seatbelt_on'] = False
            object['Face'] = ''
            self.setObjectInfo(object)
            self.setSeatInfo(object)
            object['Accessory'] = 'None'

        else:
            # No matching objects found returning id -1
            object_entity_id = -1
            object = None

        return object

    #_______________________________________________________________
    def placeBabyOnCharacter(self, seat_locator, character_id, name = None, version = None):
        print('[INFO] Placing baby on {}'.format(self._workspace.get_entity_name(character_id)))

        # select a named baby from resoures
        baby_id, baby = self.selectBaby('', '', True, name='Baby02') if random.uniform(0,1) < 0.5 else self.selectBaby('', '', False, name='Baby01')
        print('[INFO] Baby on character {}'.format(baby['resource_name']))
        
        if baby_id != -1:
            # Create the baby fixed entity
            baby_entity_id = self._workspace.create_fixed_entity(baby['resource_name'], seat_locator, baby_id)
            scale_factor = random.uniform(0.75, 0.95) if '02' in baby['resource_name'] else 1
            if scale_factor != 1:
                print('[INFO] Rescaling baby to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(baby_entity_id,round(scale_factor, 2))
            baby['fixed_entity_id'] = baby_entity_id

            # Delete existing region if it exists
            existing_landing_region = self._workspace.get_entities_by_name('landing_region')
            if len(existing_landing_region) > 0:
                self._workspace.delete_entity(existing_landing_region[0])

            # Create a reagion around the seat locator. Default 1x1x1 meters
            landing_region_id = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Region, 'landing_region', seat_locator)

            # Resize the region to 70x70x70 cm
            width = 0.5
            depth = 0.4
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','width', width)
            # self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','height', 0.7)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','depth', depth)

            # Apply position offset to separate from the back of the seat to avoid "flying" babies
            pos_offset_y = 0
            pos_offset_x = 0.25
            landing_region_pos = self._workspace.get_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position')
            landing_region_pos.x += pos_offset_x
            landing_region_pos.y += pos_offset_y
            self._workspace.set_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position',landing_region_pos)

            # Get the car id and insert it in the set of port entities
            # The car is goign to be the only one for the time being
            the_car = self._workspace.get_entities_by_name('The_Car')[0]
            port_entities = city_builder.core.EntitySet()
            # port_entities.insert(the_car)
            port_entities.insert(character_id)

            # place the baby in the in the region and land it on the character
            # For next version to control lander orientation and position 
            self._workspace.placement.place_entity_on_entities(baby_entity_id, port_entities, landing_region_id, -1, True, False, 10)
            self._workspace.set_entity_property_value(baby_entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")

            # WORKAROUND: Set instance if possible ALWAYS to False so custom metadata
            # for identical babies is always exported. Until ANYS-3660 is fixed
            self.setInstanceIfPossible(baby_entity_id, False)

            # Set custom meta data for the baby
            self.setExportAlwaysExcludeOcclusion(baby_entity_id)
            baby['Seatbelt_on'] = False
            baby['Face'] = ''
            self.setCharacterInfo(baby)
            self.setSeatInfo(baby)
            baby['Accessory'] = 'None'

        else:
            # No matching babies found returning id -1
            baby_entity_id = -1
            baby = None

        return baby

    #_______________________________________________________________
    def placeObjectInChildseat(self, seat_locator, childseat, object_types = None, name = None, version = None):
        seat_id = childseat['fixed_entity_id']
        print('[INFO] Placing object on {}'.format(self._workspace.get_entity_name(seat_id)))

        big_object = False

        # select an object from resources, of specified name and version,
        # or from specified types list, or from all in-cabin compliant objects 
        object = self.selectObject(name, version, object_types, big_object)
        if object and object['entity_id'] != -1:
            print('[INFO] Object to place {}'.format(object['resource_name']))
            # Create the object fixed entity
            try:
                object_entity_name = object['resource_name']+'_'+object['version'] if 'version' in object else object['resource_name']
                object_entity_id = self._workspace.create_fixed_entity(object_entity_name, seat_locator, object['entity_id'])
                scale_factor = random.uniform(float(object['min_scale'].replace(',','.')), float(object['max_scale'].replace(',','.')))
            except KeyError as ke:
                print('[WARN] wrong asset {}: {}'.format(object['resource_name'], ke))
                if 'scale' in str(ke):
                    print('[WARN] Scale attributes missing')
                    scale_factor = 1
            except AttributeError:
                scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))

            if scale_factor != 1:
                print('[INFO] Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['fixed_entity_id'] = object_entity_id
            is_animal = True if object['class'].lower() == ['dog', 'cat'] else False

            if 'dynamic_material' in object and object['dynamic_material']:
                self.changeExposedMaterials(object_entity_id, object)

            # Delete existing region if it exists
            existing_landing_region = self._workspace.get_entities_by_name('landing_region')
            if len(existing_landing_region) > 0:
                self._workspace.delete_entity(existing_landing_region[0])

            # Create a reagion around the seat locator. Default 1x1x1 meters
            landing_region_id = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Region, 'landing_region', seat_locator)

            # Resize the region to 70x70x70 cm
            width = 0.4
            depth = 0.4
            height = 0.5
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','width', width)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','height', height)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','depth', depth)

            # Apply position offset to separate from the back of the seat to avoid "flying" objects
            # pos_offset_y = 0
            # pos_offset_x = 0.25
            # landing_region_pos = self._workspace.get_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position')
            # landing_region_pos.x += pos_offset_x
            # landing_region_pos.y += pos_offset_y
            # self._workspace.set_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position',landing_region_pos)

            # Get the car id and insert it in the set of port entities
            # The car is goign to be the only one for the time being
            port_entities = city_builder.core.EntitySet()
            port_entities.insert(seat_id)

            # place the object in the in the region and land it in the car seat
            # For next version to control lander orientation and position 
            if is_animal: 
                animal_rot = self._workspace.get_entity_property_value(object_entity_id, 'RelativeTransformToComponent','rotation')
                animal_rot.z = random.randrange(360)
                self._workspace.set_entity_property_value(object_entity_id, 'RelativeTransformToComponent','rotation', animal_rot)
                self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id, -1, True, False, 5)
            else:
                self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id)
            self._workspace.set_entity_property_value(object_entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")

            if 'dynamic_material' in object and object['dynamic_material']:
                self.changeExposedMaterials(object_entity_id, object)

            # WORKAROUND: Set instance if possible ALWAYS to False so custom metadata
            # for identical objects is always exported. Until ANYS-3660 is fixed
            self.setInstanceIfPossible(object_entity_id, False)

            # Set custom meta data for the object
            self.setExportAlwaysExcludeOcclusion(object_entity_id)
            object['Seatbelt_on'] = False
            object['Seatbelt_placement'] = 'Off'
            object['Face'] = ''
            self.setObjectInfo(object)
            self.setSeatInfo(object)
            object['Accessory'] = 'None'

            # Overwriting seat info to update occupancy
            self.setChildseatInfo(childseat)
            self.setSeatInfo(childseat)

        else:
            # No matching objects found returning id -1
            object_entity_id = -1
            object = None

        return object

    #_______________________________________________________________
    def placeObjectOnSeat(self, seat_locator, seat_id, object_types = None, name = None, version = None):
        print('[INFO] Placing object on {}'.format(self._workspace.get_entity_name(seat_id)))

        big_object = True if random.uniform(0,1) >= 0.75 and not self.isMiddleBackSeat(seat_locator) else False
        big_object = False # HACK for Continental
        print('[INFO] Big object: {}'.format(big_object))

        # select an object from resources, of specified name and version,
        # or from specified types list, or from all in-cabin compliant objects 
        object = self.selectObject(name, version, object_types, big_object)
        if object and object['entity_id'] != -1:
            print('[INFO] Object to place {}'.format(object['resource_name']))
            # Create the object fixed entity
            try:
                object_entity_name = object['resource_name']+'_'+object['version'] if 'version' in object else object['resource_name']
                object_entity_id = self._workspace.create_fixed_entity(object_entity_name, seat_locator, object['entity_id'])
                scale_factor = random.uniform(float(object['min_scale'].replace(',','.')), float(object['max_scale'].replace(',','.')))
            except KeyError as ke:
                print('[WARN] wrong asset {}: {}'.format(object['resource_name'], ke))
                if 'scale' in str(ke):
                    print('[WARN] Scale attributes missing')
                    scale_factor = 1
            except AttributeError:
                scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))

            if scale_factor != 1:
                print('[INFO] Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['fixed_entity_id'] = object_entity_id
            is_animal = True if object['class'].lower() == 'dog' or object['class'].lower() == 'cat' else False

            # Delete existing region if it exists
            existing_landing_region = self._workspace.get_entities_by_name('landing_region')
            if len(existing_landing_region) > 0:
                self._workspace.delete_entity(existing_landing_region[0])

            # Create a region around the seat locator. Default 1x1x1 meters
            landing_region_id = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Region, 'landing_region', seat_locator)

            # Resize the region to 70x70x70 cm
            width = 0.5
            depth = 0.4
            height = 1
            if big_object:
                width = 0.70
                depth = 0.70
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','width', width)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','height', height)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','depth', depth)

            # Apply position offset to separate from the back of the seat to avoid "flying" objects
            if big_object:
                pos_offset_y = 0
                pos_offset_x = 0.15
                landing_region_pos = self._workspace.get_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position')
                landing_region_pos.x += pos_offset_x
                landing_region_pos.y += pos_offset_y
                self._workspace.set_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position',landing_region_pos)

            # Get the car id and insert it in the set of port entities
            # The car is goign to be the only one for the time being
            port_entities = city_builder.core.EntitySet()
            port_entities.insert(seat_id)

            # place the object in the in the region and land it in the car seat
            # For next version to control lander orientation and position
            if is_animal: 
                animal_rot = self._workspace.get_entity_property_value(object_entity_id, 'RelativeTransformToComponent','rotation')
                animal_rot.z = random.randrange(360)
                self._workspace.set_entity_property_value(object_entity_id, 'RelativeTransformToComponent','rotation', animal_rot)
                self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id, -1, True, False, 15)
            else:
                self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id)
            self._workspace.set_entity_property_value(object_entity_id, "Viewport3DEntityConfigurationComponent", "visualization_mode", "Mesh")

            # WORKAROUND: Set instance if possible ALWAYS to False so custom metadata
            # for identical objects is always exported. Until ANYS-3660 is fixed
            self.setInstanceIfPossible(object_entity_id, False)

            # Set custom meta data for the object
            self.setExportAlwaysExcludeOcclusion(object_entity_id)
            object['Seatbelt_on'] = False
            object['Seatbelt_placement'] = 'Off'
            object['Face'] = ''
            self.setObjectInfo(object)
            self.setSeatInfo(object)
            object['Accessory'] = 'None'

        else:
            # No matching objects found returning id -1
            object_entity_id = -1
            object = None

        return object

    #_______________________________________________________________
    def placeDriver(self, seat_locator, occupant = None, seatbelts_distribution = None, accessories_probabilities = None, expression_probabilities = None, age_group_probabilities = None, allow_child_driver = False):
        print('[INFO] Placing Driver in {}'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))

        # Select a random character based on age-group probabilities if not None
        # otherwise select a random adult 
        if age_group_probabilities:
            print('[INFO] Allow child driver: {}'.format(allow_child_driver))
            if allow_child_driver:
                age_group_idx = self.choiceUsingProbabilities([ float(o['probability']) for o in age_group_probabilities ])
            else:
                age_group_probabilities = [ o for o in age_group_probabilities if 'Adult' == o['kind'] ]
                print(age_group_probabilities)
                age_group_idx = self.choiceUsingProbabilities([ float(o['probability']) for o in age_group_probabilities ])
            age_group = age_group_probabilities[age_group_idx]['age_group']
            print('[INFO] driver age group: {}'.format(age_group))
            driver_asset_id, driver = self.selectCharacter('agegroup', age_group)
            # kind = age_group_probabilities['age_group_idx']['kind']
            # driver_asset_id, driver = self.selectCharacter('kind', kind, name)
        elif occupant:
            driver_asset_id, driver = occupant['entity_id'], occupant
        else:
            driver_asset_id, driver = self.selectCharacter('kind', 'Adult')

        if driver_asset_id != -1:
            driver_id = self._workspace.create_fixed_entity(driver['name'], seat_locator, driver_asset_id)

            driver['fixed_entity_id'] = driver_id

            bright_pupil = False
            if self.setBrightPupil():
                bright_pupil_material = self.getBrightPupilMaterial()
                if bright_pupil_material != anyverse_platform.invalid_entity_id:
                    bright_pupil = self.changeMaterial(driver_id, '.*_eye_pupil$', bright_pupil_material)
            if bright_pupil:
                print('[INFO] Pupil should be bright under NIR light')

            bright_iris = False
            if self.setBrightIris(seat_locator):
                bright_nir_material = self.getBrightPupilMaterial()
                if bright_nir_material != anyverse_platform.invalid_entity_id:
                    bright_iris = self.changeMaterial(driver_id, '.*_eye_iris$', bright_nir_material)
            if bright_iris:
                print('[INFO] Iris should be bright under NIR light')

            # set driver pose
            animation = self.getAnimIdByName('Driving')
            self.setAnimation('base', animation, 1.0, driver_id)
            # Grab the steering wheel by default
            self.grabSteeringWheel(driver_id)

            # setting spine animation 50% of the times
            set_spine_anim = True if random.uniform(0,1) <= 0.3 else False
            if set_spine_anim:
                max_weight = 1 if self._seat_collision else 0.15 # Avoid extreme weights for leaning if no seat_collision
                animation, weight = self.selectAdultAnimation('spine', 0, max_weight)
                spine_animation_name = self._workspace.get_entity_name(animation)
                if 'side_ward' in spine_animation_name or 'backward' in spine_animation_name:
                    weight = 0.8 if weight >= 0.8 else weight # cap the weight until extreme cases work properly with the colliders
                if 'extreme' in spine_animation_name and weight < 0.5:
                    weight = 0.5

                self.setAnimation('spine', animation, weight, driver_id)

            # Set one arm animation for half the samples
            animate_arms = True if random.uniform(0,1) <= 0.5 else False
            if  animate_arms:
                arms = ['left_arm', 'right_arm']
                arm = random.randint(0,1)
                if arm == 1:
                    animation, weight = self.selectAdultAnimation(arms[arm], 0, 0.5)
                else:
                    animation, weight = self.selectAdultAnimation(arms[arm], 0, 1)
                self.setAnimation(arms[arm], animation, weight, driver_id)

            # setting head animation
            # This is done now when setting the gaze
            # after all occupants are placed. Controlled by probability 

            # Decide if we fasten the seat belt or not
            fasten_seatbelt = self.decideFastenSeatbelt(driver, seatbelts_distribution['belt_on_probability'])
            driver['Seatbelt_on'] = fasten_seatbelt
            driver['Seatbelt_placement'] = 'Normal' if fasten_seatbelt else 'Off'

            # Place accessories on the driver according to external probabilities
            if accessories_probabilities != None:
                place_accessories = True if random.uniform(0,1) < accessories_probabilities['global'] else False
            else:
                place_accessories = False

            accessories = []
            driver['Accessory'] = 'None'
            if place_accessories:
                print('[INFO] Placing accessories...')
                accessories = self.placeAccessories(driver, accessories_probabilities)

                if len(accessories) == 0:
                    print('[WARN] Cannot place any accessory to {}'.format(driver['name']))
                for accessory in accessories:
                    print('[INFO] Placed {} on driver {}'.format(accessory['class'], driver['name']))
                    accessory['Character'] = driver['name']
                    driver['Accessory'] = accessory['class']+'.'+accessory['name'] if driver['Accessory'] == 'None' else driver['Accessory'] + '|' + accessory['class']+'.'+accessory['name']
                    self.setAccessoryInfo(accessory)
            else:
                print('[INFO] Not placing accessories for driver {}'.format(driver['name']))
            
            # Set an expression based on probabilities
            # or 'neutral' if no probabilities defined 
            if expression_probabilities != None:
                expression_idx = self.choiceUsingProbabilities([ float(o['probability']) for o in expression_probabilities ])
                picked_expression = expression_probabilities[expression_idx]
                self.setNamedFaceExpression(driver_id, picked_expression['expression'])
                driver['Face'] = picked_expression['name']
            else:
                # Set Neutral facial expression
                self.setNamedFaceExpression(driver_id, 0)
                driver['Face'] = 'neutral'

            if fasten_seatbelt and not self._script_console:
                belt_placement = self.createBeltFor(self.getSeatPos(seat_locator), driver_id, self._car_brand, self._car_model, seatbelts_distribution = seatbelts_distribution)
                if belt_placement:
                    driver['Seatbelt_placement'] = belt_placement
                else:
                    driver['Seatbelt_placement'] = 'Off'
                    driver['Seatbelt_on'] = False
                    print('[ERROR] Cannot create belt')                    

            self.setExportAlwaysExcludeOcclusion(driver_id)
            self.setAvoidArmsAutoCollision(driver_id, True)
            if self._seat_collision:
                self.setSeatCollision(driver_id, 'SeatSearchedInAncestors')
            self.removeMotionBlur(driver_id)
            self.applyCharacterOffset(driver)
            self.setCharacterInfo(driver)
            self.setCharacterPoseInfo(driver)
            self.setSeatInfo(driver)

            self._already_used_characters.append(driver['model'])
        else:
            # No matching drivers found returning id -1
            if driver != None:
                driver['fixed_entity_id'] = driver_asset_id
                print('[ERROR] Driver {} not found in resources!'.format(driver['name']))
                driver = None

        return driver

    #_______________________________________________________________
    def selectChildseat(self, key, value, orientation = None, name = None):
        childseats = self._workspace.childseats
        if name == None:
            filtered_childseats = self.filterCharacters(childseats, key, value)
        else:
            filtered_childseats = self.filterCharacters(childseats, 'name', name)

        # Filter by orientation if convertible
        if key == 'kind' and (value == 'Convertible' or value == 'BabyChild') and orientation is not None:
            filtered_childseats = [ cs for cs in filtered_childseats if cs['aim looking'].lower() == orientation.lower() ]

        # pick one randomly
        if len(filtered_childseats) > 0:
            childseat_idx = random.randrange(len(filtered_childseats))
            childseat = filtered_childseats[childseat_idx]
            # Pick the only possible asset and set the orientation from the childseat dictionary
            childseat['Orientation'] = childseat['aim looking']
            childseat_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, childseat['resource_id'])
        else:
            childseat_asset_id = -1
            childseat = None

        return childseat_asset_id, childseat

    #_______________________________________________________________
    def applyPositionOffset(self, entity_id, offset):
        print('[INFO] Applying position offset to child seat in front passenger seat')
        pos = self._workspace.get_entity_property_value(entity_id, 'RelativeTransformToComponent','position')
        pos += offset
        self._workspace.set_entity_property_value(entity_id, 'RelativeTransformToComponent','position', pos)
        
    #_______________________________________________________________
    def placeChildseat(self, seat_locator, childseat_config, name = None, only_baby_in_copilot = True):
        childseat_type_probabilities = childseat_config['childseat_type_probabilities']
        childseat_orientation_probabilities = childseat_config['childseat_orientation_probabilities']
        childseat_probabilities = [ float(t['probability']) for t in childseat_type_probabilities ]
        orientation_probabilities = [ float(t['probability']) for t in childseat_orientation_probabilities ]
        max_rotation = childseat_config['childseat_rotation_max']
        pos_offset = anyverse_platform.Vector3D(-0.15, 0, 0)

        # Only baby child seat in copilot front seat
        if self.isCopilotSeat(seat_locator) and only_baby_in_copilot:
            childseat_type_idx = 0
        # Only booster seat in middle back seat
        # elif self.isMiddleBackSeat(seat_locator):
        #     childseat_type_idx = 2
        else:
            childseat_type_idx = self.choiceUsingProbabilities(childseat_probabilities)

        childseat_type = childseat_type_probabilities[childseat_type_idx]['Type']
        orientation = None
        # select a random childseat of the given type and orientation
        if childseat_type == 'BabyChild':
            orientation_idx = self.choiceUsingProbabilities(orientation_probabilities)
            orientation = childseat_orientation_probabilities[orientation_idx]['Orientation']
            childseat_asset_id, childseat = self.selectChildseat('kind', childseat_type, orientation, name)
            if self.isCopilotSeat(seat_locator):
                pos_offset = anyverse_platform.Vector3D(-0.15, 0, 0)
        else:
            orientation = 'Forward'
            childseat_asset_id, childseat = self.selectChildseat('kind',childseat_type, orientation, name)

        if childseat_asset_id != -1:
            childseat_id = self._workspace.create_fixed_entity(childseat['resource_name'], seat_locator, childseat_asset_id)
            if pos_offset:
                self.applyPositionOffset(childseat_id, pos_offset)
            childseat['fixed_entity_id'] = childseat_id
            print('[INFO] Placing Childseat {} in {}'.format(childseat['name'], self._workspace.get_entity_name(seat_locator).split('_')[0]))

            mu, sigma = 0, max_rotation/3.6
            yaw = random.normalvariate(mu, sigma)
            # REMOVE this code. It doesn't make sense. I think it was left here from a customer request
            # who wanted all baby childseats facing backwards, but even so the orientation metadata was wrong!!!
            #
            # if childseat_type == 'BabyChild' and orientation == 'Forward':
            #     childseat['Orientation']  = orientation
            #     yaw += 180
            #     pos = self._workspace.get_entity_property_value(childseat_id,'RelativeTransformToComponent','position')
            #     pos.x += 0.65
            #     self._workspace.set_entity_property_value(childseat_id,'RelativeTransformToComponent','position', pos)
            print('[INFO] Rotating childseat {:.2f}º'.format(yaw))
            self.wiggleChildseatRandom(childseat_id, yaw , pitch = 0)

            self.changeExposedMaterials(childseat_id, childseat)

            self.setExportAlwaysExcludeOcclusion(childseat_id)
            self.setChildseatInfo(childseat)
            self.setSeatInfo(childseat)

            # self._already_used_characters.append(childseat['name'])
        else:
            print('[WARN]: Could not find a {} childseat with orientation {}'.format(childseat_type, orientation))

        return childseat

    #_______________________________________________________________
    def placeBabyInChildseat(self, childseat, seat_locator, name = None, seatbelts_distribution = None):
        for_backseat = False
        if self.isLeftBackSeat(seat_locator) or self.isRightBackSeat(seat_locator):
            for_backseat = True

        baby_asset_id, baby = self.selectBaby('suitableseat','BabyChild', for_backseat, name)
        print('[INFO] Placing baby {} in childseat {}'.format(baby['name'], self._workspace.get_entity_name(childseat['fixed_entity_id'])))

        # get the childseat locator
        childseat_locators = [ l for l in self.getEntityLocators(childseat['fixed_entity_id']) if re.search("child.*_locator$", self._workspace.get_entity_name(l).lower()) ]
        if len(childseat_locators) == 1:
            childseat_locator = childseat_locators[0]
        else:
            print('[ERROR] Child seat missing child or childseat locator with format child.*_locator$')
            assert False

        if baby_asset_id != -1 and childseat_locator != -1:
            baby_id = self._workspace.create_fixed_entity(baby['name'], childseat_locator, baby_asset_id)
            baby['fixed_entity_id'] = baby_id
            # Babies now can have seatblets on the new child seat assets
            fasten_seatbelt = self.decideFastenSeatbelt(baby, seatbelts_distribution['belt_on_probability'])
            if fasten_seatbelt:
                self.createBabyBelt(childseat)
            baby['Seatbelt_on'] = fasten_seatbelt
            baby['Seatbelt_placement'] = 'Normal' if fasten_seatbelt else 'Off'

            if 'Cybex-CloudZ' in childseat['name']:
                updown = random.uniform(0,5)
            else:
                updown = random.uniform(-3,0)

            if self.isLeftBackSeat(seat_locator):
                self.wiggleBabyRandom(baby_id, updown, random.uniform(0, 5),random.uniform(0, 15) )
            if self.isRightBackSeat(seat_locator):
                self.wiggleBabyRandom(baby_id, updown, random.uniform(-5, 0), random.uniform(-15, 0))

            self.setInstanceIfPossible(baby_id, False)
            self.setExportAlwaysExcludeOcclusion(baby_id)
            self.setCharacterInfo(baby)
            self.setSeatInfo(baby)

            # Because of the occupancy we have to overwrite the child seat custom metadata
            self.setChildseatInfo(childseat)
            self.setSeatInfo(childseat)

            # We don't allow the same childseat repeated
            self._already_used_characters.append(baby['model'])
        elif baby_asset_id == -1:
            # No matching children found returning id -1
            print('[WARN]: could not find suitable baby for childseat')
            baby_id = -1
            baby['fixed_entity_id'] = baby_id
        else:
            # No child locator in child seat
            print('[WARN] Cannot place child without a locator in child seat.')

        return baby

    #_______________________________________________________________
    def placeChildInChildseat(self, childseat, seat_locator, name  = None, seatbelts_distribution = None, expression_probabilities = None):
        # select a random child character sutable for a childseat
        suitable_child = False
        while not suitable_child:
            child_asset_id, child = self.selectCharacter('kind','Child', name)
            if child['suitableseat'] != 'None' and child['suitableseat'] == childseat['kind']:
                suitable_child = True
            else:
                # print('[WARN] Child {} not suitable for chilsseat {}. Trying a different one...'.format(child['name'], childseat['name']))
                continue

        print('[INFO] Placing child {} in childseat {}'.format(child['name'], self._workspace.get_entity_name(childseat['fixed_entity_id'])))

        # get the childseat locator
        childseat_locators = [ l for l in self.getEntityLocators(childseat['fixed_entity_id']) if re.search("child.*_locator$", self._workspace.get_entity_name(l).lower()) ]
        if len(childseat_locators) == 1:
            childseat_locator = childseat_locators[0]
        else:
            print('[ERROR] Child seat missing child or childseat locator with format child.*_locator$')
            assert False

        if child_asset_id != -1 and childseat_locator != -1:
            child_id = self._workspace.create_fixed_entity(child['name'], childseat_locator, child_asset_id)

            child['fixed_entity_id'] = child_id

            bright_pupil = False
            if self.setBrightPupil():
                bright_nir_material = self.getBrightPupilMaterial()
                if bright_nir_material != anyverse_platform.invalid_entity_id:
                    bright_pupil = self.changeMaterial(child_id, '.*_eye_pupil$', bright_nir_material)
            if bright_pupil:
                print('[INFO] Pupil should be bright under NIR light')

            bright_iris = False
            if self.setBrightIris(seat_locator):
                bright_nir_material = self.getBrightPupilMaterial()
                if bright_nir_material != anyverse_platform.invalid_entity_id:
                    bright_iris = self.changeMaterial(child_id, '.*_eye_iris$', bright_nir_material)
            if bright_iris:
                print('[INFO] Iris should be bright under NIR light')

            # Decide if we fasten the seat belt or not
            # Never fasten seatbelt if it's a big baby or if the convertible backwards
            # For the other children in convertibles we always fasten the seatbelts to have a 50/50
            # considering the re are 4 big babies and 4 children characters suitable for convertibles.
            # Fastening seat belts affect what base animation we set: only sitting straight when seat belts fastened
            if 'Baby' in child['name'] or childseat['Orientation'] == 'Backward' or childseat['kind'] == 'Booster':
                fasten_seatbelt = False
            else:
                fasten_seatbelt = self.decideFastenSeatbelt(child, seatbelts_distribution['belt_on_probability'])

            child['Seatbelt_on'] = fasten_seatbelt
            child['Seatbelt_placement'] = 'Normal' if fasten_seatbelt else 'Off'

            # set child pose if not a big baby
            if 'Baby' not in child['name']:
                if fasten_seatbelt:
                    animation, weight = self.getChildSittingStraightAnimation(seat_locator)
                else:
                    animation, weight = self.selectChildAnimation(seat_locator, 'base', 0, 0.6)
                self.setAnimation('base', animation, weight, child_id)
                # Set spine animation
                animation, weight = self.selectChildAnimation(seat_locator, 'spine', 0, 1)
                self.setAnimation('spine', animation, weight, child_id)
                # Set arms animation
                if self.isCopilotSeat(seat_locator) or self.isRightBackSeat(seat_locator):
                    animate_left_arm = True if random.uniform(0,1) < 0.2 else False
                    animate_right_arm = True if random.uniform(0,1) < 0.5 else False
                    left_arm_max_weight = 0.4
                    right_arm_max_weight = 1.0
                if  self.isLeftBackSeat(seat_locator):
                    animate_left_arm = True if random.uniform(0,1) < 0.5 else False
                    animate_right_arm = True if random.uniform(0,1) < 0.2 else False
                    left_arm_max_weight = 1.0
                    right_arm_max_weight = 0.4
                if  self.isMiddleBackSeat(seat_locator):
                    animate_left_arm = True if random.uniform(0,1) < 0.5 else False
                    animate_right_arm = True if random.uniform(0,1) < 0.5 else False
                    left_arm_max_weight = 0.5
                    right_arm_max_weight = 0.5

                arms_min_weight = 0.2
                if self.isLeftBackSeat(seat_locator) or self.isRightBackSeat(seat_locator):
                    arms_min_weight = 0.75

                if animate_left_arm:
                    arm = 'left_arm'
                    animation, weight = self.selectChildAnimation(seat_locator, arm, arms_min_weight, left_arm_max_weight)
                    self.setAnimation(arm, animation, weight, child_id)
                # Animate right arm
                if animate_right_arm:
                    arm = 'right_arm'
                    animation, weight = self.selectChildAnimation(seat_locator, arm, arms_min_weight, right_arm_max_weight)
                    self.setAnimation(arm, animation, weight, child_id)

                # setting head animation
                animation, weight = self.selectChildAnimation(seat_locator, 'head', 0, 1)
                self.setAnimation('head', animation, weight, child_id)

                # Set an expression based on probabilities
                # or 'neutral' if no probabilities defined 
                if expression_probabilities != None:
                    expression_idx = self.choiceUsingProbabilities([ float(o['probability']) for o in expression_probabilities ])
                    picked_expression = expression_probabilities[expression_idx]
                    self.setNamedFaceExpression(child_id, picked_expression['expression'])
                    child['Face'] = picked_expression['name']
                else:
                    # Set Neutral facial expression
                    self.setNamedFaceExpression(child_id, 0)
                    child['Face'] = 'neutral'
                
                # Set the pose info only if it is not a baby
                self.setCharacterPoseInfo(child)
            # If a Big Baby wiggle them a little bit and set the flag to not treat them as instances
            else:
                if self.isLeftBackSeat(seat_locator):
                    self.wiggleBabyRandom(child_id, 0, random.uniform(-10, 3),random.uniform(-15, 15) )
                if self.isRightBackSeat(seat_locator):
                    self.wiggleBabyRandom(child_id, 0, random.uniform(0, 10), random.uniform(-15, 15))
                self.setInstanceIfPossible(child_id, False)

            if childseat['kind'] == 'Booster':
                if fasten_seatbelt and not self._script_console:
                    print('[INFO] Setting seat belt for booster...')
                    belt_placement = self.createBeltFor(self.getSeatPos(seat_locator), child_id, self._car_brand, self._car_model, seatbelts_distribution)
                    if belt_placement:
                        child['Seatbelt_placement'] = belt_placement
                        child['Seatbelt_on'] = True
                    else:
                        child['Seatbelt_placement'] = 'Off'
                        child['Seatbelt_on'] = False
                        print('[ERROR] Cannot create belt')                    
                else:
                    child['Seatbelt_placement'] = 'Off'
                    child['Seatbelt_on'] = False

            if childseat['kind'] == 'Convertible':
                if fasten_seatbelt and not self._script_console:
                    print('[INFO] Setting child seat belt for child {}'.format(child['name']))
                    self.createChildBelt( child_id, childseat['fixed_entity_id'], self._clip_asset, self.getSeatPos(seat_locator), None )
                    child['Seatbelt_placement'] = 'Normal'

            self.setExportAlwaysExcludeOcclusion(child_id)
            self.setAvoidArmsAutoCollision(child_id, True)
            if self._seat_collision:
                self.setSeatCollision(child_id, 'SeatEntity', collision_entity_id=childseat['fixed_entity_id'])
            self.removeMotionBlur(child_id)
            self.setCharacterInfo(child)
            self.setSeatInfo(child)

            # Because of the occupancy we have to overwrite the child seat custom metadata
            self.setChildseatInfo(childseat)
            self.setSeatInfo(childseat)

            self._already_used_characters.append(child['model'])
        elif child_asset_id == -1:
            # No matching children found returning id -1
            print('[WARN]: could not find suitable child for childseat')
            child_id = -1
            child['fixed_entity_id'] = child_id
        else:
            # No child locator in child seat
            print('[WARN] Cannot place child without a locator in child seat.')

        return child

    #_______________________________________________________________
    def placePassenger(self, seat_locator, occupant = None, seatbelts_distribution = None, accessories_probabilities = None, expression_probabilities = None, baby_on_lap = False):
        print('[INFO] Placing Passenger in {} ({})'.format(self._workspace.get_entity_name(seat_locator).split('_')[0], seat_locator))
        # select a random adult character
        # select a random childseat of the given type
        
        if occupant:
            passenger = occupant
            passenger_id = self._workspace.create_fixed_entity(occupant['resource_name'], seat_locator, occupant['entity_id'])
            passenger_found = True
        else:
            passenger_found = False
        stop_searching = False
        while not passenger_found and not stop_searching:
            passenger_asset_id, passenger = self.selectCharacter('kind','Adult', occupant)
            if passenger_asset_id != -1:
                passenger_id = self._workspace.create_fixed_entity(passenger['resource_name'], seat_locator, passenger_asset_id)
                passenger_found = True
            else:
                # No matching passengers found returning id -1
                if passenger == None:
                    print('[WARN]: Could not find valid passenger to place')
                    stop_searching = True
                else:
                    print('[WARN]: Could not find a passenger {} to place. Trying another one...'.format(passenger['name']))
                passenger_id = -1

        body_min_weight = 0
        body_max_weight = 1

        if passenger_found:
            passenger['fixed_entity_id'] = passenger_id

            bright_pupil = False
            if self.setBrightPupil():
                bright_pupil_material = self.getBrightPupilMaterial()
                if bright_pupil_material != anyverse_platform.invalid_entity_id:
                    bright_pupil = self.changeMaterial(passenger_id, '.*_eye_pupil$', bright_pupil_material)
            if bright_pupil:
                print('[INFO] Pupil should be bright under NIR light')

            bright_iris = False
            if self.setBrightIris(seat_locator):
                bright_nir_material = self.getBrightPupilMaterial()
                if bright_nir_material != anyverse_platform.invalid_entity_id:
                    bright_iris = self.changeMaterial(passenger_id, '.*_eye_iris$', bright_nir_material)
            if bright_iris:
                print('[INFO] Iris should be bright under NIR light')

            # Decide if we faten the seat belt or not
            fasten_seatbelt = self.decideFastenSeatbelt(passenger, seatbelts_distribution['belt_on_probability'])
            passenger['Seatbelt_on'] = fasten_seatbelt
            passenger['Seatbelt_placement'] = 'Normal' if fasten_seatbelt else 'Off'

            # set passenger pose. If we fasten the seat belt the base pose will always by sitting straight
            if (self.isCopilotSeat(seat_locator)): # and fasten_seatbelt:
                animation, weight = self.getAdultSittingStraightAnimation(seat_locator)
            else:
                animation, weight = self.selectAdultAnimation('base', body_min_weight, body_max_weight)

            self.setAnimation('base', animation, weight, passenger_id)
            base_animation_name = self._workspace.get_entity_name(animation)

            # setting spine animation 30% of the times
            set_spine_anim = True if random.uniform(0,1) <= 0.3 and not baby_on_lap else False
            if set_spine_anim:
                if self.isCopilotSeat(seat_locator):
                    max_weight = 1 if self._seat_collision else 0.3 # Avoid extreme weights for leaning if no seat_collision
                else:
                    max_weight = 0.5 if self._seat_collision else 0.3 # Avoid extreme weights for leaning if no seat_collision
                animation, weight = self.selectAdultAnimation('spine', 0, max_weight)
                spine_animation_name = self._workspace.get_entity_name(animation)
                if 'side_ward' in spine_animation_name or 'backward' in spine_animation_name:
                    weight = 0.8 if weight >= 0.8 else weight # cap the weight until extreme cases work properly with the colliders
                if 'extreme' in spine_animation_name and weight < 0.5:
                    weight = 0.5

                self.setAnimation('spine', animation, weight, passenger_id)

            # Set arms animation if not baby on lap
            if not baby_on_lap:
                animate_left_arm = False if random.uniform(0,1) <= 0.05 else True
                animate_right_arm = False if random.uniform(0,1) <= 0.05 else True
            else:
                animate_left_arm = False
                animate_right_arm = False
        
            if self.isCopilotSeat(seat_locator) or self.isRightBackSeat(seat_locator):
                left_arm_max_weight = 0.65
                right_arm_max_weight = 1.0
            if  self.isLeftBackSeat(seat_locator) or self.isMiddleBackSeat:
                left_arm_max_weight = 1.0
                right_arm_max_weight = 0.2

            arms_min_weight = 0.2 if set_spine_anim and 'extreme' not in spine_animation_name else 0.5
            if animate_left_arm:
                arm = 'left_arm'
                animation, weight = self.selectAdultAnimation(arm, 0.35, left_arm_max_weight) # left arm min weight enough to avoid seatbelt collision
                self.setAnimation(arm, animation, weight, passenger_id)
            # Animate right arm
            if animate_right_arm:
                arm = 'right_arm'
                animation, weight = self.selectAdultAnimation(arm, arms_min_weight, right_arm_max_weight)
                self.setAnimation(arm, animation, weight, passenger_id)

            # setting head animation
            # For copilot this is controlled by the gaze settings. 
            # For other passengers we set a head animation
            if  not self.isCopilotSeat(seat_locator):
                animation, weight = self.selectAdultAnimation('head', 0, 0.8)
                self.setAnimation('head', animation, weight, passenger_id)

            # Place accessories on the passenger according to external probabilities
            if accessories_probabilities != None:
                place_accessories = True if random.uniform(0,1) < accessories_probabilities['global'] else False
            else:
                place_accessories = False

            accessories = []
            passenger['Accessory'] = 'None'
            if place_accessories:
                print('[INFO] Placing accessories...')
                accessories = self.placeAccessories(passenger, accessories_probabilities)

                if len(accessories) == 0:
                    print('[WARN] Cannot place any accessory to {}'.format(passenger['name']))
                for accessory in accessories:
                    accessory['Character'] = passenger['name']
                    passenger['Accessory'] = accessory['class']+'.'+accessory['name'] if passenger['Accessory'] == 'None' else passenger['Accessory'] + '|' + accessory['class']+'.'+accessory['name']
                    self.setAccessoryInfo(accessory)
            else:
                print('[INFO] Not placing accessories for passenger {}'.format(passenger['name']))

            # Set an expression based on probabilities
            # or 'neutral' if no probabilities defined 
            if expression_probabilities != None:
                expression_idx = self.choiceUsingProbabilities([ float(o['probability']) for o in expression_probabilities ])
                picked_expression = expression_probabilities[expression_idx]
                self.setNamedFaceExpression(passenger_id, picked_expression['expression'])
                passenger['Face'] = picked_expression['name']
            else:
                # Set Neutral facial expression
                self.setNamedFaceExpression(passenger_id, 0)
                passenger['Face'] = 'neutral'

            if fasten_seatbelt and not self._script_console:
                belt_placement = self.createBeltFor(self.getSeatPos(seat_locator), passenger_id, self._car_brand, self._car_model, seatbelts_distribution = seatbelts_distribution)
                # Move the children 7 cm forward when sitting on the seatbelt
                if belt_placement is None:
                    passenger['Seatbelt_placement'] = 'Off'
                    passenger['Seatbelt_on'] = False
                    print('[ERROR] Cannot create belt')
                else:
                    if belt_placement == 'CharacterOverSeatbelt' and passenger['kind'] == 'Child':
                        pass_pos = self._workspace.get_entity_property_value(passenger_id, 'RelativeTransformToComponent', 'position')
                        pass_pos.x += 0.07
                        self._workspace.set_entity_property_value(passenger_id, 'RelativeTransformToComponent', 'position', pass_pos)
                    passenger['Seatbelt_placement'] = belt_placement
            
            # Place Baby on passenger
            if baby_on_lap:
                self.placeBabyOnCharacter(seat_locator, passenger_id)

            self.setExportAlwaysExcludeOcclusion(passenger_id)
            self.setAvoidArmsAutoCollision(passenger_id, True)
            if self._seat_collision:
                self.setSeatCollision(passenger_id, 'SeatSearchedInAncestors')
            self.removeMotionBlur(passenger_id)
            self.applyCharacterOffset(passenger)
            self.setCharacterInfo(passenger)
            self.setCharacterPoseInfo(passenger)
            self.setSeatInfo(passenger)

            self._already_used_characters.append(passenger['model'])

        return passenger

    #_______________________________________________________________
    def getBabies(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        babies = []
        for entity in fixed:
            asset_id = self._workspace.get_entity_property_value(entity, 'AssetEntityReferenceComponent','asset_entity_id')
            tags = self._workspace.get_tags_from_entity(asset_id)
            if ('person' in tags) and self.isVisible(entity) and 'Baby' in self._workspace.get_entity_name(entity):
                babies.append(entity)
        return babies

    #_______________________________________________________________
    def setCarInfo(self, car, the_car):
        car_info={}
        car_info["brand"] = car['brand']
        car_info["model"] = car['model']
        car_info["submodel"] = car['version']
        car_info["seats"] = 5

        self.setCustomMetadata(the_car, "carInfo", car_info)

        return car_info

    #_______________________________________________________________
    def getChildseats(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        childseats = []
        for entity in fixed:
            asset_id = self._workspace.get_entity_property_value(entity, 'AssetEntityReferenceComponent','asset_entity_id')
            tags = self._workspace.get_tags_from_entity(asset_id)
            if ('childseat' in tags) and self.isVisible(entity):
                childseats.append(entity)
        return childseats

    #_______________________________________________________________
    def isChildseatOccupied(self, childseat_id):
        childseat_locators = [ l for l in self._workspace.get_hierarchy(childseat_id) if 'Locator' == self._workspace.get_entity_type(l) and self.isChildseatLocator(l) ]
        childseat_locator = childseat_locators[0] if len(childseat_locators) == 1 else None
        if childseat_locator != None:
            occupants = len(self._workspace.get_hierarchy(childseat_locator))
        else:
            occupants = 0
        if occupants == 1: # means no children
            ret = False
        else:
            ret = True
        # print('[INFO] Occupied({}): {}'.format(occupants,ret))
        return ret

    #_______________________________________________________________
    def setChildseatInfo(self, childseat):
        childseat_name = childseat['name']

        childseat_info = {}
        childseat_info["type"] = childseat['kind']
        childseat_info["brand"] = childseat["brand"]
        childseat_info["orientation"] = childseat['Orientation']
        occupied = self.isChildseatOccupied(childseat['fixed_entity_id'])
        childseat_info["occupied"] = occupied
        occupant_name = ''
        if occupied:
            descendants = [ e for e in self._workspace.get_hierarchy(childseat['fixed_entity_id']) if e != childseat['fixed_entity_id'] and self._workspace.get_entity_type(e) == 'FixedEntity' ]
            occupant_name = self._workspace.get_entity_name(descendants[0]) if len(descendants) > 0 else ''
        childseat_info["occupant"] = occupant_name

        self.setCustomMetadata(childseat['fixed_entity_id'], "ChildseatInfo", childseat_info)

        return childseat_info

    #_______________________________________________________________
    def isChildseatLocator(self, locator_id):
        return self._workspace.get_entity_name(locator_id).lower() == 'childseat_locator' or self._workspace.get_entity_name(locator_id).lower() == 'babychildseat_locator' or self._workspace.get_entity_name(locator_id).lower() == 'child_locator'

    #_______________________________________________________________
    def setAdjustableSeatInfo(self, seat_id, depth, tilt):
        seat_info = {}
        seat_info["depth"] = depth
        seat_info["tilt"] = tilt

        self.setCustomMetadata(seat_id, "Position", seat_info)

        return seat_info

    #_______________________________________________________________
    def setSeatInfo(self, character):
        parent_id = self.getParent(character['fixed_entity_id'])
        if self.isChildseatLocator(parent_id ):
            locator_id = self.getParent(self.getParent(parent_id))
        else:
            locator_id = parent_id
        seat = self._workspace.get_entity_property_value(locator_id,'WorkspaceEntityComponent','name').split('_')[0]
        seat_info = {}
        seat_info["number"] = seat
        try:
            seat_info["seatbelt_on"] = character['Seatbelt_on']
            seat_info['Placement'] = character['Seatbelt_placement']
        except KeyError:
            print('[WARN] It is a child seat, no seatbelt_on info')
            seat_info["seatbelt_on"] = 'Off'
            seat_info['Placement'] = ''

        self.setCustomMetadata(character['fixed_entity_id'], "Seat", seat_info)

        return seat_info

    #_______________________________________________________________
    def setAccessoryInfo(self, accessory):
        accessory_info = {}
        accessory_info["character"] = accessory['Character']

        self.setCustomMetadata(accessory['fixed_entity_id'], "person", accessory_info)

        return accessory_info

    #_______________________________________________________________
    def getBeltsOff(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        belts_off = []
        for entity in fixed:
            asset_id = self._workspace.get_entity_property_value(entity, 'AssetEntityReferenceComponent','asset_entity_id')
            tags = self._workspace.get_tags_from_entity(asset_id)
            if ('belts' in tags) and self.isVisible(entity):
                belts_off.append(entity)
        return belts_off

    #_______________________________________________________________
    def getPassengers(self):
        fixed = self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
        passengers = []
        for entity in fixed:
            asset_id = self._workspace.get_entity_property_value(entity, 'AssetEntityReferenceComponent','asset_entity_id')
            tags = self._workspace.get_tags_from_entity(asset_id)
            if ('character' in tags) and self.isVisible(entity):
                passengers.append(entity)
        return passengers

    #_______________________________________________________________
    def setCharacterPoseInfo(self, character):
        base_animation_entity_id = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','base_anim_config.animation_entity_id')
        if base_animation_entity_id == self._no_entry:
            base_pose = 'none'
            base_pose_weight = 1.0
        else:
            base_pose = self._workspace.get_entity_property_value(base_animation_entity_id,'WorkspaceEntityComponent','name')
            base_pose_weight = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','base_anim_config.weight')

        spine_animation_entity_id = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','spine_anim_config.animation_entity_id')
        if spine_animation_entity_id == self._no_entry:
            spine_pose = 'none'
            spine_pose_weight = 1.0
        else:
            spine_pose = self._workspace.get_entity_property_value(spine_animation_entity_id,'WorkspaceEntityComponent','name')
            spine_pose_weight = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','spine_anim_config.weight')

        head_animation_entity_id = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','head_anim_config.animation_entity_id')
        if head_animation_entity_id == self._no_entry:
            head_pose = 'none'
            head_pose_weight = 1.0
        else:
            head_pose = self._workspace.get_entity_property_value(head_animation_entity_id,'WorkspaceEntityComponent','name')
            head_pose_weight = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','head_anim_config.weight')

        r_arm_animation_entity_id = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','arm_r_anim_config.animation_entity_id')
        if r_arm_animation_entity_id == self._no_entry:
            r_arm_pose = 'none'
            r_arm_pose_weight = 1.0
        else:
            r_arm_pose = self._workspace.get_entity_property_value(r_arm_animation_entity_id,'WorkspaceEntityComponent','name')
            r_arm_pose_weight = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','arm_r_anim_config.weight')

        l_arm_animation_entity_id = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','arm_l_anim_config.animation_entity_id')
        if l_arm_animation_entity_id == self._no_entry:
            l_arm_pose = 'none'
            l_arm_pose_weight = 1.0
        else:
            l_arm_pose = self._workspace.get_entity_property_value(l_arm_animation_entity_id,'WorkspaceEntityComponent','name')
            l_arm_pose_weight = self._workspace.get_entity_property_value(character['fixed_entity_id'], 'CharacterAnimationConfigurationComponent','arm_l_anim_config.weight')

        face_expression = character['Face']

        pose_info={}
        pose_info["base"] = base_pose
        pose_info["base_weight"] = base_pose_weight
        pose_info["spine"] = spine_pose
        pose_info["spine_weight"] = spine_pose_weight
        pose_info["head"] = head_pose
        pose_info["head_weight"] = head_pose_weight
        pose_info["face"] = face_expression
        pose_info["right_arm"] = r_arm_pose
        pose_info["right_arm_weight"] = r_arm_pose_weight
        pose_info["left_arm"] = l_arm_pose
        pose_info["left_arm_weight"] = l_arm_pose_weight

        self.setCustomMetadata(character['fixed_entity_id'], "Pose", pose_info)

        return pose_info

    #_______________________________________________________________
    def setObjectInfo(self, object):
        object_info={}
        object_info["class"] = object['class'] if 'class' in object else ''
        object_info["name"] = object['name'] if 'name' in object else ''
        object_info["version"] = object['version'] if 'version' in object else ''
        object_info["color"] = object['Dominant color'] if 'Dominant color' in object else ''

        self.setCustomMetadata(object['fixed_entity_id'], "Info", object_info)

        return object_info

    #_______________________________________________________________
    def setCharacterInfo(self, character):
        personal_info={}
        personal_info["gender"] = character['gender']
        personal_info["race"] = character['ethnicity']
        personal_info["type"] = character['kind']
        personal_info["age"] = character['agegroup']
        personal_info["height"] = character['height']

        self.setCustomMetadata(character['fixed_entity_id'], "Info", personal_info)

        return personal_info

    #_______________________________________________________________
    def getCamerasDict(self):
        cam_ids = self._workspace.get_camera_entities()
        cams = {}
        for cam_id in cam_ids:
            camera_name = self._workspace.get_entity_name(cam_id)
            if 'nir' in camera_name.lower():
                cams['nir'] = cam_id
            else:
                cams['rgb'] = cam_id
        return cams

    #_______________________________________________________________
    def resetLight(self, light_id):
        light_position = self._workspace.get_entity_property_value(light_id, 'RelativeTransformToComponent','position')
        light_rotation = self._workspace.get_entity_property_value(light_id, 'RelativeTransformToComponent','rotation')

        light_position.x = 0
        light_position.y = 0
        light_position.z = 0
        # light_rotation.x = 0
        # light_rotation.y = 90
        # light_rotation.z = 0

        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', light_position)
        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','rotation', light_rotation)
        self._workspace.set_entity_property_value(light_id, 'VisibleComponent','visible', False)

        return light_position, light_rotation
    
    #_______________________________________________________________
    def resetLights(self):
        light_ids = self._workspace.get_entities_by_type('Light')
        for light_id in light_ids:
            self.resetLight(light_id)

     #_______________________________________________________________
    def resetCamera(self, cam_id):
        cam_position = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','position')
        cam_rotation = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation')

        cam_position.x = 0
        cam_position.y = 0
        cam_position.z = 0
        cam_rotation.x = -90
        cam_rotation.y = 0
        cam_rotation.z = 90

        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','position', cam_position)
        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation', cam_rotation)

        return cam_position, cam_rotation
    
    #_______________________________________________________________
    def resetCameras(self):
        cam_ids = self._workspace.get_camera_entities()
        for cam_id in cam_ids:
            self.resetCamera(cam_id)

    #_______________________________________________________________
    def resetEgo(self):
        ego_id = self._ego_id
        ego_position = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','position')
        ego_rotation = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation')
        ego_scale = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','scale')

        ego_position.x = 0
        ego_position.y = 0
        ego_position.z = 0
        ego_rotation.x = 0
        ego_rotation.y = 0
        ego_rotation.z = 0
        ego_scale.x = 1
        ego_scale.y = 1
        ego_scale.z = 1

        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','position', ego_position)
        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation', ego_rotation)
        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','scale', ego_scale)

        return ego_position, ego_rotation, ego_scale

    #_______________________________________________________________
    def setEgoInPosition(self, rotation, position):
        ego_id = self._ego_id
        ego_rotation = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation')

        ego_rotation.x += rotation.x
        ego_rotation.y += rotation.y
        ego_rotation.z += rotation.z

        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','position', position)
        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation', ego_rotation)

        return position, ego_rotation

    #_______________________________________________________________
    def setCameraInPosition(self, cam_id, rotation, position):
        cam_rotation = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation')

        cam_rotation.x += rotation.y
        cam_rotation.y += rotation.x
        cam_rotation.z += rotation.z
    
        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','position', position)
        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation', cam_rotation)

        return position, cam_rotation

    #_______________________________________________________________
    def setActiveLightInPosition(self, light_id, position, rotation):
        light_rotation = self._workspace.get_entity_property_value(light_id, 'RelativeTransformToComponent','rotation')

        light_rotation.x += rotation.x
        light_rotation.y += rotation.y
        light_rotation.z += -rotation.z
    
        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', position)
        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','rotation', light_rotation)

        return position, light_rotation

    #_______________________________________________________________
    def setEgoVibration(self, pos_intervals, rot_intervals, normal = True):
        center = 0
        x, y, z = 0, 1 ,2
        ego_id = self._ego_id
        ego_position = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','position')
        ego_rotation = self._workspace.get_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation')

        left_right_delta = self.getDelta(center, pos_intervals[y], normal)    # pos.y
        up_down_delta = self.getDelta(center, pos_intervals[z], normal)       # pos.z
        front_back_delta = self.getDelta(center, pos_intervals[x], normal)    # pos.x
        pos_delta = (front_back_delta, left_right_delta, up_down_delta)
        roll_delta = self.getDelta(center, rot_intervals[x], normal)  # rot.x
        pitch_delta = self.getDelta(center, rot_intervals[y], normal) # rot.y
        yaw_delta = self.getDelta(center, rot_intervals[z], normal)   # rot.z
        rot_delta = (roll_delta, pitch_delta, yaw_delta)

        ego_position.x += front_back_delta / 100
        ego_position.y += left_right_delta / 100
        ego_position.z += up_down_delta / 100
        ego_rotation.x += roll_delta
        ego_rotation.y += pitch_delta
        ego_rotation.z += yaw_delta

        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','position', ego_position)
        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation', ego_rotation)

        pos_delta_info = {'x': front_back_delta / 100, 'y': left_right_delta / 100, 'z': up_down_delta / 100}
        rot_delta_info = {'x': roll_delta, 'y': pitch_delta, 'z': yaw_delta}
        self.setCustomMetadata(ego_id, 'pos-delta', pos_delta_info)
        self.setCustomMetadata(ego_id, 'rot-delta', rot_delta_info)
        return ego_position, ego_rotation, pos_delta, rot_delta

    #_______________________________________________________________
    def setCameraVibration(self, cam_id, pos_intervals, rot_intervals, normal = True):
        center = 0
        x, y, z = 0, 1 ,2

        cam_position = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','position')
        cam_rotation = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation')

        left_right_delta = self.getDelta(center, pos_intervals[y], normal)    # pos.y
        up_down_delta = self.getDelta(center, pos_intervals[z], normal)       # pos.z
        front_back_delta = self.getDelta(center, pos_intervals[x], normal)    # pos.x
        pos_delta = (front_back_delta, left_right_delta, up_down_delta)
        roll_delta = self.getDelta(center, rot_intervals[x], normal)  # rot.x
        pitch_delta = self.getDelta(center, rot_intervals[y], normal) # rot.y
        yaw_delta = self.getDelta(center, rot_intervals[z], normal)   # rot.z
        rot_delta = (roll_delta, pitch_delta, yaw_delta)

        cam_position.x += front_back_delta / 100
        cam_position.y += left_right_delta / 100
        cam_position.z += up_down_delta / 100
        cam_rotation.x += roll_delta
        cam_rotation.y += pitch_delta
        cam_rotation.z += yaw_delta

        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','position', cam_position)
        self._workspace.set_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation', cam_rotation)

        return cam_position, cam_rotation, pos_delta, rot_delta

    #_______________________________________________________________
    def setCameraVisibility(self, cam_name):
        cam_ids = self._workspace.get_camera_entities()

        visible_cam_id = None
        visible_cam_name = None
        for  cam_id in cam_ids:
            if cam_name in self._workspace.get_entity_name(cam_id):
                self._workspace.set_entity_property_value(cam_id, 'VisibleComponent','visible', True)
                visible_cam_id = cam_id
                visible_cam_name = self._workspace.get_entity_name(visible_cam_id)
            else:
                self._workspace.set_entity_property_value(cam_id, 'VisibleComponent','visible', False)

        return visible_cam_id, visible_cam_name

    #_______________________________________________________________
    def getVisibleCameras(self):
        cam_ids = self._workspace.get_camera_entities()

        visible_cam_names = []
        for  cam_id in cam_ids:
            visibility = self._workspace.get_entity_property_value(cam_id, 'VisibleComponent','visible')
            if visibility:
                visible_cam_name = self._workspace.get_entity_name(cam_id)
                visible_cam_names.append(visible_cam_name)

        return visible_cam_names

    #_______________________________________________________________
    def reduceCameraResolution(self,cam_id, factor):
        sensor_id = self._workspace.get_entity_property_value(cam_id, 'CameraReferencesComponent','sensor')
        width = self._workspace.get_entity_property_value(sensor_id, 'SensorContentComponent','size.width_resolution')
        height = self._workspace.get_entity_property_value(sensor_id, 'SensorContentComponent','size.height_resolution')
        self._workspace.set_entity_property_value(sensor_id, 'SensorContentComponent','size.width_resolution', width/factor)
        self._workspace.set_entity_property_value(sensor_id, 'SensorContentComponent','size.height_resolution', height/factor)

        lens_id = self._workspace.get_entity_property_value(cam_id, 'CameraReferencesComponent','camera_lens')
        focal_length = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.focal_length')
        self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.focal_length', focal_length/factor)

        lens_type = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.lens_type')
        if 'OPENCV' in lens_type:
            cx = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cx')
            cy = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cy')
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cx', cx/factor)
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cy', cy/factor)

            fx = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fx')
            fy = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fy')
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fx', fx/factor)
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fy', fy/factor)

    #_______________________________________________________________
    def reduceAllCameraResolution(self, factor):
        cameras = self._workspace.get_camera_entities()
        for cam in cameras:
            self.reduceCameraResolution(cam, factor)

    #_______________________________________________________________
    def increaseCameraResolution(self,cam_id, factor):
        sensor_id = self._workspace.get_entity_property_value(cam_id, 'CameraReferencesComponent','sensor')
        width = self._workspace.get_entity_property_value(sensor_id, 'SensorContentComponent','size.width_resolution')
        height = self._workspace.get_entity_property_value(sensor_id, 'SensorContentComponent','size.height_resolution')
        self._workspace.set_entity_property_value(sensor_id, 'SensorContentComponent','size.width_resolution', width*factor)
        self._workspace.set_entity_property_value(sensor_id, 'SensorContentComponent','size.height_resolution', height*factor)

        lens_id = self._workspace.get_entity_property_value(cam_id, 'CameraReferencesComponent','camera_lens')
        focal_length = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.focal_length')
        self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.focal_length', focal_length*factor)

        lens_type = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','properties.lens_type')
        if 'OPENCV' in lens_type:
            cx = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cx')
            cy = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cy')
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cx', cx*factor)
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-cy', cy*factor)

            fx = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fx')
            fy = self._workspace.get_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fy')
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fx', fx*factor)
            self._workspace.set_entity_property_value(lens_id, 'CameraLensPropertiesComponent','intrinsics.camera-intrinsics-fy', fy*factor)
    #_______________________________________________________________
    def increaseAllCameraResolution(self, factor):
        cameras = self._workspace.get_camera_entities()
        for cam in cameras:
            self.increaseCameraResolution(cam, factor)

    #_______________________________________________________________
    def queryResultToDic(self, queryResult, workspaceEntityType = anyverse_platform.WorkspaceEntityType.Asset):
        result = []
        total = len(queryResult)
        print('[INFO] {} assets'.format(total))
        processed = 0
        for elem in queryResult:
            attributes_string = self._resources.get_resource_attributes(workspaceEntityType, elem)

            attrs = json.loads(attributes_string)
            dic = {}
            for attr_name in attrs.keys():
                dic[attr_name.lower()] = attrs[attr_name]['value']

            dic["resource_id"] = elem
            dic["resource_name"] = dic['name']
            if dic['name'] not in self._excluded_objects:
                result.append(dic)
            processed += 1
            # self.update_progress(processed/total)

        return result

    #_______________________________________________________________
    def queryCars(self, dynamic_material = False):
        query = aux.ResourceQueryManager(self._workspace)
        # query.add_tag_filter("compound")
        # query.add_tag_filter("car-interior")
        # query.add_exists_attribute_filter('brand')
        # query.add_exists_attribute_filter('model')
        # query.add_exists_attribute_filter('version')
        query.add_attribute_filter('category', 'vehicle_cabin')
        query.add_attribute_filter('adjustable_seats', True)
        query.add_attribute_filter('detailed_interior', True)


        query.add_attribute_filter('dynamic_material', dynamic_material)

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryCharacters(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_tag_filter("character")
        query.add_attribute_filter('texture', '8k')
        query.add_exists_attribute_filter('root_offset')
        query.add_exists_attribute_filter('kind')
        query.add_exists_attribute_filter('agegroup')
        query.add_exists_attribute_filter('ethnicity')
        query.add_exists_attribute_filter('gender')
        query.add_exists_attribute_filter('height')

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryBabies(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_tag_filter("person")
        query.add_attribute_filter("kind", "Baby")

        return self.queryResultToDic(query.execute_query_on_assets())
        

    #_______________________________________________________________
    def queryChildSeats(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_exists_attribute_filter('kind')
        query.add_attribute_filter("class", "ChildSeat")
        query.add_attribute_filter("dynamic_material", True)

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryChildSeatBelts(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_exists_attribute_filter('kind')
        query.add_attribute_filter("class", "seat_belt")

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryObjects(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("in_cabin_compliant", True)

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryAccessories(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("category", "Human Accessories")
        query.add_attribute_filter_from_list("class", [ "Hat", "Facemask", "Baseball_cap", "Sunglasses", "Glasses" ])

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryCarBeltClip(self, brand, model):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("brand", brand)
        query.add_attribute_filter("model", model)
        query.add_attribute_filter("type", "ClipBelt")

        result = self.queryResultToDic(query.execute_query_on_assets())

        clip = None
        if len(result) >= 1:
            clip = result[0]
            # print('[INFO] Found clip for ' + brand)

        return clip

    #_______________________________________________________________
    def queryCarBeltsOff(self, picked_car):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("brand", picked_car['brand'])
        query.add_attribute_filter("model", picked_car['model'])
        query.add_attribute_filter("type", "Belt")

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryCarSeats(self, picked_car, dynamic_material = False):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("brand", picked_car['brand'])
        query.add_attribute_filter("model", picked_car['model'])
        query.add_attribute_filter("type", "Seat")

        query.add_attribute_filter('dynamic_material', dynamic_material)

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryBackgrounds(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_exists_attribute_filter('IBL_intensity')
        query.add_attribute_filter("environment", 'Exterior')

        return self.queryResultToDic(query.execute_query_on_backgrounds(), anyverse_platform.WorkspaceEntityType.Background)

    #_______________________________________________________________
    def queryMaterials(self, color_scheme = False):
        query_color_scheme = aux.ResourceQueryManager(self._workspace)
        query_color_scheme.add_exists_attribute_filter('compatibility')
        if color_scheme:
            query_color_scheme.add_exists_attribute_filter('color_scheme')
        color_scheme_materials = self.queryResultToDic(query_color_scheme.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

        query_family = aux.ResourceQueryManager(self._workspace)
        query_family.add_exists_attribute_filter('compatibility')
        query_family.add_attribute_filter('family', 'textile')
        textile_materials = self.queryResultToDic(query_family.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

        color_scheme_materials_set = {frozenset(d.items()) for d in color_scheme_materials}
        textile_materials_set = {frozenset(d.items()) for d in textile_materials}
        union_set = color_scheme_materials_set.union(textile_materials_set)
        return [dict(s) for s in union_set]

    #_______________________________________________________________
    def queryCompatibleMaterials(self, compatibility, color_scheme = None):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter('compatibility', compatibility)

        if color_scheme:
            query.add_attribute_filter('color_scheme', color_scheme)

        return self.queryResultToDic(query.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

    #_______________________________________________________________
    def queryPupilMaterial(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter('family', 'organic')

        return self.queryResultToDic(query.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

    #_______________________________________________________________
    def getBrightPupilMaterial(self):
        pupil_material_id = anyverse_platform.invalid_entity_id
        pupil_materials = self.queryPupilMaterial()
        if len(pupil_materials) > 0:
            pupil_material_id = pupil_materials[0]['entity_id']
        else:
            print('[WARN] Could NOT find bright pupil material')

        return pupil_material_id

    #_______________________________________________________________
    def setBrightPupil(self):
        light_ids = self._workspace.get_entities_by_type('Light')
        light_on = False
        for light_id in light_ids:
            if self._workspace.get_entity_property_value(light_id, 'VisibleComponent','visible'):
                light_on = True
                break
        return False # TODO: Not setting bright pupil yet. Define the conditions beyond active light on.
        return light_on and not self.isDay()
    
    #_______________________________________________________________
    def setBrightIris(self, seat_locator):
        return False # TODO: Not setting bright iris yet. Define the conditions beyond active light on.
        return self.setBrightPupil() and (self.isDriverSeat(seat_locator) or self.isCopilotSeat(seat_locator))
    
    #_______________________________________________________________
    def queryBeltMaterials(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter('compatibility', 'seatbelt')

        return self.queryResultToDic(query.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

    #_______________________________________________________________
    def getRandomBeltMaterial(self):
        belt_materials = self.queryBeltMaterials()
        idx = random.randrange(len(belt_materials))
        return belt_materials[idx]

    #_______________________________________________________________
    def getAssetExposedMaterials(self, fixed_id):
        exposed_materials = [ m for m in self._workspace.get_hierarchy(fixed_id) if 'MaterialPartEntity' == self._workspace.get_entity_type(m) ]

        return exposed_materials
    
    #_______________________________________________________________
    def changeMaterial(self, fixed_id, material_name_pattern, new_material):
        ok = False
        # Make sure we change the material that belongs to the fixed_id in case there are more exposed materials in the hierarchy matching the pattern or name
        matched_materials = [ m for m in self.getAssetExposedMaterials(fixed_id) if re.search(material_name_pattern, self._workspace.get_entity_name(m)) and self.getParent(self.getParent(m)) == fixed_id ]
        if len(matched_materials) > 0:
            material = matched_materials[0]
            self._workspace.set_entity_property_value(material, 'MaterialOverrideInfoComponent','material_entity_id', new_material)
            ok = True
        else:
            print('[WARN] Could NOT find material matching {} in fixed entity {}'.format(material_name_pattern, self._workspace.get_entity_name(fixed_id)))
        
        return ok
    
    #_______________________________________________________________
    def changeExposedMaterials(self, fixed_id, asset_set, color_scheme = None):
        # Get the asset that correspond to the fixed entity that expose the materials
        asset_id = self._workspace.get_entity_property_value(fixed_id, 'AssetEntityReferenceComponent','asset_entity_id')
        if type(asset_set) is list: 
            asset = [ a for a in asset_set if a['entity_id'] == asset_id ]
            if len(asset) == 0:
                return
            asset = asset[0]
        else: 
            asset = asset_set

        if color_scheme is None:
            materials_list = anyverse_platform.materials
        else:
            materials_list = [ m for m in anyverse_platform.materials if 'color_scheme' in m ]
            # print('[INFO] Scheme {} materials: {}'.format(color_scheme, materials_list))

        # Get Fixed entity exposed materials
        exposed_materials = self.getAssetExposedMaterials(fixed_id)
        for material in exposed_materials:
            material_name = self._workspace.get_entity_name(material)
            # Get compatible materials from asset
            if material_name in asset:
                compatibility = asset[material_name]
                compatible_materials = [ cm for cm in materials_list if compatibility == cm['compatibility'] and cm['color_scheme'] == color_scheme ] if color_scheme else [ cm for cm in materials_list if compatibility == cm['compatibility'] ]
                if len(compatible_materials) == 0:
                    print('[WARN] No compatible materials found for exposed material {} Trying in the DB...'.format(material_name))
                    compatible_materials = [ cm for cm in self.queryCompatibleMaterials(compatibility, color_scheme) ]
                if len(compatible_materials) !=0:
                    selected_material = compatible_materials[random.randrange(len(compatible_materials))]
                    selected_material['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Material, selected_material['resource_id'])
                    # Take into account an equal probability to use the default material
                    self._workspace.set_entity_property_value(material, 'MaterialOverrideInfoComponent','material_entity_id', selected_material['entity_id'])
                    # print('[INFO] Changing material {} to {}'.format(material_name, self._workspace.get_entity_name(selected_material)))
                else:
                    # print('[WARN] No compatible materials found for exposed material {}'.format(material_name))
                    continue

            else:
                print('[ERROR] Cannot change material: No {} attribute in asset {}'.format(material_name, asset['resource_name']))

    #_______________________________________________________________
    def changeExposedMaterialsList(self, fixed_ids_list, asset_set, color_scheme = None):
        cached_materials = {}
        for fixed_id in fixed_ids_list:
            if fixed_id == anyverse_platform.invalid_entity_id:
                continue
            
            print('[INFO] Changing materials for {}'.format(self._workspace.get_entity_name(fixed_id)))
            # Get the asset that correspond to the fixed entity that expose the materials
            asset_id = self._workspace.get_entity_property_value(fixed_id, 'AssetEntityReferenceComponent','asset_entity_id')
            if type(asset_set) is list: 
                asset = [ a for a in asset_set if a['entity_id'] == asset_id ][0]
            else: 
                asset = asset_set

            if color_scheme is None:
                materials_list = anyverse_platform.materials
            else:
                materials_list = [ m for m in anyverse_platform.materials if 'color_scheme' in m ]
                # print('[INFO] Scheme {} materials: {}'.format(color_scheme, materials_list))

            # Get Fixed entity exposed materials
            exposed_materials = self.getAssetExposedMaterials(fixed_id)
            for material in exposed_materials:
                material_name = self._workspace.get_entity_name(material)
                # Get compatible materials from asset
                if material_name in asset:
                    compatibility = asset[material_name]
                    compatible_materials = [ cm for cm in materials_list if compatibility == cm['compatibility'] and cm['color_scheme'] == color_scheme ] if color_scheme else [ cm for cm in materials_list if compatibility == cm['compatibility'] ]
                    if len(compatible_materials) != 0:
                        if material_name in cached_materials:
                            selected_material = cached_materials[material_name]
                        else:
                            selected_material = compatible_materials[random.randrange(len(compatible_materials))]
                            cached_materials[material_name] = selected_material
                        selected_material['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Material, selected_material['resource_id'])
                        # Take into account an equal probability to use the default material
                        self._workspace.set_entity_property_value(material, 'MaterialOverrideInfoComponent','material_entity_id', selected_material['entity_id'])
                        # print('[INFO] Changing material {} to {}'.format(material_name, self._workspace.get_entity_name(selected_material)))
                    else:
                        # print('[WARN] No compatible materials found for exposed material {}'.format(material_name))
                        continue
                else:
                    print('[ERROR] Cannot change material: No {} attribute in asset {}'.format(material_name, asset['resource_name']))

    #_______________________________________________________________
    def filterCharacters(self, characters, key, value, check_twins = True):
        filtered_characters = [c for c in characters if key.lower() in c and c[key.lower()] == value]

        elegible_chars = filtered_characters.copy()
        # Discard the characters already used
        for character in filtered_characters:
            if check_twins and character['model'] in self._already_used_characters:
                # print('[WARN]: Character {} used. Removing from elegible...'.format(character['resource_name']))
                elegible_chars.remove(character)
        return elegible_chars

    #_______________________________________________________________
    def filterObjects(self, objects, key, values):
        if type(values) is list:
            filtered_objects = [ o for o in objects if o[key.lower()].lower() in [ x.lower() for x in values]]
        else:
            filtered_objects = [ o for o in objects if o[key.lower()].lower() in  values ]
        return filtered_objects

    #_______________________________________________________________
    def choiceUsingProbabilities(self, probabilities):
        '''
        Given a list of probabilities return the index of the list selected. For instance,
        given the list [0.1, 0.3, 0.6], we are indicating that the first element of the list
        will be chosen with a probability of 10%, etc. The summatory of all probabilities
        doesn't have to be 1.0 but it is recommended to uderstand better the distribution.
        '''
        totalProbability = sum(probabilities)

        randomValue = random.uniform(0.0, totalProbability)
        accumProbability = 0.0
        for idx, probability in enumerate(probabilities):
            if randomValue < probability + accumProbability:
                return idx
            accumProbability += probability
        assert False
        return -1

    #_______________________________________________________________
    def isAssetAlreadyCreated(self, name):
        return self.isEntityAlreadyCreated(name, anyverse_platform.WorkspaceEntityType.Asset)

    #_______________________________________________________________
    def isBackgroundAlreadyCreated(self, name):
        return self.isEntityAlreadyCreated(name, anyverse_platform.WorkspaceEntityType.Background)

    #_______________________________________________________________
    def isEntityAlreadyCreated(self, name, entity_type):
        entities = self._workspace.get_entities_by_type(entity_type)
        for entity in entities:
            if self._workspace.get_entity_name(entity) == name:
                return True

        return False

    #_______________________________________________________________
    def getConvertibleClipAsset(self, name, assetList):
        for item in assetList:
            if item.name == name :
                return item

        return None

#_______________________________________________________________
    def getAssetsByName(self, name, assetList):
        for item in assetList:
            if (name == item.name) :
                return item

#_______________________________________________________________
    def getAssetsByTag(self, tag, assetList):
        result = []
        for item in assetList:
            if (tag in item.tags) :
                result.append(item)

        return result

    #_______________________________________________________________
    def getBabyAssets(self):
        person_assets = self.getAssetsByTag('person', self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset))
        babies = [ b for b in person_assets if 'Baby' in b.name ]
        return babies

    #_______________________________________________________________
    def setDayIntensities(self, sky, sun, simulation_id):
        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sky_light_intensity', sky)
        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sun_light_intensity', sun)

    #_______________________________________________________________
    def setNightIntensities(self, backg, ibl, simulation_id):
        background_id = self._workspace.get_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','fixed_background')
        self._workspace.set_entity_property_value(background_id, 'BackgroundContentComponent','environment_weight', backg)
        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','iblLightIntensity', ibl)

    #_______________________________________________________________
    def setAnalogGain(self, camera_id, analog_gain):
        sensor_id = self._workspace.get_entity_property_value(camera_id, 'CameraReferencesComponent','sensor')
        self._workspace.set_entity_property_value(sensor_id, 'SensorContentComponent','misc.analogGain', analog_gain)

    #_______________________________________________________________
    def setIllumination(self, day, background, simulation_id, multiple_cameras = False, active_light = False):

        incabin_light = None
        incabin_lights = self._workspace.get_entities_by_type('Light')
        if multiple_cameras:
            for incabin_light in incabin_lights:
                if active_light and incabin_light != None:
                    print('[INFO] Active light {} ({}) turned on'.format(self._workspace.get_entity_name(incabin_light), incabin_light))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', True)
                elif incabin_light == None:
                    print('[WARN] Active light set to True, but no active light defined in the workspace')
                else:
                    print('[INFO] Active light {} turned off'.format(self._workspace.get_entity_name(incabin_light)))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', False)
        elif len(incabin_lights) > 0: # No multiple cameras, turn on all the lights we find
            # incabin_light = incabin_lights[0]
            for incabin_light in incabin_lights:
                if active_light:
                    print('[INFO] Active light {} ({}) turned on'.format(self._workspace.get_entity_name(incabin_light), incabin_light))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', True)
                else:
                    print('[INFO] Active light {} turned off'.format(self._workspace.get_entity_name(incabin_light)))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', False)
        elif active_light:
            print('[WARN] Active light set to True, but no active light defined in the workspace')

        self.setCustomMetadata(simulation_id, 'day', day)
        self.setCustomMetadata(simulation_id, 'interior_lights', active_light)

        if day:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','ilumination_type', 'PhysicalSky')
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','surrounding_type', 'Background')
            sky_light_intensity = 1
            sun_light_intensity = 1

            # set default values
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sky_light_intensity', sky_light_intensity)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sun_light_intensity', sun_light_intensity)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','scatteringIntensity', 300)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','diffractionIntensity', 0)

            return sun_light_intensity
        else:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','ilumination_type', 'Background')
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','surrounding_type', 'Background')
            ibl_light_intensity = background['ibl_intensity']
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','iblLightIntensity', ibl_light_intensity)

            background_weight = 1
            if background != None:
                self._workspace.set_entity_property_value(background['entity_id'], 'BackgroundContentComponent','environment_weight', background_weight)
            return ibl_light_intensity

    #_______________________________________________________________
    def setSensor(self, cam_id, sensor_name):
        if sensor_name is None:
            sensor = anyverse_platform.invalid_entity_id
        else:
            sensors = [ s for s in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Sensor) if sensor_name == self._workspace.get_entity_name(s) ]
            if len(sensors) > 0:
                sensor = sensors[0]
            else:
                sensor = anyverse_platform.invalid_entity_id
                print('[WARN] Cannot find sensor {}, setting the camera to No Sensor'.format(sensor_name))

        self._workspace.set_entity_property_value(cam_id, 'CameraReferencesComponent','sensor', sensor)

    #_______________________________________________________________
    def setIsp(self, cam_id, isp_name):
        if isp_name is None:
            isp = anyverse_platform.invalid_entity_id
        else:
            isps = [ i for i in self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.ISP) if isp_name == self._workspace.get_entity_name(i) ]
            if len(isps) > 0:
                isp = isps[0]
            else:
                isp = anyverse_platform.invalid_entity_id
                print('[WARN] Cannot find ISP {}, setting the camera to No Sensor'.format(isp_name))
                
        self._workspace.set_entity_property_value(cam_id, 'CameraReferencesComponent','isp', isp)

    #_______________________________________________________________
    def setGroundRotation(self, gr, simulation_id):
        sim_rotation = self._workspace.get_entity_property_value(simulation_id, 'RelativeTransformToComponent','rotation')
        sim_rotation.z = gr
        self._workspace.set_entity_property_value(simulation_id, 'RelativeTransformToComponent','rotation', sim_rotation)

    #_______________________________________________________________
    def genTimeOfday(self, day, dawn):
        if day and dawn:
            time_of_day = random.uniform(6.233, 6.30)
        elif day and not dawn:
            time_of_day = random.uniform(6.31, 18)
        elif not day:
            time_of_day_1 = (random.uniform(18, 23.99), random.uniform(0, 6.23))
            time_of_day = time_of_day_1[random.randint(0,1)]
        return time_of_day

    #_______________________________________________________________
    def genSunDirection(self, day, dawn, min_elevation = 7): # min is 7 for Continental
        elevation = 0
        azimuth = 0
        sun_direction = anyverse_platform.Vector3D(0,0,0)
        if day and dawn:
            azimuth = random.uniform(0, 360)
            elevation = random.uniform(1, 10)
        elif day and not dawn:
            azimuth = random.uniform(0, 360)
            elevation = random.uniform(min_elevation, 90)
        elif not day:
            azimuth = 0
            elevation = -10

        sun_direction.x = math.sin(math.radians(azimuth))
        sun_direction.y = math.cos(math.radians(azimuth))
        sun_direction.z = math.sin(math.radians(elevation))

        return sun_direction, elevation, azimuth

    #_______________________________________________________________
    def setGroundRotationSunDirection(self, day, simulation_id, dawn = False, ground_rotation = None, sun_direction = None):
        if sun_direction is None:
            sun_direction, elevation, azimuth = self.genSunDirection(day, dawn)
        if ground_rotation is None:
            ground_rotation = random.uniform(0,360)

        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sky.sunDirection', sun_direction)
        # self.setGroundRotation(ground_rotation, simulation_id)
        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','background_offset', ground_rotation)

        self.setCustomMetadata(simulation_id, 'ground-rotation', ground_rotation)
        self.setCustomMetadata(simulation_id, 'sun-elevation', elevation)
        self.setCustomMetadata(simulation_id, 'sun-azimuth', azimuth)

        return elevation, azimuth, ground_rotation

    #_______________________________________________________________
    def setBackground(self, background, simulation_id, dawn = False):
        if not dawn:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','fixed_background',background['entity_id'])
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','iblLightIntensity', background['ibl_intensity'])
        else:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','fixed_background',self._no_entry)

        # Dump the background info in the simulation custom metadata
        bkg_info = {}
        bkg_info['background'] = background['name']
        bkg_info['day'] = background['day']
        bkg_info['IBL_intensity'] = background['ibl_intensity']
        bkg_info['environment'] = background['environment']
        bkg_info['sky_type'] = background['sky_type']
        bkg_info['env-weight'] = self._workspace.get_entity_property_value(background['entity_id'], 'BackgroundContentComponent','environment_weight')

        self.setCustomMetadata(simulation_id, "backgroundInfo", bkg_info)

    #_______________________________________________________________
    def selectBackground(self, day, bg_list = None, bg_name = None):
        if bg_list == None:
            if day :
                backgrounds = [ b for b in self._workspace.backgrounds if b['day'] ]
            else:
                backgrounds = [ b for b in self._workspace.backgrounds if not b['day'] ]
        else:
            backgrounds = bg_list

        if bg_name:
            for idx, background in enumerate(backgrounds):
                if bg_name == background['name']:
                    selected_background = backgrounds[idx]
                    break
        else:
            selected_background_idx = random.randrange(0,len(backgrounds))
            selected_background = backgrounds[selected_background_idx]


        selected_background['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Background, selected_background['resource_id'])
        ws_bckgnd_id = selected_background['entity_id']

        return selected_background, ws_bckgnd_id

    #_______________________________________________________________
    def selectCar(self, use_probs = False, car_idx = None):
        if use_probs:
            probabilities = [ c['probability'] for c in use_probs ]
            idx = self.choiceUsingProbabilities(probabilities)
            car_name = use_probs[idx]['car_name']
            elegible_cars = [ i for i, c in enumerate(self._workspace.cars) if c['brand'].replace(" ", "") in car_name ]
            idx = elegible_cars[random.randrange(len(elegible_cars))]
        else:
            idx = random.randrange(len(self._workspace.cars))

        if car_idx is not None:
            idx = car_idx
        picked_car = self._workspace.cars[idx]
        entity_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_car['resource_id'])
        picked_car['entity_id'] = entity_id
        self._car_brand = picked_car['brand']
        self._car_model = picked_car['model']
        return picked_car

    #_______________________________________________________________
    def buildCar(self, picked_car, the_car, dynamic_materials = False, move_seats_conf = None, change_belt_material = False):
        self._workspace.set_entity_property_value(the_car, 'AssetEntityReferenceComponent','asset_entity_id', picked_car['entity_id'])
        print('[INFO] Using car: {}_{}_{}'.format(picked_car['brand'], picked_car['model'], picked_car['version']))

        # Change car interior materials following a color scheme
        color_scheme = self._car_color_schemes[random.randrange(len(self._car_color_schemes))]
        print('[INFO] Color scheme: {}'.format(color_scheme))
        
        if dynamic_materials:
            print('[INFO] Changing materials for {}_{}'.format(picked_car['brand'], picked_car['model']))
            self.changeExposedMaterials(the_car, picked_car, color_scheme = color_scheme)

        print('[INFO] Change belt material: {}'.format(change_belt_material))
        self.setCarSeatbeltsOff(picked_car, change_belt_material)
        self.setSeats(picked_car, the_car, dynamic_materials, color_scheme, move_seats_conf)

    #_______________________________________________________________
    def setSeat(self, the_car, seats, seat_locators, seat_num, move_seat_conf = None):
        locator = next( (x for x in seat_locators if seat_num in self._workspace.get_entity_name(x).lower()), None )
        if locator != None:
            # There is a specific locator por this seat
            seat = next((x for x in seats if seat_num in x["resource_name"].lower()), None)
            if seat != None:
                seat['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, seat['resource_id'])
                seat_id = self._workspace.create_fixed_entity(seat["resource_name"], locator, seat['entity_id'])
                # self.setSplitAction(seat_id, 'Split') # If the assets does not have the the 'compound' tag
            else:
                print("[ERROR] Locator {} exists but not its seat".format(self._workspace.get_entity_name(locator)) )
                assert False
                seat_id = anyverse_platform.invalid_entity_id
        else:
            # There is not a specific locator por this seat. Create it under the car directly
            seat = next((x for x in seats if seat_num in x["resource_name"].lower()), None)
            if seat != None:
                seat['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, seat['resource_id'])
                seat_id = self._workspace.create_fixed_entity(seat["resource_name"], the_car, seat['entity_id'])
            else:
                print("[INFO] Locator exists neither seat for position {}".format(seat_num) )
                seat_id = anyverse_platform.invalid_entity_id

        # If change seat position True get a random depth and tilt to apply only to front seats
        depth = 0
        tilt = 0
        if move_seat_conf and move_seat_conf['move_seats'] and seat_id != anyverse_platform.invalid_entity_id:
            normal = move_seat_conf['normal_dist']
            max_depth = move_seat_conf['max_depth']
            max_tilt = move_seat_conf['max_tilt']
            if isinstance(normal, bool):
                depth = self.getDelta(0, max_depth, normal)
                tilt = self.getDelta(0, max_tilt, normal)
            elif isinstance(normal, list):
                depth = normal[0] if isinstance(normal[0], float) else 0
                tilt = normal[1] if isinstance(normal[1], float) else 0
            else:
                depth = 0
                tilt = 0
            seat_pos = self._workspace.get_entity_property_value(seat_id,'RelativeTransformToComponent','position')
            seat_rot = self._workspace.get_entity_property_value(seat_id,'RelativeTransformToComponent','rotation')
            seat_pos.x += depth
            seat_rot.y += tilt
            seat_pos = self._workspace.set_entity_property_value(seat_id,'RelativeTransformToComponent','position', seat_pos)
            seat_rot = self._workspace.set_entity_property_value(seat_id,'RelativeTransformToComponent','rotation', seat_rot)

        self.setAdjustableSeatInfo(seat_id, depth, tilt)

        seat_info = {}
        seat_info['number'] = seat_num
        self.setCustomMetadata(seat_id, "Seat", seat_info)

        self.setExportAlwaysExcludeOcclusion(seat_id)

        return seat_id

    #_______________________________________________________________
    def setSeats(self, picked_car, the_car, dynamic_materials = False, color_scheme = None, move_seats_conf = None):
        if (not 'adjustable_seats' in picked_car) or (not picked_car['adjustable_seats'] ):
            return

        # Check if the car is a seven seater
        seven_seater = False
        seat_locators = self._workspace.get_entities_by_name_including('adjustableSeat')
        if len(seat_locators) > 5:
            seven_seater = True

        # Get seats from DDBB and get only the conventional ones for a seven seater
        seats = self.queryCarSeats(picked_car, dynamic_material = True)
        if seven_seater:
            seat_locators = [ sl for sl in seat_locators if 'conventional' in self._workspace.get_entity_name(sl) ]
            seats  = [ s for s in seats if 'conventional' in s['resource_name'] ]

        seat_ids_list = []  
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat01", move_seats_conf))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat02", move_seats_conf))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat03"))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat04"))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat05"))
        if seven_seater:
            seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat06"))
            seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat07"))
        
        if dynamic_materials:
            self.changeExposedMaterialsList(seat_ids_list, seats, color_scheme)
        
    #_______________________________________________________________
    def setCarSeatbeltsOff(self, picked_car, change_belt_material = False):
        belt_locator = self._workspace.get_entities_by_name('belt_locator')[0]
        self.deleteChildren(belt_locator)
        belts = self.queryCarBeltsOff(picked_car)
        if change_belt_material:
            belt_material = self.getRandomBeltMaterial()
            print('[INFO] Using material {} for belts'.format(belt_material['name']))
            self._belt_material_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Material, belt_material['resource_id'])

        for belt in belts:
            belt['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, belt['resource_id'])
            beltoff_id = self._workspace.create_fixed_entity(belt['resource_name'], belt_locator, belt['entity_id'])
            if change_belt_material:
                self.changeMaterial(beltoff_id, 'belt', self._belt_material_id)
            self.setExportAlwaysExcludeOcclusion(beltoff_id)
            belt_name = self._workspace.get_entity_name(beltoff_id)
            seat_info = {}
            seat_info['number'] = 'seat{}'.format(belt_name.split('_')[-2][-2:])
            # seat_info['number'] = 'seat{}'.format(belt_name[-2:])
            self.setCustomMetadata(beltoff_id, "Seat", seat_info)

    #_______________________________________________________________
    def setChildSeatSeatbeltOff(self, childseat):
        # Get the belt off asset for the specific child seat
        belts_off = [ b for b in anyverse_platform.childseatbelts if 'off' in b['version'].lower() and b['brand'].lower() == childseat['brand'].lower() and b['model'].lower() == childseat['model'].lower() and b['aim looking'].lower() == childseat['aim looking'].lower() ]

        if len(belts_off) == 1:
            belt_off = belts_off[0]
        else:
            print('[ERROR] No belt OFF found for child seat brand {} model {}'.format(childseat['brand'], childseat['model']))
            return False
        
        try:
            belt_off['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, belt_off['resource_id'])
            belt_off_id = self._workspace.create_fixed_entity( belt_off['name'], childseat['fixed_entity_id'], belt_off['entity_id'] )
        except RuntimeError as rte:
            # TODO: show warning message here
            return False       

        self._workspace.set_entity_property_value(belt_off_id, 'ExportConfigurationComponent', 'export_always', True)
        self._workspace.set_entity_property_value(belt_off_id, 'ExportConfigurationComponent', 'exclude_from_occlusion_tests', True)

        return True
    
    #_______________________________________________________________
    def createBeltFor(self, seat_pos, beltUserEntityId, car_brand, car_model, seatbelts_distribution ):
        print("[INFO] Setting belt on in position {}".format(seat_pos))
        seatId = str(seat_pos).zfill(2)
        clip = self.queryCarBeltClip(car_brand, car_model)
        if clip == None:
            print("[ERROR] Cannot find clip for brand " + car_brand)
            return None
        
        clip['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, clip['resource_id'])
        clip_asset = clip['entity_id']
        assert clip_asset != anyverse_platform.invalid_entity_id

        jointsToRemove = None  # For the moment just use the default: both arms

        belt_id, belt_placement = self.createBelt( beltUserEntityId, clip_asset, seatId, jointsToRemove, seatbelts_distribution )
        if belt_id == anyverse_platform.invalid_entity_id:
            return None
        
        belt_name = self._workspace.get_entity_name(belt_id)
        # print('[INFO] Placed belt name: {}'.format(belt_name))
        self._workspace.set_entity_name(belt_id, 'SeatBelt0{}_On'.format(seat_pos))
        # print('[INFO] New belt name: {}'.format(self._workspace.get_entity_name(belt_id)))
        # Set the user custom metadata with the belt placement and the 
        seat_info = {}
        seat_info['number'] = 'seat0{}'.format(seat_pos)
        self.setCustomMetadata(belt_id, "Seat", seat_info)

        return belt_placement

    #_______________________________________________________________
    def createBelt( self, beltUserEntityId, clipAsset, seatId="01", joints_to_remove=[], seatbelts_distribution = None ):
        clipLocatorName = "clipOn{}_locator".format( seatId )
        clipLocator = self._workspace.get_entities_by_name( clipLocatorName )
        if len(clipLocator) == 0:
            print( "[ERROR] Cannot find clip locator " + clipLocatorName )
            return anyverse_platform.invalid_entity_id, None

        clipLocator = clipLocator[0]
        clipName = "clipEntity" + seatId
        clipEntityId = self._workspace.create_fixed_entity( clipName, clipLocator, clipAsset )
        assert clipEntityId != anyverse_platform.invalid_entity_id
        anyverse_platform.entitiesToClear.append(clipEntityId)

        self._workspace.set_entity_property_value(clipEntityId, 'ExportConfigurationComponent', 'export_always', True)
        self._workspace.set_entity_property_value(clipEntityId, 'ExportConfigurationComponent', 'exclude_from_occlusion_tests', True)

        clipChildren = self._workspace.get_hierarchy( clipEntityId )

        for clipChild in clipChildren:
            childName = self._workspace.get_entity_name( clipChild )
            if childName.startswith( "beltA_step02" ):
                clip_beltA_step02 = clipChild
            elif childName.startswith( "beltB_step02" ):
                clip_beltB_step02 = clipChild
            elif childName.startswith( "beltA_step03" ):
                clip_beltA_step03 = clipChild
            elif childName.startswith( "beltB_step03" ):
                clip_beltB_step03 = clipChild

        seat_beltA_step01 = self._workspace.get_entities_by_name( "seat{}_beltA_step01_locator".format(seatId) )[0]
        seat_beltB_step01 = self._workspace.get_entities_by_name( "seat{}_beltB_step01_locator".format(seatId) )[0]

        seat_beltA_step04 = self._workspace.get_entities_by_name( "seat{}_beltA_step04_locator".format(seatId) )[0]
        seat_beltB_step04 = self._workspace.get_entities_by_name( "seat{}_beltB_step04_locator".format(seatId) )[0]

        assert seat_beltA_step01 != anyverse_platform.invalid_entity_id
        assert seat_beltB_step01 != anyverse_platform.invalid_entity_id
        assert seat_beltA_step04 != anyverse_platform.invalid_entity_id
        assert seat_beltB_step04 != anyverse_platform.invalid_entity_id

        beltId = -1

        args = [ beltUserEntityId,
                seat_beltA_step01, seat_beltB_step01,
                seat_beltA_step04, seat_beltB_step04,
                clip_beltA_step02, clip_beltB_step02,
                clip_beltA_step03, clip_beltB_step03 ]

        joints = city_builder.core.StringVector()
        if joints_to_remove:
            for joint in joints_to_remove:
                joints.append( joint )
            args.append( joints )
        else:
            args.append( joints )

        if seatbelts_distribution is None:
            beltType = 'Normal'
            beltPlacement = self._beltOptions[beltType]
        else:
            random_belt_material = seatbelts_distribution['random_belt_material']
            differentiate_segments = seatbelts_distribution['differentiate_segments']
            beltType = ""
            if beltUserEntityId == anyverse_platform.invalid_entity_id:
                beltPlacement = anyverse_platform.SeatBeltPlacement.WithoutCharacter
                beltType = 'WithoutCharacter'
            else:
                toList = [ (key, float(value)) for key, value in seatbelts_distribution['seatbelt_placement_probabilities'].items() ]
                idx = self.choiceUsingProbabilities([x[1] for x in toList])
                beltType = toList[idx][0]
                beltPlacement = self._beltOptions[beltType]
                # print('[INFO] beltPlacement: {}'.format(beltPlacement))
        args.append( beltPlacement )

        # The belt material has been set when placing the seatbelts off or it is invalid_entity_id by default
        args.append(self._belt_material_id)            

        print('[INFO] Differentiate belt segments: {}'.format(differentiate_segments))
        args.append(differentiate_segments)

        beltId = self._workspace.create_seat_belt( *args )
        anyverse_platform.entitiesToClear.append(beltId)

        self.setCustomMetadata(beltId, "Placement", beltType)
        self.removeOffBeltAt(seatId)

        return beltId, beltType

    #_______________________________________________________________
    def removeOffBeltAt(self, pos):
        try:
            belts_off_loc = self._workspace.get_entities_by_name( 'belt_locator')[0]
        except IndexError:
            print('[ERROR] No belt_locator found in car')
            return
        offs = [ bo for bo in self._workspace.get_hierarchy(belts_off_loc) if self._workspace.get_entity_type(bo) == str(anyverse_platform.WorkspaceEntityType.FixedEntity) ]
        for off in offs:
            if pos in self._workspace.get_entity_name(off):
                print('[INFO] Deleting off belt {}'.format(self._workspace.get_entity_name(off)))
                self._workspace.delete_entity(off)

    #_______________________________________________________________
    def createChildBelt( self, beltUserEntityId, seatEntityId, clipAsset, seat_pos, joints_to_remove=None ):
        config = anyverse_platform.ChildSeatBeltConfig()

        config.entity_id_using_belt = beltUserEntityId

        seatChildren = self._workspace.get_hierarchy( seatEntityId )

        for seatChild in seatChildren:
            childNameLower = self._workspace.get_entity_name( seatChild ).lower()

            if childNameLower.startswith( "belt01_a_step01_locator" ):
                config.first_up_right_locator_id = seatChild
            if childNameLower.startswith( "belt01_b_step01_locator" ):
                config.second_up_right_locator_id = seatChild

            if childNameLower.startswith( "belt02_a_step01_locator" ):
                config.first_up_left_locator_id = seatChild
            if childNameLower.startswith( "belt02_b_step01_locator" ):
                config.second_up_left_locator_id = seatChild

            if childNameLower.startswith( "belt01_a_step04_locator" ):
                config.first_down_right_locator_id = seatChild
            if childNameLower.startswith( "belt01_b_step04_locator" ):
                config.second_down_right_locator_id = seatChild

            if childNameLower.startswith( "belt02_a_step04_locator" ):
                config.first_down_left_locator_id = seatChild
            if childNameLower.startswith( "belt02_b_step04_locator" ):
                config.second_down_left_locator_id = seatChild

            if childNameLower.startswith( "belt03_a_step02_locator" ):
                config.first_central_locator_id = seatChild
            if childNameLower.startswith( "belt03_b_step02_locator" ):
                config.second_central_locator_id = seatChild

        seatId = str(seat_pos).zfill(2)
        clipName = "clipEntity" + seatId
        clipEntityId = self._workspace.create_fixed_entity( clipName, beltUserEntityId, clipAsset )
        anyverse_platform.iteration_entities.append( clipEntityId )  # To be removed later

        config.clip_entity_id = clipEntityId

        self._workspace.set_entity_property_value( clipEntityId, 'ExportConfigurationComponent', 'export_always', True)
        self._workspace.set_entity_property_value( clipEntityId, 'ExportConfigurationComponent', 'exclude_from_occlusion_tests', True)

        clipChildren = self._workspace.get_hierarchy( clipEntityId )

        # belt01 - Right
        # belt02 - Left
        # belt03 - Central

        for clipChild in clipChildren:
            childNameLower = self._workspace.get_entity_name( clipChild ).lower()

            if childNameLower.startswith( "belt01_a_step02_locator" ):  # front locators
                config.clip_first_up_right_locator_id = clipChild
            if childNameLower.startswith( "belt01_b_step02_locator" ):  # front locators
                config.clip_second_up_right_locator_id = clipChild

            if childNameLower.startswith( "belt02_a_step02_locator" ):  # front locators
                config.clip_first_up_left_locator_id = clipChild
            if childNameLower.startswith( "belt02_b_step02_locator" ):  # front locators
                config.clip_second_up_left_locator_id = clipChild

            if childNameLower.startswith( "belt03_a_step01_locator" ):
                config.clip_first_central_locator_id = clipChild
            if childNameLower.startswith( "belt03_b_step01_locator" ):
                config.clip_second_central_locator_id = clipChild

        beltId = -1

        args = [ config ]

        if joints_to_remove:
            joints = city_builder.core.StringVector()
            for joint in joints_to_remove:
                joints.append( joint )
            args.append( joints )

        self.validateConfig( config )

        beltId = self._workspace.create_child_seat_belt( *args )

        # Set the user custom metadata with the belt placement and the 
        seat_info = {}
        seat_info['number'] = 'seat0{}'.format(seat_pos)
        self.setCustomMetadata(beltId, "Seat", seat_info)
        self.setCustomMetadata(beltId, "Placement", "Normal")

        return beltId

    #_______________________________________________________________
    def createBabyBelt( self, childseat ):
        # Get the belt on asset for the specific child seat
        belts_on = [ b for b in anyverse_platform.childseatbelts if 'on' in b['version'].lower() and b['brand'].lower() == childseat['brand'].lower() and b['model'].lower() == childseat['model'].lower() and b['aim looking'].lower() == childseat['aim looking'].lower() ]

        if len(belts_on) == 1:
            belt_on = belts_on[0]
        else:
            print('[ERROR] No belt ON found for child seat brand {} model {}'.format(childseat['brand'], childseat['model']))
            return False
        
        belt_on['entity_id'] = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, belt_on['resource_id'])
        belt_on_id = self._workspace.create_fixed_entity( belt_on['name'], childseat['fixed_entity_id'], belt_on['entity_id'] )
        self._workspace.set_entity_property_value(belt_on_id, 'ExportConfigurationComponent', 'export_always', True)
        self._workspace.set_entity_property_value(belt_on_id, 'ExportConfigurationComponent', 'exclude_from_occlusion_tests', True)
        
        return True
    
    #_______________________________________________________________
    def selectConditions(self, conditions):
        probabilities = [ float(c['probability']) for c in conditions ]
        cond = conditions[self.choiceUsingProbabilities(probabilities)]

        return cond['Day'], cond['interior-lights']

    #_______________________________________________________________
    def seatLocator2ChildseatLocator(self, seat_locator, the_car):
        childseat_locators = self.getChildseatLocators(the_car)
        seat_locator_name = self._workspace.get_entity_name(seat_locator)
        childseat_locator_name = 'child' + seat_locator_name

        # print('[INFO] transforming {} to {}'.format(seat_locator_name,childseat_locator_name))

        for childseat_locator in childseat_locators:
            if self._workspace.get_entity_name(childseat_locator).lower() == childseat_locator_name:
                ret = childseat_locator
                break

        return ret


    #_______________________________________________________________
    def fillSeat(self, occupancy, seat_locator, childseat_config, asset = None, seatbelts_distribution = None, accessories_probabilities = None, expression_probabilities = None, baby_on_lap_probability = 0, age_group_probabilities = None, object_types = None, allow_child_driver = False):
        the_car = self.getCars()[0]
        car_name = self._workspace.get_entity_name(self._workspace.get_entity_property_value(the_car, 'AssetEntityReferenceComponent','asset_entity_id'))
        if occupancy == 0:
            ret = {}
            self.doNothing(seat_locator)
            if seatbelts_distribution is not None:
                set_seatbel_on = True if random.uniform(0,1) <= seatbelts_distribution["belt_on_without_character_probability"] else False
                if set_seatbel_on and not self._script_console:
                    print('[INFO] Setting belt on to empty seat {}'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))
                    self.createBeltFor(self.getSeatPos(seat_locator), anyverse_platform.invalid_entity_id, self._car_brand, self._car_model, seatbelts_distribution)

            ret['isEmpty'] = True
            ret['Seatbelt_on'] = set_seatbel_on
        elif occupancy == 1:
            driver = self.placeDriver(seat_locator, seatbelts_distribution = seatbelts_distribution, accessories_probabilities = accessories_probabilities, expression_probabilities = expression_probabilities, age_group_probabilities = age_group_probabilities, allow_child_driver = allow_child_driver)
            if driver == None:
                print('[WARN]: Could not find a driver to place')
            ret = driver
        elif occupancy == 2:
            childseat_occupancy_probabilities = childseat_config['childseat_occupancy_probabilities']
            childseat = self.placeChildseat(seat_locator, childseat_config, only_baby_in_copilot = False)
            if childseat != None:
                childseat_occupancy = self.decideChildSeatOccupancy(childseat_occupancy_probabilities)
                if childseat_occupancy == 0: # Empty
                    child = None
                    print('[INFO]: Leaving childseat empty')
                    if childseat['kind'].lower() != 'booster':
                        self.setChildSeatSeatbeltOff(childseat)
                    ret = [childseat, child]
                elif childseat_occupancy == 1: # Child
                    if childseat['kind'] != 'BabyChild':
                        child = self.placeChildInChildseat(childseat, seat_locator, seatbelts_distribution = seatbelts_distribution, expression_probabilities = expression_probabilities)
                    else:
                        child = self.placeBabyInChildseat(childseat, seat_locator, seatbelts_distribution = seatbelts_distribution)
                    ret = [childseat, child]
                elif childseat_occupancy == 2: # Object
                    childseat_locator = self.getChildLocatorInChildSeat(childseat['fixed_entity_id'])
                    if childseat_locator != -1:
                        object = self.placeObjectInChildseat(childseat_locator, childseat, object_types)
                    else:
                        print('[WARN] Cannot place object without a locator in child seat.')
                        object = None
                    ret = [childseat, object]
            else:
                print('[WARN]: Could not find a childseat to place')
                ret = {}
                ret['isEmpty'] = True
                ret['Seatbelt_on'] = False
        elif occupancy == 3:
            baby_on_lap = False if random.uniform(0,1) > baby_on_lap_probability else True
            passenger = self.placePassenger(seat_locator, seatbelts_distribution = seatbelts_distribution, accessories_probabilities = accessories_probabilities, expression_probabilities = expression_probabilities, baby_on_lap = baby_on_lap)
            if passenger == None:
                print('[WARN]: Could not find a passenger to place')
            # move the arms free around xiphoid
            elif not self.isCopilotSeat(seat_locator) and not baby_on_lap:
                self.setBackSeatPassengerPose(seat_locator) if random.uniform(0, 1) < 0.75 else True

            ret = passenger
        elif occupancy == 4:
            object = self.placeObjectOnSeat(seat_locator, self.getParent(seat_locator), object_types)

            if object == None:
                print('[WARN]: Could not find a object to place')
            ret = object
        else:
            print('[ERROR] Invalid filling seat action')

        return ret

    #_______________________________________________________________
    def EmptyDistribution(self, the_car, occupancy_distribution, day):
        print('[INFO] Empty distribution, leaving the car empty')
        seat_locators = self.getSeatLocators(the_car)
        occupied_seats = 0
        ret = {}
        ret['day'] = day
        ret['occupancy'] = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            occupancy = 0 # Empty
            # Now we fill the seats to apply the seatbelt logic on empty seats
            seat_occupant = self.fillSeat(occupancy,seat_locator,
                                        childseat_config = occupancy_distribution['childseat_config'],
                                        seatbelts_distribution = occupancy_distribution['seatbelts_distribution'],
                                        accessories_probabilities = occupancy_distribution['accessories_probabilities']
                                        )
            ret['occupancy'].append({'seat': seat_locator_name, 'childseat': False, 'occupant': 'empty', 'seat_belt_on': seat_occupant['Seatbelt_on']})
        return ret

    #_______________________________________________________________
    def NormalOccupantDistribution(self, the_car, occupancy_distribution, day):
        seat_locators = self.getSeatLocators(the_car)
        seven_seater = False
        if len(seat_locators) == 7:
            seven_seater = True
        occupied_seats = 0
        ret = {}
        ret['day'] = day
        ret['occupancy'] = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            if seven_seater and 'seat05' in seat_locator_name:
                break
            occupancy = self.decideSeatOccupancy(seat_locator, occupancy_distribution)
            if occupancy != 0:
                occupied_seats += 1
            if occupancy == 2: # 2 means we are placing a childseat so we need the childseat locator
                seat_locator = self.seatLocator2ChildseatLocator(seat_locator, the_car)

            if 'expression_probabilities' in occupancy_distribution:
                expression_probabilities = occupancy_distribution['expression_probabilities']
            else:
                expression_probabilities = None

            if 'baby_on_lap_probability' in occupancy_distribution:
                baby_on_lap_probability = occupancy_distribution['baby_on_lap_probability']
            else:
                baby_on_lap_probability = 0

            if 'age_group_probabilities' in occupancy_distribution:
                age_group_probabilities = occupancy_distribution['age_group_probabilities']
            else:
                age_group_probabilities = None

            if 'object_types' in occupancy_distribution:
                object_types = occupancy_distribution['object_types']
            else:
                object_types = None

            if 'allow_child_driver' in occupancy_distribution:
                allow_child_driver = occupancy_distribution['allow_child_driver']
            else:
                allow_child_driver = None

            seat_occupant = self.fillSeat(occupancy,seat_locator,
                                        childseat_config = occupancy_distribution['childseat_config'],
                                        seatbelts_distribution = occupancy_distribution['seatbelts_distribution'],
                                        accessories_probabilities = occupancy_distribution['accessories_probabilities'],
                                        expression_probabilities = expression_probabilities,
                                        baby_on_lap_probability = baby_on_lap_probability,
                                        age_group_probabilities = age_group_probabilities,
                                        object_types = object_types,
                                        allow_child_driver = allow_child_driver
                                        )

            # Build a return list with a dict with the occupancy of every seat
            if not seat_occupant:
                ret['occupancy'].append({'seat': seat_locator_name, 'childseat': False, 'occupant': 'empty', 'seat_belt_on': False})
            elif 'isEmpty' in seat_occupant:
                ret['occupancy'].append({'seat': seat_locator_name, 'childseat': False, 'occupant': 'empty', 'seat_belt_on': seat_occupant['Seatbelt_on']})
            else:
                if type(seat_occupant) != list:
                    if 'gender' in seat_occupant.keys():
                        occupant_type = 'person'
                        if seat_occupant['gender'] == 'Male':
                            occupant_type = 'man'
                        elif seat_occupant['gender'] == 'Female':
                            occupant_type = 'woman'
                    else:
                        occupant_type = 'animal' if seat_occupant['class'].lower() == ['dog', 'cat'] else 'object'
                    ret['occupancy'].append({'seat': seat_locator_name, 'childseat': False, 'occupant': occupant_type, 'seat_belt_on': seat_occupant['Seatbelt_on']})
                else:
                    if seat_occupant[1] != None:
                        
                        ret['occupancy'].append({'seat': seat_locator_name, 'childseat': True, 'occupant': 'child', 'seat_belt_on': seat_occupant[1]['Seatbelt_on']})
                    else:
                        ret['occupancy'].append({'seat': seat_locator_name, 'childseat': True, 'occupant': 'empty', 'seat_belt_on': False})

        if 'gaze_probabilities' in occupancy_distribution:
            gaze_distribution = occupancy_distribution['gaze_probabilities']
        else:
            gaze_distribution = None
            print('[WARN] No gaze probabilities')

        # After occupancy is complete we adjust the driver's and copilot's gaze
        # according to configuration 
        if gaze_distribution:
            driver_gaze = gaze_distribution['driver_gaze_probabilities']
            self.setDriverGaze(driver_gaze) 
            copilot_gaze = gaze_distribution['copilot_gaze_probabilities']
            self.setPassengerGaze(copilot_gaze)


        return ret, occupied_seats

    #_______________________________________________________________
    def setDriverGaze(self, gaze_probabilities):
        the_car = self.getCars()[0]
        seat_locators = self.getSeatLocators(the_car)
        driver_seat = [ ent for ent in seat_locators if 'seat01' in self._workspace.get_entity_name(ent).lower() ][0]
        driver_l = [ ent for ent in self._workspace.get_hierarchy(driver_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
        driver = driver_l[0] if len(driver_l) > 0 else anyverse_platform.invalid_entity_id
        # We consider the passenger what ever is placed in the copilot seat:
        # (character, object, child seat, child on child seat, object on child seat or the seat itself if empty)
        passenger_seat = self.getParent([ ent for ent in seat_locators if 'seat02' in self._workspace.get_entity_name(ent).lower() ][0])
        passenger_l = [ ent for ent in self._workspace.get_hierarchy(passenger_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'clipEntity' not in self._workspace.get_entity_name(ent) ]
        if len(passenger_l) > 0:
            passenger = passenger_l[len(passenger_l)-1]
        else:
            passenger = passenger_seat

        gaze_info = {}
        idx = self.choiceUsingProbabilities([ float(o['probability']) for o in gaze_probabilities ])
        gaze_id = gaze_probabilities[idx]['id']
        reach = gaze_probabilities[idx]['reach']
        change_gaze = True if random.uniform(0,1) < gaze_probabilities[idx]['gaze'] else False
        gaze_info['direction'] = gaze_probabilities[idx]['name']
        gaze_info['code'] = gaze_id
        gaze_info['change-gaze'] = change_gaze
        gaze_info['reach'] = reach
        if driver != anyverse_platform.invalid_entity_id:
            print('[INFO] Setting the driver to look at {}({})'.format(gaze_probabilities[idx]['name'], gaze_probabilities[idx]['id']))
            # if gaze == 0 do nothing: looking straight at the road
            if gaze_id == 1: # exterior rear view mirror (50% each side)
                if change_gaze:
                    side = 'left' if random.uniform(0,1) <= 0.5 else 'right'
                    self.LookAtExteriorRearViewMirror(driver, the_car, side)
                    gaze_info['direction'] += '_' + side
            elif gaze_id == 2: # inside rear view mirror
                if change_gaze:
                    self.LookAtInsideRearViewMirror(driver, the_car)
                side = 'left' if random.uniform(0,1) <= 0.5 else 'right'
                if reach:
                    self.reachRVM(driver, side)
            elif gaze_id == 3: # infotaintment
                if change_gaze:
                    self.LookAtInfotainment(driver, the_car)
                if reach:
                    self.reachInfotainment(driver, 'right')
            elif gaze_id == 4: # passenger
                if change_gaze:
                    self.LookAtOtherCharacter(driver, passenger)
            elif gaze_id == 5: # rear seat
                if change_gaze:
                    self.LookAtRearSeat(driver, the_car, 'right')
            elif gaze_id == 6: # headrest
                if change_gaze:
                    self.LookAtHeadrest(driver, the_car, 'right')
                if reach:
                    self.reachHeadrest(driver, 'right') # reach the right side headrest
            elif gaze_id == 7: # glove compartment
                if change_gaze:
                    self.LookAtGloveCompartment(driver, the_car)
                if reach:
                    self.reachGloveCompartment(driver, 'right')
            elif gaze_id == 8: # seat belt
                if change_gaze:
                    self.LookAtSeatbelt(driver, the_car, 'left')
                if reach:
                    self.reachSeatbelt(driver, 'right')
            elif gaze_id == 9: # floor own side
                if change_gaze:
                    self.LookAtFloor(driver, the_car, 'left')
                if reach:
                    self.reachFloor(driver, 'left')
            elif gaze_id == 10:
                animation, weight = self.selectAdultAnimation('head', 0, 1)
                self.setAnimation('head', animation, weight, driver)
                print('[INFO] setting {}({}) head animation'.format(self._workspace.get_entity_name(animation), weight))
                hand = 'left' if random.uniform(0,1) >= 0.5 else 'right'
                self.reachXiphoidLocator(driver, hand, 0.3)
                gaze_info['reach'] = True

            self.setCustomMetadata(driver, 'gaze', gaze_info)
        else:
            print('[WARN]: Cannot set gaze, no driver')

    #_______________________________________________________________
    def setPassengerGaze(self, gaze_probabilities):
        the_car = self.getCars()[0]
        seat_locators = self.getSeatLocators(the_car)
        # We consider the driver what ever is placed in the driver seat:
        # (a character or the seat itself if empty)
        driver_seat = self.getParent([ ent for ent in seat_locators if 'seat01' in self._workspace.get_entity_name(ent).lower() ][0])
        driver_l = [ ent for ent in self._workspace.get_hierarchy(driver_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
        driver = driver_l[len(driver_l)-1] if len(driver_l) > 0 else driver_seat

        passenger_seat = self.getParent([ ent for ent in seat_locators if 'seat02' in self._workspace.get_entity_name(ent).lower() ][0])
        passenger_l = [ ent for ent in self._workspace.get_hierarchy(passenger_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
        passenger = passenger_l[0] if len(passenger_l) > 0 else anyverse_platform.invalid_entity_id

        gaze_info = {}
        idx = self.choiceUsingProbabilities([ float(o['probability']) for o in gaze_probabilities ])
        gaze_id = gaze_probabilities[idx]['id']
        reach = gaze_probabilities[idx]['reach']
        change_gaze = True if random.uniform(0,1) <= gaze_probabilities[idx]['gaze'] else False
        gaze_info['direction'] = gaze_probabilities[idx]['name']
        gaze_info['code'] = gaze_id
        gaze_info['change-gaze'] = change_gaze
        gaze_info['reach'] = reach
        if passenger != anyverse_platform.invalid_entity_id:
            is_child = 'child' in self._workspace.get_entity_name(self.getParent(passenger)).lower()
            # if gaze_id == 0 do nothing: looking straight at the road
            if gaze_id == 1: # exterior rear view mirror (50% each side)
                if change_gaze:
                    side = 'left' if random.uniform(0,1) <= 0.5 else 'right'
                    self.LookAtExteriorRearViewMirror(passenger, the_car, side)
                    gaze_info['direction'] += '_' + side
            elif gaze_id == 2: # inside rear view mirror
                if change_gaze:
                    self.LookAtInsideRearViewMirror(passenger, the_car)
                if reach:
                    self.reachRVM(driver, 'right')
            elif gaze_id == 3: #  infotaintment
                if change_gaze:
                    self.LookAtInfotainment(passenger, the_car)
                if reach:
                    self.reachInfotainment(passenger, 'left')
            elif gaze_id == 4: #passenger
                if change_gaze:
                    self.LookAtOtherCharacter(passenger, driver)
            elif gaze_id == 5 and not is_child: # rear seat
                if change_gaze:
                    self.LookAtRearSeat(passenger,the_car, 'left')
            elif gaze_id == 6 and not is_child: # headrest
                if change_gaze:
                    self.LookAtHeadrest(passenger, the_car, 'left')
                if reach:
                    self.reachHeadrest(passenger, 'left')
            elif gaze_id == 7: # glove compartment
                if change_gaze:
                    self.LookAtGloveCompartment(passenger, the_car)
                if reach:
                    self.reachGloveCompartment(passenger, 'right')
            elif gaze_id == 8 and not is_child: # seat belt
                if change_gaze:
                    self.LookAtSeatbelt(passenger, the_car, 'right')
                if reach:
                    self.reachSeatbelt(passenger, 'left')
            elif gaze_id == 9 and not is_child: # floor own side
                if change_gaze:
                    self.LookAtFloor(passenger, the_car, 'right')
                if reach:
                    self.reachFloor(passenger, 'right')
            elif gaze_id == 10:
                animation, weight = self.selectAdultAnimation('head', 0, 1)
                self.setAnimation('head', animation, weight, passenger)
                print('[INFO] setting {}({}) head animation'.format(self._workspace.get_entity_name(animation), weight))
                both_hands = False if random.uniform(0,1) >= 0.5 else True
                if both_hands:
                    self.reachXiphoidLocator(passenger, 'left')
                    self.reachXiphoidLocator(passenger, 'right')
                else:
                    hand = 'left' if random.uniform(0,1) >= 0.5 else 'right' 
                    self.reachXiphoidLocator(passenger, hand)

            print('[INFO] Setting the passenger to look at {}({})'.format(gaze_info['direction'], gaze_info['code']))
            self.setCustomMetadata(passenger, 'gaze', gaze_info)
        else:
            print('[WARN]: Cannot set gaze, no passenger.')

    #_______________________________________________________________
    def setBackSeatPassengerPose(self, seat_locator):
        passenger_l = [ ent for ent in self._workspace.get_hierarchy(seat_locator) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
        passenger = passenger_l[0] if len(passenger_l) > 0 else anyverse_platform.invalid_entity_id

        animation, weight = self.selectAdultAnimation('head', 0, 1)
        self.setAnimation('head', animation, weight, passenger)
        print('[INFO] setting {}({}) head animation'.format(self._workspace.get_entity_name(animation), weight))
        both_hands = False if random.uniform(0,1) >= 0.5 else True
        if both_hands:
            self.reachXiphoidLocator(passenger, 'left')
            self.reachXiphoidLocator(passenger, 'right')
        else:
            hand = 'left' if random.uniform(0,1) >= 0.5 else 'right' 
            self.reachXiphoidLocator(passenger, hand)

    #_______________________________________________________________
    def getOccupant(self, seat_locator, occupant_dist):
        seat_name = self._workspace.get_entity_name(seat_locator).split("_")[0]
        for occupant in occupant_dist:
            if occupant['Seat'] == seat_name:
                return occupant

    #_______________________________________________________________
    def getOccupantByType(self, occupant_type):
        occupant = (-1, None)
        gender = None
        kind = None
        if occupant_type == 'man':
            gender = 'Male'
        elif occupant_type == 'woman':
            gender = 'Female'
        elif occupant_type == 'person':
            kind = 'Adult'
        elif occupant_type == 'child':
            kind = 'Child'

        if gender:
            found = False
            while not found:
                occupant = self.selectCharacter('gender', gender)
                found = True if occupant[1]['kind'] == 'Adult' else False

        if kind:
            occupant = self.selectCharacter('kind', kind)

        if occupant[1]:
            occupant[1]['entity_id'] = occupant[0]

        return occupant[1]
    
    #_______________________________________________________________
    def getSeatOccupancyFromGemini(self, seat_locator, occupancy):
        seat_name = self._workspace.get_entity_name(seat_locator).split("_")[0]
        for seat_occupancy in occupancy:
            if seat_occupancy['seat'] == seat_name:
                return seat_occupancy
    
    #_______________________________________________________________
    def applyOccupantDistributionFromGemini(self, the_car, occupancy_distribution, occupant_dist, random_object_on_empty_prob = 0):
        seat_locators = self.getSeatLocators(the_car)
        seatbelts_distribution = {
            'random_belt_material': True,
            'differentiate_segments': False,
            'belt_on_probability': 0.0, # Probability for seatbelt on when there is a character seated on
            'seatbelt_placement_probabilities': {
                'Normal': 1.0,
                'BehindTheBack': 0.0,
                'UnderShoulder': 0.0,
                'WrongSideOfHead': 0.0,
                'CharacterOverSeatbelt': 0.0
            },   
            'belt_on_without_character_probability': 0.0, # Probability for seatbelt on when the seat is empty
        }
        animal_types = ['cat', 'Dog']
        object_types = ['Backpack', 'Baseball_cap', 'Bottle', 'Box', 'Can', 'Coffee', 'Consumer_electronics', 'Glasses', 'Handbag', 'Hat', 'Milkshake', 'Mobile Phone', 'Paper_Bag', 'Snack', 'Sunglasses', 'Toy', 'ammunition', 'cloth', 'garbage bag', 'handgun', 'knife', 'paper_bag', 'plastic bag', 'sheath', 'snack', 'wallet'] # All possible object types

        ret = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            seat_occupancy = self.getSeatOccupancyFromGemini(seat_locator, occupant_dist['occupancy'])
            occupied = seat_occupancy['occupant'] != 'empty'
            if seat_occupancy['seat_belt_on']:
                seatbelts_distribution['belt_on_probability'] = 0.5
                
            seat_occupant = None
            occupant_type = seat_occupancy['occupant']
            occupant = self.getOccupantByType(occupant_type)
            # print(occupant_type)
            # print(occupant)
            if self.isDriverSeat(seat_locator) and occupied:
                seat_occupant = self.placeDriver(seat_locator, occupant=occupant, seatbelts_distribution=seatbelts_distribution)
            else:
                if occupant_type == 'child':
                    childseat_config = occupancy_distribution['childseat_config']
                    childseat = self.placeChildseat(seat_locator, childseat_config, only_baby_in_copilot = False)
                    if childseat['kind'] == 'BabyChild' and occupied:
                        child = self.placeBabyInChildseat(childseat, seat_locator, seatbelts_distribution=seatbelts_distribution)
                        self._workspace.set_entity_property_value(childseat['fixed_entity_id'], 'RelativeTransformToComponent','scale', anyverse_platform.Vector3D(0.9,0.9,0.9))
                    else:
                        child = self.placeChildInChildseat(childseat, seat_locator,  seatbelts_distribution=seatbelts_distribution)
                        self._workspace.set_entity_property_value(childseat['fixed_entity_id'], 'RelativeTransformToComponent','scale', anyverse_platform.Vector3D(0.8,0.8,0.8))
                    seat_occupant = [childseat, child]
                elif (occupant_type == 'man' or occupant_type == 'woman' or occupant_type == 'person') and occupied:
                    seat_occupant = self.placePassenger(seat_locator, occupant=occupant, seatbelts_distribution=seatbelts_distribution)
                elif occupied:
                    if occupant_type == 'animal':
                        seat_occupant = self.placeObjectOnSeat(seat_locator, self.getParent(seat_locator), object_types = animal_types)
                    else:
                        seat_occupant = self.placeObjectOnSeat(seat_locator, self.getParent(seat_locator), object_types = object_types)
                elif seat_occupancy['child_seat']:
                    chilldseat_config = occupancy_distribution['childseat_config']
                    childseat = self.placeChildseat(seat_locator, chilldseat_config, only_baby_in_copilot = False)
                elif random_object_on_empty_prob:
                    random_object_types = ['Backpack', 'briefcase', 'Mobile Phone', 'laptop_case', 'Paper_Bag', 'Handbag', 'cloth']
                    seat_occupant = self.placeObjectOnSeat(seat_locator, self.getParent(seat_locator), object_types = random_object_types) if random.uniform(0,1) < random_object_on_empty_prob else None

            # Build a return list with a dict with the occupancy of every seat
            if seat_occupant == None:
                ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': 'None', 'Seatbelt_on': False})
            else:
                if type(seat_occupant) != list:
                    ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': seat_occupant['name'], 'Seatbelt_on': seat_occupant['Seatbelt_on'], 'Seatbelt_mode': seat_occupant['Seatbelt_placement'], 'Accessory': seat_occupant['Accessory']})
                else:
                    if seat_occupant[1] != None:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['name'], 'Occupant': seat_occupant[1]['name'], 'Seatbelt_on': seat_occupant[1]['Seatbelt_on']})
                    else:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['name'], 'Occupant': 'None', 'Seatbelt_on': False})

        if 'gaze_probabilities' in occupancy_distribution:
            gaze_distribution = occupancy_distribution['gaze_probabilities']
        else:
            gaze_distribution = None
            print('[WARN] No gaze probabilities')

        # After occupancy is complete we adjust the driver's and copilot's gaze
        # according to configuration 
        if gaze_distribution:
            driver_gaze = gaze_distribution['driver_gaze_probabilities']
            self.setDriverGaze(driver_gaze) 
            copilot_gaze = gaze_distribution['copilot_gaze_probabilities']
            self.setPassengerGaze(copilot_gaze)

        return ret

    #_______________________________________________________________
    def createGloveCompLocator(self, the_car, displace = True):
        glove_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'glove_' in self._workspace.get_entity_name(ent) ]
        if len(glove_locators) > 0:
            # print('[INFO] Recreating glove compartment locator')
            self._workspace.delete_entity(glove_locators[0])
        glove_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'glove_locator', the_car)

        try:
            pos = self._look_and_reach_positions['glove']['right']
            x, y, z = pos[0],  pos[1], pos[2]
            if displace:
                x += random.uniform(-0.3, 0)
                y += random.uniform(-0.3, 0.3)
                z += random.uniform(-0.25, 0.25)
            loc_position = anyverse_platform.Vector3D(x, y, z)
        except KeyError as ke:
            print('[WARN] No position defined for glove compartment')
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(glove_locator,'RelativeTransformToComponent','position', loc_position)
        # print('[INFO] Glove compartment locator: {}'.format(self._workspace.get_entity_name(glove_locator)))
        return glove_locator

    #_______________________________________________________________
    def createFloorLocator(self, the_car, side):
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'floor_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            # print('[INFO] Recreating floor {} locator'.format(side))
            self._workspace.delete_entity(locators[0])            
        floorlocator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'floor_' + side + '_locator', the_car)
        try:
            pos = self._look_and_reach_positions['floor'][side]
            x, y, z = pos[0],  pos[1], pos[2]
            loc_position = anyverse_platform.Vector3D(x, y, z)
            delta = random.uniform(0, 0.5)
            loc_position.z += delta
        except KeyError as ke:
            print('[WARN] No position defined for floor side {}'.format(side))
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(floorlocator,'RelativeTransformToComponent','position', loc_position)

        # print('[INFO] Floor locator: {}'.format(self._workspace.get_entity_name(floorlocator)))
        return floorlocator

    #_______________________________________________________________
    def createHeadrestLocator(self, the_car, side, displace = True):
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'headrest_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            # print('[INFO] Recreating headrest {} locator'.format(side))
            self._workspace.delete_entity(locators[0])            
        headrest_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'headrest_' + side + '_locator', the_car)
        try:
            pos = self._look_and_reach_positions['headrest'][side]
            x, y, z = pos[0],  pos[1], pos[2]
            if displace:
                x += random.uniform(-0.2, 0.3)
                y += random.uniform(-0.2, 0.2)
                z += random.uniform(-0.3, 0.3)
            loc_position = anyverse_platform.Vector3D(x, y, z)
            # loc_position.y = random.uniform(loc_position.y, 0) if loc_position.y < 0 else random.uniform(0,loc_position.y)
        except KeyError as ke:
            print('[WARN] No position defined for headrest side {}'.format(side))
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(headrest_locator,'RelativeTransformToComponent','position', loc_position)

        # print('[INFO] Headrest locator: {}'.format(self._workspace.get_entity_name(headrest_locator)))
        return headrest_locator

    #_______________________________________________________________
    def createSeatbeltLocator(self, the_car, side, displace = True):
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'seatbelt_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            # print('[INFO] Recreating seatbelt {} locator'.format(side))
            self._workspace.delete_entity(locators[0])            
        seatbeltlocator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'seatbelt_' + side + '_locator', the_car)
        try:
            pos = self._look_and_reach_positions['seatbelt'][side]
            x, y, z = pos[0],  pos[1], pos[2]
            if displace:
                x += random.uniform(-0.2, 0.2)
                y += random.uniform(0, 0.1) if side == 'right' else random.uniform(-0.1, 0)
                z += random.uniform(0, 0.2)
            loc_position = anyverse_platform.Vector3D(x, y, z)
        except KeyError as ke:
            print('[WARN] No position defined for seat belt side {}'.format(side))
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(seatbeltlocator,'RelativeTransformToComponent','position', loc_position)

        # print('[INFO] Seatbelt locator: {}'.format(self._workspace.get_entity_name(seatbeltlocator)))
        return seatbeltlocator

    #_______________________________________________________________
    def createRVMLocator(self, the_car, side):
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'rvm_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            # print('[INFO] Recreating rvm {} locator'.format(side))
            self._workspace.delete_entity(locators[0])            
        rvm_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'rvm_' + side + '_locator', the_car)
        try:
            pos = self._look_and_reach_positions['rvm'][side]
            x, y, z = pos[0],  pos[1], pos[2]
            loc_position = anyverse_platform.Vector3D(x, y, z)
        except KeyError as ke:
            print('[WARN] No position defined for rvm side {}'.format(side))
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(rvm_locator,'RelativeTransformToComponent','position', loc_position)

        # print('[INFO] RVM locator: {}'.format(self._workspace.get_entity_name(rvm_locator)))
        return rvm_locator

    #_______________________________________________________________
    def createCCLocator(self, the_car, displace = False):
        cc_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'cc_info' in self._workspace.get_entity_name(ent) ]
        if len(cc_locators) > 0:
            # print('[INFO] Recreating CC locator')
            self._workspace.delete_entity(cc_locators[0])
        cc_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'cc_info_locator', the_car)

        try:
            pos = self._look_and_reach_positions['cc']['center']
            x, y, z = pos[0],  pos[1], pos[2]
            if displace:
                x += random.uniform(-0.3, 0)
                y += random.uniform(-0.3, 0.3)
                z += random.uniform(-0.25, 0.35)
            loc_position = anyverse_platform.Vector3D(x, y, z)
        except KeyError as ke:
            print('[WARN] No position defined for central console')
            loc_position = anyverse_platform.Vector3D(0, 0, 0)
        self._workspace.set_entity_property_value(cc_locator,'RelativeTransformToComponent','position', loc_position)
        # print('[INFO] CC locator: {}'.format(self._workspace.get_entity_name(cc_locator)))
        return cc_locator

    #_______________________________________________________________
    def reachLocator(self, character_id, hand, locator, offset = None):
        type = None
        try:
            type = self._workspace.get_entity_type(locator)
        except:
            print('[ERROR] locator {} does not exist.'.format(locator))
            locator_name = None
        if type == 'Locator':
            hand_config = 'left_hand_config.locator_entity_id'
            if hand == 'right':
                hand_config = 'right_hand_config.locator_entity_id'
            self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent',hand_config, locator)
            if offset is not None:
                self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent',hand_config+'.offset', offset)
            locator_name = self._workspace.get_entity_name(locator)
        elif type is not None:
            print('[WARN] {}({}) not a locator.'.format(self._workspace.get_entity_name(locator), locator))
        return locator_name

    #_______________________________________________________________
    def reachXiphoidLocator(self, char_id, hand, max_distance = 0.4):
        xiphoid_locators = [ ent for ent in self._workspace.get_hierarchy(char_id) if self._workspace.get_entity_type(ent) == 'Locator' and 'xiphoid' in self._workspace.get_entity_name(ent) ]
        for loc in xiphoid_locators:
            self._workspace.delete_entity(loc)

        xiphoid = [ b for b in self._workspace.get_hierarchy(char_id) if 'SkeletonJointEntity' == self._workspace.get_entity_type(b) and 'xiphoid' in self._workspace.get_entity_name(b) ][0]
        xiphoid_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, hand + 'xiphoid_locator', xiphoid)
        xiphoid_position = self._workspace.get_entity_local_position(xiphoid_locator)
        xiphoid_position.x += random.uniform(0.1, max_distance)
        xiphoid_position.y += random.uniform(-max_distance, max_distance)
        xiphoid_position.z += random.uniform(-max_distance, max_distance)

        self._workspace.set_entity_property_value(xiphoid_locator, 'RelativeTransformToComponent','position', xiphoid_position)

        if hand == 'left':
            self._workspace.set_entity_property_value(char_id, 'CharacterHandAttachmentComponent','left_hand_config.locator_entity_id', xiphoid_locator)
        else:
            self._workspace.set_entity_property_value(char_id, 'CharacterHandAttachmentComponent','right_hand_config.locator_entity_id', xiphoid_locator)

        return xiphoid_locator

    #_______________________________________________________________
    def reachFloor(self, character_id, hand):
        the_car = self.getCars()[0]

        # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0.5, 1, 'leaning_forward_extreme')
        self.setAnimation('spine', animation, weight, character_id)

        side = hand
        floor_locator = self.getFloorLocator(the_car, side)
        if floor_locator:
            locator_name = self.reachLocator(character_id, hand, floor_locator)
        else:
            print('[WARN] Could not find {} floor locator.'.format(side))
        return locator_name

    #_______________________________________________________________
    def reachSeatbelt(self, character_id, hand):
        the_car = self.getCars()[0]

        if hand == 'right':
            side = 'left'
        elif hand == 'left':
            side = 'right'

         # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0, 0.1, 'leaning_forward')
        self.setAnimation('spine', animation, weight, character_id)

        seatbelt_locator = self.getSeatbeltLocator(the_car, side)
        if seatbelt_locator:
            locator_name = self.reachLocator(character_id, hand, seatbelt_locator)
        else:
            print('[WARN] Could not find {} seatbelt locator.'.format(side))
        return locator_name

    #_______________________________________________________________
    def reachHeadrest(self, character_id, hand):
        the_car = self.getCars()[0]

        side = hand

         # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0.3, 0.5, 'leaning_forward')
        self.setAnimation('spine', animation, weight, character_id)

        headrest_locator = self.getHeadrestLocator(the_car, side)
        if headrest_locator:
            locator_name = self.reachLocator(character_id, hand, headrest_locator)
        else:
            print('[WARN] Could not find {} headrest locator.'.format(side))
        return locator_name

    #_______________________________________________________________
    def reachGloveCompartment(self, character_id, hand):
        the_car = self.getCars()[0]

         # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0.5, 1, 'leaning_forward_extreme')
        self.setAnimation('spine', animation, weight, character_id)

        glove_locator = self.getGloveCompLocator(the_car)
        if glove_locator:
            locator_name = self.reachLocator(character_id, hand, glove_locator)
        else:
            print('[WARN] Could not find glove compartment locator.')
        return locator_name

    #_______________________________________________________________
    def reachInfotainment(self, character_id, hand):
        the_car = self.getCars()[0]
        cc_locator = self.getCCLocator(the_car)
        if cc_locator:
            locator_name = self.reachLocator(character_id, hand, cc_locator)
        else:
            print('[WARN] Could not find CC infotainment locator.')
        return locator_name

    #_______________________________________________________________
    def reachRVM(self, character_id, hand):
        the_car = self.getCars()[0]
        rvm_inside_locator = self.getRVMLocator(the_car, 'inside')
        if rvm_inside_locator:
            loc_rot = self._workspace.get_entity_property_value(rvm_inside_locator, 'RelativeTransformToComponent','rotation')
            loc_rot.z += 90
            loc_rot.y += 0
            loc_rot.x += 45
            self._workspace.set_entity_property_value(rvm_inside_locator, 'RelativeTransformToComponent','rotation', loc_rot)
            offset_value = random.uniform(-0.4,0.1)
            offset = anyverse_platform.Vector3D(0,0,offset_value)
            locator_name = self.reachLocator(character_id, hand, rvm_inside_locator, offset=offset)
        else:
            print('[WARN] Could not find RVM locator.')
        return locator_name+' ({})'.format(offset_value)

    #_______________________________________________________________
    def getSeatbeltLocator(self, the_car, side):
        return self.getLocator(the_car, 'seatbelt_'+side)

    #_______________________________________________________________
    def getFloorLocator(self, the_car, side):
        return self.getLocator(the_car, 'floor_'+side)

    #_______________________________________________________________
    def getHeadrestLocator(self, the_car, side):
        return self.getLocator(the_car, 'headrest_'+side)

    #_______________________________________________________________
    def getRVMLocator(self, the_car, side):
        return self.getLocator(the_car, 'rvm_'+side)

    #_______________________________________________________________
    def getGloveCompLocator(self, the_car):
        return self.getLocator(the_car, 'glove_')

    #_______________________________________________________________
    def getCCLocator(self, the_car):
        return self.getLocator(the_car, 'cc_info')

    #_______________________________________________________________
    def getLocator(self, the_car, prefix):
        locator = None
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and prefix in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            locator = locators[0]
        else:
            print('[WARN] Could NOT find {}_locator'.format(prefix))

        # print('[INFO] locator: {}'.format(self._workspace.get_entity_name(locator)))
        return locator

    #_______________________________________________________________
    def letGoWheel(self, looker, side):
        if side == 'right':
            self._workspace.set_entity_property_value(looker, 'CharacterHandAttachmentComponent','right_hand_config.locator_entity_id', anyverse_platform.invalid_entity_id)
        if side == 'left':
            self._workspace.set_entity_property_value(looker, 'CharacterHandAttachmentComponent','left_hand_config.locator_entity_id', anyverse_platform.invalid_entity_id)

    #_______________________________________________________________
    def LookAtRearSeat(self, looker, the_car, side):
        seat_number = '01'
        if side == 'right':
            seat_number = '05'
            self.letGoWheel(looker, side)
            animation, weight = self.selectAdultAnimation('right_arm', 0.25, 0.5, 'above_the_head_r')
            self.setAnimation('right_arm', animation, weight, looker)
        elif side == 'left':
            seat_number = '03'
            animation, weight = self.selectAdultAnimation('right_arm', 0.25, 0.35, 'above_the_head_r')
            self.setAnimation('right_arm', animation, weight, looker)

        # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0, 1, 'leaning_forward')
        self.setAnimation('spine', animation, weight, looker)

        seat_locators = [ ent for ent in self.getSeatLocators(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'seat'+seat_number in self._workspace.get_entity_name(ent).lower() ]
        if len(seat_locators) > 0:
            seat_loc = seat_locators[0]
        else:
            seat_loc = anyverse_platform.invalid_entity_id

        return self.LookAtLocator(looker, seat_loc)

    #_______________________________________________________________
    def LookAtOtherCharacter(self, looker, looked_at):
        looked_at_name = self._workspace.get_entity_name(looked_at)

        if looked_at != anyverse_platform.invalid_entity_id and 'rp_' in looked_at_name:
            char_locators = [ ent for ent in self._workspace.get_hierarchy(looked_at) if self._workspace.get_entity_type(ent) == 'Locator' ]
            if len(char_locators) >= 1:
                lookat_locator = char_locators[0]
            else:
                lookat_locator = self.getParent(looked_at)
        else:
            lookat_locator = self.getParent(looked_at)

        return self.LookAtLocator(looker, lookat_locator)

    #_______________________________________________________________
    def LookAtInsideRearViewMirror(self, looker, the_car):
        rvm_inside_locator = self.getRVMLocator(the_car, 'inside')

        return self.LookAtLocator(looker, rvm_inside_locator)

    #_______________________________________________________________
    def LookAtExteriorRearViewMirror(self, looker, the_car, side):
        rvm_locator = self.getRVMLocator(the_car, side)

        return self.LookAtLocator(looker, rvm_locator)

    #_______________________________________________________________
    def LookAtHeadrest(self, looker, the_car, side):
        headrest_locator = self.getHeadrestLocator(the_car, side)

        return self.LookAtLocator(looker, headrest_locator)

    #_______________________________________________________________
    def LookAtSeatbelt(self, looker, the_car, side):
        seatbelt_locator = self.getSeatbeltLocator(the_car, side)

        return self.LookAtLocator(looker, seatbelt_locator)

    #_______________________________________________________________
    def LookAtFloor(self, looker, the_car, side):
        floor_locator = self.getFloorLocator(the_car, side)

        return self.LookAtLocator(looker, floor_locator)

    #_______________________________________________________________
    def LookAtInfotainment(self, looker, the_car):
        cc_locator = self.getCCLocator(the_car)

        return self.LookAtLocator(looker, cc_locator)

    #_______________________________________________________________
    def LookAtGloveCompartment(self, looker, the_car):
        glove_locator = self.getGloveCompLocator(the_car)

        return self.LookAtLocator(looker, glove_locator)

    #_______________________________________________________________
    def LookAtLocator(self, looker, locator):
        locator_name = self._workspace.get_entity_name(locator)
        type = None
        try:
            type = self._workspace.get_entity_type(locator)
        except:
            print('[ERROR] locator {} does not exist.'.format(locator_name))
        if type == 'Locator':
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 3)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', locator)
        elif type is not None:
            print('[WARN] {} ({}) not a locator.'.format(locator_name, locator))
        return locator_name

    #_______________________________________________________________
    def setFaceExpression(self, character_id, eyes_position, eyelids_position, eyebrows_positions, mouth_positions, jaw_position):
        has_face_control = self._workspace.has_entity_component(character_id,'CharacterFaceControlComponent')
        if has_face_control:
            # Set eyes positions. Both the same positions. It is a Vector3D, z coordinate is always 0 x and y are [-0.13, 0.13]
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eye_l_ctrl',eyes_position)
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eye_r_ctrl',eyes_position)

            # Set eye lids positions. They can be different. It is a duple. [0] for left eye and [1] for right eye
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eyelid_left_control.control_value', eyelids_position[0])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eyelid_right_control.control_value', eyelids_position[1])

            # Set eye brows positions. They can be different. It is a duple. [0] for left eyebrow and [1] for right eyebrow
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eyebrow_left_control.control_value', eyebrows_positions[0])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','eyebrow_right_control.control_value', eyebrows_positions[1])

            # Set mouth positions. It is a 4-tuple, 2 for the left side([0], [1]) and 2 for the right side ([2], [3])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','mouth_left_control.control_value_x', mouth_positions[0])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','mouth_left_control.control_value_y', mouth_positions[1])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','mouth_right_control.control_value_x', mouth_positions[2])
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','mouth_right_control.control_value_y', mouth_positions[3])

            # Set jaw position. It is a number between 0 and 1. 0 = open, 1 = close
            self._workspace.set_entity_property_value(character_id,'CharacterFaceControlComponent','jaw_control.control_value', jaw_position)
        else:
            print('[WARN] Character {} does not have face controls'.format(self._workspace.get_entity_name(character_id)))

    #_______________________________________________________________
    def setNamedFaceExpression(self, character_id, expression_code):
        if expression_code == 0: # neutral
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (1, 1)
            eyebrows_positions = (0.5, 0.5)
            mouth_positions = (0.6, 0.6, 0.6, 0.6)
            jaw_position = 1
        elif expression_code == 1: # happy
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (0.72, 0.72)
            eyebrows_positions = (0.81, 0.81)
            mouth_positions = (0.71, 0.71, 0.71, 0.71)
            jaw_position = 0.55
        elif expression_code == 2: # sad
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (0.72, 0.72)
            eyebrows_positions = (0.81, 0.81)
            mouth_positions = (0.2, 0.0, 0.2, 0.0)
            jaw_position = 1
        elif expression_code == 3: # angry
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (0.7, 0.7)
            eyebrows_positions = (0, 0)
            mouth_positions = (0.32, 0.18, 0.32, 0.18)
            jaw_position = 1
        elif expression_code == 4: # surprised
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (0.99, 0.99)
            eyebrows_positions = (0.99, 0.99)
            mouth_positions = (0.3, 0, 0.3, 0)
            jaw_position = 0
        elif expression_code == 5: # random
            eyes_position = anyverse_platform.Vector3D(random.uniform(-0.13, 0.13), random.uniform(-0.13, 0.13), random.uniform(-0.13, 0.13))
            eyelids_position = (random.uniform(0, 1), random.uniform(0, 1))
            eyebrows_positions = (random.uniform(0, 1), random.uniform(0, 1))
            mouth_positions = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
            jaw_position = random.uniform(0, 1)
        else: # neutral
            eyes_position = anyverse_platform.Vector3D(0, 0, 0)
            eyelids_position = (1, 1)
            eyebrows_positions = (0.5, 0.5)
            mouth_positions = (0.6, 0.6, 0.6, 0.6)
            jaw_position = 1

        self.setFaceExpression(character_id, eyes_position, eyelids_position, eyebrows_positions, mouth_positions, jaw_position)
