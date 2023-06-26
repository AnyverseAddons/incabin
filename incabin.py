import anyverse_platform
import city_builder
import json
import csv
import random
import re
import sys
import anyverseaux as aux

class InCabinUtils:
    def __init__(self, workspace, script_console, iteration_index = None):
        self._iteration_index = iteration_index
        self._workspace = workspace
        self._no_entry = anyverse_platform.invalid_entity_id
        self._ego_id = self._workspace.get_entities_by_name("Ego")[0]
        self._already_used_characters = []
        self._car_brand = ""
        self._car_model = ""
        self._clip_asset_name = "ConvertibleChildSeat_ClipOn"
        self._car_color_schemes = ['black', 'brown', 'darkgrey', 'lightgrey']
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
            }

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
        entity_name = self._workspace.get_entity_name(entity_id)
        # print('Deleting all entities under {}'.format(entity_name))
        # descendant_fixed_entities_list = self.vectorToList(self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity))
        descendant_fixed_entities_list = [ fe for fe in self._workspace.get_hierarchy(entity_id) if 'FixedEntity' == self._workspace.get_entity_type(fe) ]
        descendant_fixed_entities_list.reverse()

        for fixed_entity_id in descendant_fixed_entities_list:
            fixed_entity_name = self._workspace.get_entity_name(fixed_entity_id)
            if fixed_entity_name != entity_name:
                # print('Deleting entity {}'.format(fixed_entity_name))
                self._workspace.delete_entity(fixed_entity_id)

    #_______________________________________________________________
    def getCameraDelta(self, center, interval, normal = True):
        if normal:
            mu, sigma = center, interval/3.6
            delta = random.normalvariate(mu, sigma)
        else:
            delta = random.uniform(center - interval,center + interval)

        return delta

    #_______________________________________________________________
    def isVisible(self, entityId):
        return self._workspace.get_entity_property_value(entityId, 'VisibleComponent','visible')

    #_______________________________________________________________
    def setCustomMetadata(self, entityId, key, value):
        old_metadata = self._workspace.get_entity_property_value(entityId, 'UserMetadataComponent','json_metadata')
        if not old_metadata:
            old_metadata = "{}"
        metadata_dict = json.loads(old_metadata)
        metadata_dict[key] = value
        new_metadata = json.dumps(metadata_dict)
        self._workspace.set_entity_property_value(entityId, 'UserMetadataComponent','json_metadata', new_metadata)

    #_______________________________________________________________
    def hasCustomMetadata(self, entity_id):
        ret = False
        try:
            custom_metadata = json.loads(self._workspace.get_entity_property_value(entity_id, 'UserMetadataComponent','json_metadata'))
        except json.decoder.JSONDecodeError as jde:
            ret = False
            custom_metadata = None
        if isinstance(custom_metadata, dict):
            ret = True

        return ret

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
    def setAvoidArmsAutoCollision(self, entity_id):
        self._workspace.set_entity_property_value(entity_id, 'CharacterBodyRestrictionsComponent','avoid_arms_auto_collision', True)

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
            if self._workspace.get_entity_name(anim) == anim_name:
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
    def applyCharacterOffset(self, character):
        position = self._workspace.get_entity_property_value(character['Entity_id'], 'RelativeTransformToComponent','position')
        position.z += float(character['root_offset'].replace(',','.'))/100
        self._workspace.set_entity_property_value(character['Entity_id'], 'RelativeTransformToComponent','position', position)
    #_______________________________________________________________
    # def applyCharacterOffset(self, character):
    #     # Apply the  offset to the locator instead of the character
    #     parent_id = self.getParent(character['Entity_id'])
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
            print('Character too short, not seat belt...')
            return ret

        if belt_on_probability == None:
            belt_on_probability = 0.5
        if random.uniform(0,1) < belt_on_probability:
            ret = True
        return ret

    #_______________________________________________________________
    def doNothing(self, seat_locator):
        print('Leaving seat {} empty'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))

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
            baby_characters = self.filterCharacters(babies, key, value)
        else:
            baby_characters = self.filterCharacters(babies, 'name', name)
        
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

        baby_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, baby["resource_id"])

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
            character_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, character["resource_id"])
            print('Selected character: {}'.format(character['resource_name']))
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
        print('Selected character: {}'.format(character['resource_name']))
        for character_asset in character_assets:
            if character['resource_name'] in character_asset.name and '_OP' in character_asset.name:
                ret = character
                break
            if 'baby' in character['resource_name'].lower():
                break
        return ret

    #_______________________________________________________________
    def selectObject(self, name = None, version = None, big_object = None):
        objects = self._workspace.objects

        if name == None:
            if big_object == None:
                picked_object = objects[random.randrange(len(objects))]
            elif big_object:
                big_objects = [ o for o in objects if 'big_object' in o and o['big_object']  ]
                picked_object = big_objects[random.randrange(len(big_objects))]
            else:
                small_objects = [ o for o in objects if 'big_object' in o and not o['big_object']]
                picked_object = small_objects[random.randrange(len(small_objects))]
        else:
            for idx, object in enumerate(objects):
                if name == object['name'] and version == object['version']:
                    picked_object = objects[idx]
                    break

        object_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_object["resource_id"])
        picked_object['Asset_id'] = object_asset_id
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

            print('Picked Accessory: {}'.format(picked_accessory["resource_name"]))
            object_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_accessory["resource_id"])
            picked_accessory['Asset_id'] = object_asset_id
        else:
            picked_accessory = {}
            picked_accessory['Asset_id'] = -1

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


        character_id = character['Entity_id']
        can_glasses, can_cap, can_hat, can_mask = character['glasses'], character['cap'], character['hat'], character['facemask']
        can_headwear = can_cap or can_hat

        accessories_locators = self.getEntityLocators(character_id)

        if not zero_probs:
            if can_glasses:
                put_glasses = True if random.uniform(0,1) < glasses_prob else False
                if put_glasses:
                    glasses = self.selectHumanAccessory('class', ['Sunglasses', 'Glasses'])
                    glasses_locs = [ gl for gl in accessories_locators if 'glasses' in self._workspace.get_entity_name(gl).lower() ]
                    if len(glasses_locs) > 0 and glasses['Asset_id'] != -1:
                        glasses_loc = glasses_locs[0]
                        glasses_id = self._workspace.create_fixed_entity(glasses['resource_name'], glasses_loc, glasses['Asset_id'])
                        glasses['Entity_id'] = glasses_id
                        glasses['Character'] = character['resource_name']
                        self.setInstanceIfPossible(glasses_id, False)
                        self.setExportAlwaysExcludeOcclusion(glasses_id)
                        self.setAccessoryInfo(glasses)
                        ret.append(glasses)
                    else:
                        print('[ERROR] Could NOT find accessories of class Sunglasses or Glasses')
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
                    if len(hat_locs) > 0 and hat['Asset_id'] != -1:
                        hat_loc = hat_locs[0]
                        hat_id = self._workspace.create_fixed_entity(hat['resource_name'], hat_loc, hat['Asset_id'])
                        hat['Entity_id'] = hat_id
                        hat['Character'] = character['resource_name']
                        self.setInstanceIfPossible(hat_id, False)
                        self.setExportAlwaysExcludeOcclusion(hat_id)
                        self.setAccessoryInfo(hat)
                        ret.append(hat)
                    else:
                        print('[ERROR] Could NOT find accessories of class Hat or Baseball_cap')
            if can_mask:
                put_mask = True if random.uniform(0,1) < mask_prob else False
                if put_mask:
                    mask = self.selectHumanAccessory('class', ['Facemask'])
                    mask_locs = [ ml for ml in accessories_locators if 'facemask' in self._workspace.get_entity_name(ml).lower() ]
                    if len(mask_locs) > 0 and mask['Asset_id'] != -1:
                        mask_loc = mask_locs[0]
                        mask_id = self._workspace.create_fixed_entity(mask['resource_name'], mask_loc, mask['Asset_id'])
                        mask['Entity_id'] = mask_id
                        mask['Character'] = character['resource_name']
                        self.setInstanceIfPossible(mask_id, False)
                        self.setExportAlwaysExcludeOcclusion(mask_id)
                        self.setAccessoryInfo(mask)
                        ret.append(mask)
                    else:
                        print('[ERROR] Could NOT find accessories of class Facemask')

        return ret

    #_______________________________________________________________
    def placeObjectOnCharacter(self, seat_locator, character_id, name = None, version = None):
        print('Placing object on {}'.format(self._workspace.get_entity_name(character_id)))

        big_object = False

        # select a named object from resoures
        object = self.selectObject(name, version, big_object)
        print('Object to place {}'.format(object['resource_name']))
        if object['Asset_id'] != -1:
            # Create the object fixed entity
            object_entity_id = self._workspace.create_fixed_entity(object['resource_name']+'_'+object['Version'], seat_locator, object['Asset_id'])
            scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))
            if scale_factor != 1:
                print('Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['Entity_id'] = object_entity_id

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
            # self._workspace.placement.place_entity_on_entities(object_entity_id, port_entities, landing_region_id, -1, True, False, 30)
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
    def placeObjectInChildseat(self, seat_locator, childseat, name = None, version = None):
        seat_id = childseat['Entity_id']
        print('Placing object on {}'.format(self._workspace.get_entity_name(seat_id)))

        big_object = False

        # select a named object from resoures
        object = self.selectObject(name, version, big_object)
        print('Object to place {}'.format(object['resource_name']))
        if object['Asset_id'] != -1:
            # Create the object fixed entity
            try:
                object_entity_id = self._workspace.create_fixed_entity(object['resource_name']+'_'+object['version'], seat_locator, object['Asset_id'])
                scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))
            except KeyError as ke:
                print('[WARN] wrong asset {}: {}'.format(object['resource_name'], ke))
                scale_factor = -1

            if scale_factor != 1:
                print('Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['Entity_id'] = object_entity_id
            is_animal = True if object['class'].lower() == 'dog' else False

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
            object['Face'] = ''
            self.setObjectInfo(object)
            self.setSeatInfo(object)
            object['Accessory'] = 'None'

            # Overwriting seat info to update occupancy
            # HACK: We don't need to update this in case of objects since it is not considered occupied 
            # self.setChildseatInfo(childseat)
            # self.setSeatInfo(childseat)

        else:
            # No matching objects found returning id -1
            object_entity_id = -1
            object = None

        return object

    #_______________________________________________________________
    def placeObjectOnSeat(self, seat_locator, seat_id, name = None, version = None):
        print('Placing object on {}'.format(self._workspace.get_entity_name(seat_id)))

        big_object = True if random.uniform(0,1) >= 0.5 else False

        # select a named object from resources
        object = self.selectObject(name, version, big_object)
        print('Object to place {}'.format(object['resource_name']))
        if object['Asset_id'] != -1:
            # Create the object fixed entity
            try:
                object_entity_id = self._workspace.create_fixed_entity(object['resource_name']+'_'+object['version'], seat_locator, object['Asset_id'])
                scale_factor = random.uniform(float(object['min_scale']), float(object['max_scale']))
            except KeyError as ke:
                print('[WARN] wrong asset {}: {}'.format(object['resource_name'], ke))
                scale_factor = -1

            if scale_factor != 1:
                print('Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['Entity_id'] = object_entity_id
            is_animal = True if object['class'].lower() == 'dog' else False

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
            object['Face'] = ''
            self.setObjectInfo(object)
            self.setSeatInfo(object)
            object['Accessory'] = 'None'

            if self.isChildseatLocator(seat_locator):
                self.setChildseatInfo(childseat)
                self.setSeatInfo(childseat)

        else:
            # No matching objects found returning id -1
            object_entity_id = -1
            object = None

        return object

    #_______________________________________________________________
    def placeObject(self, seat_locator, name = None, version = None):
        print('Placing object in {}'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))

        big_object = True if random.uniform(0,1) >= 0.5 else False

        print('Big object: {}'.format(big_object))

        # select a random object from resoures
        object = self.selectObject(name, version, big_object)
        print('Object to place {}'.format(object['resource_name']))
        if object['Asset_id'] != -1:
            # Create the object fixed entity
            object_entity_id = self._workspace.create_fixed_entity(object['resource_name'], seat_locator, object['Asset_id'])
            scale_factor = random.uniform(0.9, 1.1)
            if scale_factor != 1:
                print('Rescaling object to {}'.format(round(scale_factor, 2)))
                self.scaleEntity(object_entity_id,round(scale_factor, 2))
            object['Entity_id'] = object_entity_id

            # Delete existing region if it exists
            existing_landing_region = self._workspace.get_entities_by_name('landing_region')
            if len(existing_landing_region) > 0:
                self._workspace.delete_entity(existing_landing_region[0])

            # Create a reagion around the seat locator. Default 1x1x1 meters
            landing_region_id = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Region, 'landing_region', seat_locator)

            # Resize the region to fit the seat
            if self.isMiddleBackSeat(seat_locator):
                width = 0.25
                depth = 0.35
                pos_offset_y = 0.0
            elif self.isRightBackSeat(seat_locator):
                width = 0.4
                depth = 0.5
                pos_offset_y = 0.1
            elif self.isLeftBackSeat(seat_locator):
                width = 0.4
                depth = 0.5
                pos_offset_y = -0.1
            else:
                width = 0.5
                depth = 0.5
                pos_offset_y = 0
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','width', width)
            # self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','height', 0.7)
            self._workspace.set_entity_property_value(landing_region_id, 'RegionComponent','depth', depth)

            # Apply position offset to separate from the back of the seat to avoid "flying" objects
            pos_offset_x = 0.1
            landing_region_pos = self._workspace.get_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position')
            landing_region_pos.x += pos_offset_x
            landing_region_pos.y += pos_offset_y
            self._workspace.set_entity_property_value(landing_region_id, 'RelativeTransformToComponent','position',landing_region_pos)

            # Get the car id and insert it in the set of port entities
            # The car is goign to be the only one for the time being
            the_car = self._workspace.get_entities_by_name('The_Car')[0]
            port_entities = city_builder.core.EntitySet()
            port_entities.insert(the_car)

            # place the object in the in the region and land it in the car seat
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
    def placeDriver(self, seat_locator, name = None, seatbelts_distribution = None, accessories_probabilities = None, gaze_probabilities = None, expression_probabilities = None):
        print('Placing Driver in {}'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))

        # select a random adult character
        driver_asset_id, driver = self.selectCharacter('kind','Adult', name)
        if driver_asset_id != -1:
            driver_id = self._workspace.create_fixed_entity(driver['name'], seat_locator, driver_asset_id)

            driver['Entity_id'] = driver_id

            # set driver pose
            animation = self.getAnimIdByName('Driving')
            self.setAnimation('base', animation, 1.0, driver_id)
            # Grab the steering wheel by default
            self.grabSteeringWheel(driver_id)

            # setting spine animation
            max_weight = 1
            animation, weight = self.selectAdultAnimation('spine', 0, max_weight)
            spine_animation_name = self._workspace.get_entity_name(animation)
            if 'side_ward' in spine_animation_name and weight > 0.4:
                weight = 0.4

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
                # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
                self.setAnimation(arms[arm], animation, weight, driver_id)
                if arm == 1 and 'above' not in self._workspace.get_entity_name(animation):
                    # HACK: Avoid reaching RVM if camera is placed there
                    rvm_cams_visible = [ c for c in self.getVisibleCameras() if 'RVM' in c]
                    if len(rvm_cams_visible) > 0:
                        reach = self.reachInfotainment(driver_id, 'right') if random.uniform(0,1) <= 0.5 else 'Nothing'
                    else:
                        reach = self.reachRVM(driver_id, 'right') if random.uniform(0,1) <= 0.5 else self.reachInfotainment(driver_id, 'right')
                    print('[DRIVER ARM] Driver reaching {}'.format(reach))                

            # setting head animation
            # we cannot set the driver gaze here in case it has to look at the passenger that is not there yet 
            animation, weight = self.selectAdultAnimation('head', 0, 1)
            # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
            self.setAnimation('head', animation, weight, driver_id)

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
                print('Placing accessories...')
                accessories = self.placeAccessories(driver, accessories_probabilities)

                if len(accessories) == 0:
                    print('Cannot place any accessory to {}'.format(driver['name']))
                for accessory in accessories:
                    print('Placed {} on driver {}'.format(accessory['class'], driver['name']))
                    accessory['Character'] = driver['name']
                    driver['Accessory'] = accessory['class']+'.'+accessory['name'] if driver['Accessory'] == 'None' else driver['Accessory'] + '|' + accessory['class']+'.'+accessory['name']
                    self.setAccessoryInfo(accessory)
            else:
                print('Not placing accessories for driver {}'.format(driver['name']))
            
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
                driver['Seatbelt_placement'] = belt_placement

            self.setExportAlwaysExcludeOcclusion(driver_id)
            self.setAvoidArmsAutoCollision(driver_id)
            self.removeMotionBlur(driver_id)
            self.applyCharacterOffset(driver)
            self.setCharacterInfo(driver)
            self.setCharacterPoseInfo(driver)
            self.setSeatInfo(driver)

            self._already_used_characters.append(driver['name'])
        else:
            # No matching drivers found returning id -1
            if driver != None:
                driver['Entity_id'] = driver_asset_id
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
        if key == 'kind' and value == 'Convertible' and orientation is not None:
            filtered_childseats = [ cs for cs in filtered_childseats if cs['aim looking'].lower() == orientation.lower() ]

        # pick one randomly
        if len(filtered_childseats) > 0:
            childseat_idx = random.randrange(len(filtered_childseats))
            childseat = filtered_childseats[childseat_idx]
            # Pick the only possible asset and set the orientation from the childseat dictionary
            childseat['Orientation'] = childseat['aim looking']
            childseat_asset_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, childseat["resource_id"])
        else:
            childseat_asset_id = -1
            childseat = None

        return childseat_asset_id, childseat

    #_______________________________________________________________
    def placeChildseat(self, seat_locator, childseat_config, name = None, only_baby_in_copilot = True):
        childseat_type_probabilities = childseat_config['childseat_type_probabilities']
        childseat_orientation_probabilities = childseat_config['childseat_orientation_probabilities']
        childseat_probabilities = [ float(t['probability']) for t in childseat_type_probabilities ]
        orientation_probabilities = [ float(t['probability']) for t in childseat_orientation_probabilities ]
        max_rotation = childseat_config['childseat_rotation_max']

        # Only baby child seat in copilot front seat
        if self.isCopilotSeat(seat_locator) and only_baby_in_copilot:
            childseat_type_idx = 0
        elif self.isMiddleBackSeat(seat_locator):
            childseat_type_idx = 2
        else:
            childseat_type_idx = self.choiceUsingProbabilities(childseat_probabilities)

        childseat_type = childseat_type_probabilities[childseat_type_idx]['Type']
        orientation = None
        # select a random childseat of the given type and orientation
        if childseat_type == 'BabyChild':
            orientation_idx = self.choiceUsingProbabilities(orientation_probabilities)
            orientation = childseat_orientation_probabilities[orientation_idx]['Orientation']
            childseat_asset_id, childseat = self.selectChildseat('kind',childseat_type, 'Backward', name)
        else:
            orientation = 'Forward'
            childseat_asset_id, childseat = self.selectChildseat('kind',childseat_type, orientation, name)

        if childseat_asset_id != -1:
            childseat_id = self._workspace.create_fixed_entity(childseat['resource_name'], seat_locator, childseat_asset_id)
            childseat['Entity_id'] = childseat_id
            print('Placing Childseat {} in {}'.format(childseat['name'], self._workspace.get_entity_name(seat_locator).split('_')[0]))

            mu, sigma = 0, max_rotation/3.6
            yaw = random.normalvariate(mu, sigma)
            if childseat_type == 'BabyChild' and orientation == 'Forward':
                childseat['Orientation']  = orientation
                yaw += 180
                pos = self._workspace.get_entity_property_value(childseat_id,'RelativeTransformToComponent','position')
                pos.x += 0.65
                self._workspace.set_entity_property_value(childseat_id,'RelativeTransformToComponent','position', pos)
            print('[INFO] Rotating childseat {:.2f}º'.format(yaw))
            self.wiggleChildseatRandom(childseat_id, yaw , pitch = 0)

            self.setExportAlwaysExcludeOcclusion(childseat_id)
            self.setChildseatInfo(childseat)
            self.setSeatInfo(childseat)

            self._already_used_characters.append(childseat['name'])
        else:
            print('[WARN]: Could not find a {} childseat with orientation {}'.format(childseat_type, orientation))

        return childseat

    #_______________________________________________________________
    def placeBabyInChildseat(self, childseat, seat_locator, name = None):
        for_backseat = False
        if self.isLeftBackSeat(seat_locator) or self.isRightBackSeat(seat_locator):
            for_backseat = True

        baby_asset_id, baby = self.selectBaby('suitableseat','BabyChild', for_backseat, name)
        print('Placing baby {} in childseat {}'.format(baby['name'], self._workspace.get_entity_name(childseat['Entity_id'])))

        # get the childseat locator
        childseat_locator = self.getEntityLocators(childseat['Entity_id'])[0]
        if baby_asset_id != -1:
            baby_id = self._workspace.create_fixed_entity(baby['name'], childseat_locator, baby_asset_id)
        else:
            # No matching children found returning id -1
            print('[ERROR]: could not find suitable baby for childseat')
            baby_id = -1

        baby['Entity_id'] = baby_id
        # Babies never have seatbelts. Set it to False for annotations
        baby['Seatbelt_on'] = False

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
        self._already_used_characters.append(baby['name'])

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
                print('Child {} not suitable for chilsseat {}. Trying a different one...'.format(child['name'], childseat['name']))

        print('Placing child {} in childseat {}'.format(child['name'], self._workspace.get_entity_name(childseat['Entity_id'])))

        # get the childseat locator
        childseat_locator = self.getEntityLocators(childseat['Entity_id'])[0]
        if child_asset_id != -1:
            child_id = self._workspace.create_fixed_entity(child['name'], childseat_locator, child_asset_id)
        else:
            # No matching children found returning id -1
            print('[ERROR]: could not find suitable child for childseat')
            child_id = -1

        child['Entity_id'] = child_id

        # Decide if we fasten the seat belt or not
        # Never fasten seatbelt if it's a big baby or if the convertible backwards
        # For the other children in convertibles we always fasten the seatbelts to have a 50/50
        # considering the re are 4 big babies and 4 children characters suitable for convertibles.
        # Fastening seat belts affect what base animation we set: only sitting straight when seat belts fastened
        if 'Baby' in child['name'] or childseat['Orientation'] == 'Backward':
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
            # Set spine animation. HACK: Limit the weight when leaning backward or sideward and don't allow to look up
            animation, weight = self.selectChildAnimation(seat_locator, 'spine', 0, 1)
            not_look_up = False
            max_weight = 0
            if 'backward' in self._workspace.get_entity_name(animation) or 'side' in self._workspace.get_entity_name(animation):
                not_look_up = True
                max_weight = 0.3 if 'backward' in self._workspace.get_entity_name(animation) else 0.4
                if weight > max_weight:
                    weight = max_weight
            self.setAnimation('spine', animation, weight, child_id)
            # Set arms animation
            if self.isCopilotSeat(seat_locator) or self.isRightBackSeat(seat_locator):
                animate_left_arm = True if random.uniform(0,1) < 0.2 else False
                animate_right_arm = True if random.uniform(0,1) < 0.5 else False
                left_arm_max_weight = 0.6
                right_arm_max_weight = 0.6
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
                # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
                self.setAnimation(arm, animation, weight, child_id)
            # Animate right arm
            if animate_right_arm:
                arm = 'right_arm'
                animation, weight = self.selectChildAnimation(seat_locator, arm, arms_min_weight, right_arm_max_weight)
                # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
                self.setAnimation(arm, animation, weight, child_id)

            # setting head animation
            animation, weight = self.selectChildAnimation(seat_locator, 'head', 0, 1)
            # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
            # HACK: Limit the weight to look up if not_look_up (leaning backwards) 
            if 'Up' in self._workspace.get_entity_name(animation) and not_look_up:
                if weight > 0.35:
                    weight = 0.35
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
                print('Setting seat belt for booster...')
                belt_placement = self.createBeltFor(self.getSeatPos(seat_locator), child_id, self._car_brand, self._car_model, seatbelts_distribution)
                child['Seatbelt_placement'] = belt_placement

        if childseat['kind'] == 'Convertible':
            if fasten_seatbelt and not self._script_console:
                print('Setting child seat belt for child {}'.format(child['name']))
                self.createChildBelt( child_id, childseat['Entity_id'], self._clip_asset, self.getSeatPos(seat_locator), None )
                child['Seatbelt_placement'] = 'Normal'

        self.setExportAlwaysExcludeOcclusion(child_id)
        self.setAvoidArmsAutoCollision(child_id)
        self.removeMotionBlur(child_id)
        self.setCharacterInfo(child)
        self.setSeatInfo(child)

        # Because of the occupancy we have to overwrite the child seat custom metadata
        self.setChildseatInfo(childseat)
        self.setSeatInfo(childseat)

        self._already_used_characters.append(child['name'])

        return child

    #_______________________________________________________________
    def placePassenger(self, seat_locator, name = None, seatbelts_distribution = None, accessories_probabilities = None, gaze_probabilities = None, expression_probabilities = None):
        print('Placing Passenger in {} ({})'.format(self._workspace.get_entity_name(seat_locator).split('_')[0], seat_locator))
        # select a random adult character
        # select a random childseat of the given type
        passenger_found = False
        stop_searching = False
        while not passenger_found and not stop_searching:
            passenger_asset_id, passenger = self.selectCharacter('kind','Adult', name)
            if passenger_asset_id != -1:
                passenger_id = self._workspace.create_fixed_entity(passenger['resource_name'], seat_locator, passenger_asset_id)
                passenger_found = True
            else:
                # No matching passengers found returning id -1
                if passenger == None:
                    print('[ERROR]: Could not find valid passenger to place')
                    stop_searching = True
                else:
                    print('[ERROR]: Could not find a passenger {} to place. Trying another one...'.format(passenger['name']))
                passenger_id = -1

        body_min_weight = 0
        body_max_weight = 1

        if passenger_found:
            passenger['Entity_id'] = passenger_id

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

            # setting spine animation
            if self.isCopilotSeat(seat_locator):
                max_weight = 1
            else:
                max_weight = 0.5
            animation, weight = self.selectAdultAnimation('spine', 0, max_weight)
            spine_animation_name = self._workspace.get_entity_name(animation)

            self.setAnimation('spine', animation, weight, passenger_id)

            # Set arms animation: only if not arms on the body
            animate_left_arm, animate_right_arm = True, True
            if base_animation_name == 'Arms_on_the_body':
                animate_left_arm, animate_right_arm = False, False
        
            if self.isCopilotSeat(seat_locator) or self.isRightBackSeat(seat_locator):
                left_arm_max_weight = 0.65
                right_arm_max_weight = 1.0
            if  self.isLeftBackSeat(seat_locator) or self.isMiddleBackSeat:
                left_arm_max_weight = 1.0
                right_arm_max_weight = 0.2

            arms_min_weight = 0.2
            if animate_left_arm:
                arm = 'left_arm'
                animation, weight = self.selectAdultAnimation(arm, 0.35, left_arm_max_weight) # left arm min weight enough to avoid seatbelt collision
                self.setAnimation(arm, animation, weight, passenger_id)
                if 'above' not in self._workspace.get_entity_name(animation):
                    reach = self.reachInfotainment(passenger_id, 'left') if random.uniform(0,1) <= 0.5 else 'Nothing'
                    print('[PASSENGER ARM] Passenger reaching {}'.format(reach))
            # Animate right arm
            if animate_right_arm:
                arm = 'right_arm'
                animation, weight = self.selectAdultAnimation(arm, arms_min_weight, right_arm_max_weight)
                # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
                self.setAnimation(arm, animation, weight, passenger_id)

            # setting head animation
            # Don't move the copilot head. Controled by gaze if there are gaze settings
            if (self.isCopilotSeat(seat_locator) and gaze_probabilities is not None):
                self.setPassengerGaze(gaze_probabilities)
            else:
                animation, weight = self.selectAdultAnimation('head', 0, 0.8)
                # print('Setting animation: {}, weight: {}'.format(self._workspace.get_entity_name(animation), weight))
                self.setAnimation('head', animation, weight, passenger_id)

            # Place accessories on the passenger according to external probabilities
            if accessories_probabilities != None:
                place_accessories = True if random.uniform(0,1) < accessories_probabilities['global'] else False
            else:
                place_accessories = False

            accessories = []
            passenger['Accessory'] = 'None'
            if place_accessories:
                print('Placing accessories...')
                accessories = self.placeAccessories(passenger, accessories_probabilities)

                if len(accessories) == 0:
                    print('Cannnot place any accessory to {}'.format(passenger['name']))
                for accessory in accessories:
                    accessory['Character'] = passenger['name']
                    passenger['Accessory'] = accessory['class']+'.'+accessory['name'] if passenger['Accessory'] == 'None' else passenger['Accessory'] + '|' + accessory['class']+'.'+accessory['name']
                    self.setAccessoryInfo(accessory)
            else:
                print('Not placing accessories for passenger {}'.format(passenger['name']))

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
                if belt_placement == 'CharacterOverSeatbelt' and passenger['kind'] == 'Child':
                    pass_pos = self._workspace.get_entity_property_value(passenger_id, 'RelativeTransformToComponent', 'position')
                    pass_pos.x += 0.07
                    self._workspace.set_entity_property_value(passenger_id, 'RelativeTransformToComponent', 'position', pass_pos)
                passenger['Seatbelt_placement'] = belt_placement

            self.setExportAlwaysExcludeOcclusion(passenger_id)
            self.setAvoidArmsAutoCollision(passenger_id)
            self.removeMotionBlur(passenger_id)
            self.applyCharacterOffset(passenger)
            self.setCharacterInfo(passenger)
            self.setCharacterPoseInfo(passenger)
            self.setSeatInfo(passenger)

            self._already_used_characters.append(passenger['name'])

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
        print('Occupied({}): {}'.format(occupants,ret))
        return ret

    #_______________________________________________________________
    def setChildseatInfo(self, childseat):
        childseat_name = childseat['name']

        childseat_info = {}
        childseat_info["type"] = childseat['kind']
        childseat_info["brand"] = childseat["brand"]
        childseat_info["orientation"] = childseat['Orientation']
        occupied = self.isChildseatOccupied(childseat['Entity_id'])
        childseat_info["occupied"] = occupied
        occupant_name = ''
        if occupied:
            descendants = [ e for e in self._workspace.get_hierarchy(childseat['Entity_id']) if e != childseat['Entity_id'] and self._workspace.get_entity_type(e) == 'FixedEntity' ]
            occupant_name = self._workspace.get_entity_name(descendants[0]) if len(descendants) > 0 else ''
        childseat_info["occupant"] = occupant_name

        self.setCustomMetadata(childseat['Entity_id'], "ChildseatInfo", childseat_info)

        return childseat_info

    #_______________________________________________________________
    def isChildseatLocator(self, locator_id):
        return self._workspace.get_entity_name(locator_id).lower() == 'childseat_locator' or self._workspace.get_entity_name(locator_id).lower() == 'babychildseat_locator' or self._workspace.get_entity_name(locator_id).lower() == 'child_locator'

    #_______________________________________________________________
    def setSeatInfo(self, character):
        parent_id = self.getParent(character['Entity_id'])
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
            print('It is a child seat, no seatbelt_on info')

        self.setCustomMetadata(character['Entity_id'], "Seat", seat_info)

        return seat_info

    #_______________________________________________________________
    def setAccessoryInfo(self, accessory):
        accessory_info = {}
        accessory_info["character"] = accessory['Character']

        self.setCustomMetadata(accessory['Entity_id'], "person", accessory_info)

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
        base_animation_entity_id = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','base_anim_config.animation_entity_id')
        if base_animation_entity_id == self._no_entry:
            base_pose = 'none'
            base_pose_weight = 1.0
        else:
            base_pose = self._workspace.get_entity_property_value(base_animation_entity_id,'WorkspaceEntityComponent','name')
            base_pose_weight = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','base_anim_config.weight')

        spine_animation_entity_id = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','spine_anim_config.animation_entity_id')
        if spine_animation_entity_id == self._no_entry:
            spine_pose = 'none'
            spine_pose_weight = 1.0
        else:
            spine_pose = self._workspace.get_entity_property_value(spine_animation_entity_id,'WorkspaceEntityComponent','name')
            spine_pose_weight = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','spine_anim_config.weight')

        head_animation_entity_id = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','head_anim_config.animation_entity_id')
        if head_animation_entity_id == self._no_entry:
            head_pose = 'none'
            head_pose_weight = 1.0
        else:
            head_pose = self._workspace.get_entity_property_value(head_animation_entity_id,'WorkspaceEntityComponent','name')
            head_pose_weight = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','head_anim_config.weight')

        r_arm_animation_entity_id = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','arm_r_anim_config.animation_entity_id')
        if r_arm_animation_entity_id == self._no_entry:
            r_arm_pose = 'none'
            r_arm_pose_weight = 1.0
        else:
            r_arm_pose = self._workspace.get_entity_property_value(r_arm_animation_entity_id,'WorkspaceEntityComponent','name')
            r_arm_pose_weight = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','arm_r_anim_config.weight')

        l_arm_animation_entity_id = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','arm_l_anim_config.animation_entity_id')
        if l_arm_animation_entity_id == self._no_entry:
            l_arm_pose = 'none'
            l_arm_pose_weight = 1.0
        else:
            l_arm_pose = self._workspace.get_entity_property_value(l_arm_animation_entity_id,'WorkspaceEntityComponent','name')
            l_arm_pose_weight = self._workspace.get_entity_property_value(character['Entity_id'], 'CharacterAnimationConfigurationComponent','arm_l_anim_config.weight')

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

        self.setCustomMetadata(character['Entity_id'], "Pose", pose_info)

        return pose_info

    #_______________________________________________________________
    def setObjectInfo(self, object):
        object_info={}
        object_info["class"] = object['class'] if 'class' in object else ''
        object_info["name"] = object['name'] if 'name' in object else ''
        object_info["version"] = object['version'] if 'version' in object else ''
        object_info["color"] = object['Dominant color'] if 'Dominant color' in object else ''

        self.setCustomMetadata(object['Entity_id'], "Info", object_info)

        return object_info

    #_______________________________________________________________
    def setCharacterInfo(self, character):
        personal_info={}
        personal_info["gender"] = character['gender']
        personal_info["race"] = character['ethnicity']
        personal_info["type"] = character['kind']
        personal_info["age"] = character['agegroup']
        personal_info["height"] = character['height']

        self.setCustomMetadata(character['Entity_id'], "Info", personal_info)

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
        light_rotation.x = 0
        light_rotation.y = 90
        light_rotation.z = 0

        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','position', light_position)
        self._workspace.set_entity_property_value(light_id, 'RelativeTransformToComponent','rotation', light_rotation)

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
    def setActiveLightInPosition(self, light_id, rotation, position):
        light_rotation = self._workspace.get_entity_property_value(light_id, 'RelativeTransformToComponent','rotation')

        light_rotation.x += rotation.x
        light_rotation.y += rotation.y
        light_rotation.z += rotation.z
    
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

        left_right_delta = self.getCameraDelta(center, pos_intervals[y], normal)    # pos.y
        up_down_delta = self.getCameraDelta(center, pos_intervals[z], normal)       # pos.z
        front_back_delta = self.getCameraDelta(center, pos_intervals[x], normal)    # pos.x
        pos_delta = (front_back_delta, left_right_delta, up_down_delta)
        roll_delta = self.getCameraDelta(center, rot_intervals[x], normal)  # rot.x
        pitch_delta = self.getCameraDelta(center, rot_intervals[y], normal) # rot.y
        yaw_delta = self.getCameraDelta(center, rot_intervals[z], normal)   # rot.z
        rot_delta = (roll_delta, pitch_delta, yaw_delta)

        ego_position.x += front_back_delta / 100
        ego_position.y += left_right_delta / 100
        ego_position.z += up_down_delta / 100
        ego_rotation.x += roll_delta
        ego_rotation.y += pitch_delta
        ego_rotation.z += yaw_delta

        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','position', ego_position)
        self._workspace.set_entity_property_value(ego_id, 'RelativeTransformToComponent','rotation', ego_rotation)

        return ego_position, ego_rotation, pos_delta, rot_delta

    #_______________________________________________________________
    def setCameraVibration(self, cam_id, pos_intervals, rot_intervals, normal = True):
        center = 0
        x, y, z = 0, 1 ,2

        cam_position = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','position')
        cam_rotation = self._workspace.get_entity_property_value(cam_id, 'RelativeTransformToComponent','rotation')

        left_right_delta = self.getCameraDelta(center, pos_intervals[y], normal)    # pos.y
        up_down_delta = self.getCameraDelta(center, pos_intervals[z], normal)       # pos.z
        front_back_delta = self.getCameraDelta(center, pos_intervals[x], normal)    # pos.x
        pos_delta = (front_back_delta, left_right_delta, up_down_delta)
        roll_delta = self.getCameraDelta(center, rot_intervals[x], normal)  # rot.x
        pitch_delta = self.getCameraDelta(center, rot_intervals[y], normal) # rot.y
        yaw_delta = self.getCameraDelta(center, rot_intervals[z], normal)   # rot.z
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
        width = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','width_resolution')
        height = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','height_resolution')
        self._workspace.set_entity_property_value(cam_id, 'CameraPropertiesComponent','width_resolution', width/factor)
        self._workspace.set_entity_property_value(cam_id, 'CameraPropertiesComponent','height_resolution', height/factor)

        lens_name = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','lens_type')

        if 'OPENCV' in lens_name:
            cx = self._workspace.get_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cx')
            cy = self._workspace.get_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cy')
            self._workspace.set_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cx', cx/factor)
            self._workspace.set_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cy', cy/factor)

    #_______________________________________________________________
    def reduceAllCameraResolution(self, factor):
        cameras = self._workspace.get_camera_entities()
        for cam in cameras:
            self.reduceCameraResolution(cam, factor)

    #_______________________________________________________________
    def increaseCameraResolution(self,cam_id, factor):
        width = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','width_resolution')
        height = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','height_resolution')
        self._workspace.set_entity_property_value(cam_id, 'CameraPropertiesComponent','width_resolution', width*factor)
        self._workspace.set_entity_property_value(cam_id, 'CameraPropertiesComponent','height_resolution', height*factor)

        lens_name = self._workspace.get_entity_property_value(cam_id, 'CameraPropertiesComponent','lens_type')

        if 'OPENCV' in lens_name:
            cx = self._workspace.get_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cx')
            cy = self._workspace.get_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cy')
            self._workspace.set_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cx', cx*factor)
            self._workspace.set_entity_property_value(cam_id, 'CameraIntrinsicsComponent','camera-intrinsics-cy', cy*factor)

    #_______________________________________________________________
    def increaseAllCameraResolution(self, factor):
        cameras = self._workspace.get_camera_entities()
        for cam in cameras:
            self.increaseCameraResolution(cam, factor)

    #_______________________________________________________________
    def excludeAsset(self, asset):
        ret = False
        maxicosi_excluded_colors = ['Beige', 'Blue', 'Brown']
        cybex_excluded_colors = ['Dark', 'Green', 'LightGray', 'Orange']

        if 'BabyChild' == asset['kind'] and 'Maxi-Cosi' == asset['brand'] and asset['version'] in maxicosi_excluded_colors:
            ret = True
        if 'BabyChild' == asset['kind'] and 'Cybex' == asset['brand'] and asset['version'] in cybex_excluded_colors:
            ret = True

        return ret
    #_______________________________________________________________
    def queryResultToDic(self, queryResult, workspaceEntityType = anyverse_platform.WorkspaceEntityType.Asset):
        result = []
        total = len(queryResult)
        print('{} assets'.format(total))
        processed = 0
        for elem in queryResult:
            try:
                entityId = self._workspace.add_resource_to_workspace(workspaceEntityType, elem)
            except RuntimeError as rte:
                print('asset_resource_id = {}'.format(elem))
                print('[WARN] Latest version of the asset above is not compatible with current Anyverse studio version, skipping it... Update Anyverse Studio to support it')
                continue
            attrs = self._workspace.get_attribute_list_from_entity(entityId)
            try:
                tags = self._workspace.get_tags_from_entity(entityId)
            except RuntimeError as rte:
                tags = []
            dic = {}
            for att in attrs:
                dic[att.lower()] = self._workspace.get_attribute_value_as_string_from_entity(entityId, att)
                if dic[att.lower()].lower() == 'false':
                    dic[att.lower()] = False
                    continue
                if dic[att.lower()].lower() == 'true':
                    dic[att.lower()] = True
                # if re.match("[-+]?(([0-9]*[.]?[0-9]+([eE][-+]?[0-9]+)?))", dic[att.lower()]):
                #     dic[att.lower()] = float(dic[att.lower()])

            dic["resource_id"] = elem
            dic["entity_id"] = entityId
            dic["resource_name"] = self._workspace.get_entity_name(entityId)
            if 'childseat' in tags:
                if not self.excludeAsset(dic):
                    result.append(dic)
            else:
                result.append(dic)
            processed += 1
            # self.update_progress(processed/total)

        return result

    #_______________________________________________________________
    def queryCars(self, dynamic_material = False):
        query = aux.ResourceQueryManager(self._workspace)
        # query.add_tag_filter("compound")
        query.add_tag_filter("car-interior")
        query.add_exists_attribute_filter('brand')
        query.add_exists_attribute_filter('model')
        query.add_exists_attribute_filter('version')

        if dynamic_material:
            query.add_attribute_filter('dynamic_material', True)

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
        query.add_attribute_filter("class", "ChildSeat")
        query.add_attribute_filter("dynamic_material", False)

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
    def queryCarSeats(self, picked_car, dynamic_material = False):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_attribute_filter("brand", picked_car['brand'])
        query.add_attribute_filter("model", picked_car['model'])
        query.add_attribute_filter("type", "Seat")

        if dynamic_material:
            query.add_attribute_filter('dynamic_material', True)

        return self.queryResultToDic(query.execute_query_on_assets())

    #_______________________________________________________________
    def queryBackgrounds(self):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_exists_attribute_filter('Scattering')

        return self.queryResultToDic(query.execute_query_on_backgrounds(), anyverse_platform.WorkspaceEntityType.Background)

    #_______________________________________________________________
    def queryMaterials(self, color_scheme = False):
        query = aux.ResourceQueryManager(self._workspace)
        query.add_exists_attribute_filter('compatibility')

        if color_scheme:
            query.add_exists_attribute_filter('color_scheme')

        return self.queryResultToDic(query.execute_query_on_materials(), anyverse_platform.WorkspaceEntityType.Material)

    #_______________________________________________________________
    def getAssetExposedMaterials(self, fixed_id):
        exposed_materials = [ m for m in self._workspace.get_hierarchy(fixed_id) if 'MaterialPartEntity' == self._workspace.get_entity_type(m) ]

        return exposed_materials
    
    #_______________________________________________________________
    def changeExposedMaterials(self, fixed_id, asset_set, color_scheme = None):
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
            # print('Scheme {} materials: {}'.format(color_scheme, materials_list))

        # Get Fixed entity exposed materials
        exposed_materials = self.getAssetExposedMaterials(fixed_id)
        for material in exposed_materials:
            material_name = self._workspace.get_entity_name(material)
            # Get compatible materials from asset
            if material_name in asset:
                compatible_materials = [ cm['entity_id'] for cm in materials_list if asset[material_name] == cm['compatibility'] and cm['color_scheme'] == color_scheme ]
                if len(compatible_materials) != 0:
                    selected_material = compatible_materials[random.randrange(len(compatible_materials))]
                    # Take into account an equal probability to use the default material
                    self._workspace.set_entity_property_value(material, 'MaterialOverrideInfoComponent','material_entity_id', selected_material)
                    print('[INFO] Changing material {} to {}'.format(material_name, self._workspace.get_entity_name(selected_material)))
                else:
                    print('[WARN] No compatible materials found for exposed material {}'.format(material_name))
            else:
                print('[ERROR] Cannot change material: No {} attribute in asset {}'.format(material_name, asset['resource_name']))

    #_______________________________________________________________
    def changeExposedMaterialsList(self, fixed_ids_list, asset_set, color_scheme = None):
        cached_materials = {}
        for fixed_id in fixed_ids_list:
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
                # print('Scheme {} materials: {}'.format(color_scheme, materials_list))

            # Get Fixed entity exposed materials
            exposed_materials = self.getAssetExposedMaterials(fixed_id)
            for material in exposed_materials:
                material_name = self._workspace.get_entity_name(material)
                # Get compatible materials from asset
                if material_name in asset:
                    compatible_materials = [ cm['entity_id'] for cm in materials_list if asset[material_name] == cm['compatibility'] and cm['color_scheme'] == color_scheme ]
                    if len(compatible_materials) != 0:
                        if material_name in cached_materials:
                            selected_material = cached_materials[material_name]
                        else:
                            selected_material = compatible_materials[random.randrange(len(compatible_materials))]
                            cached_materials[material_name] = selected_material
                        # Take into account an equal probability to use the default material
                        self._workspace.set_entity_property_value(material, 'MaterialOverrideInfoComponent','material_entity_id', selected_material)
                        print('[INFO] Changing material {} to {}'.format(material_name, self._workspace.get_entity_name(selected_material)))
                    else:
                        print('[WARN] No compatible materials found for exposed material {}'.format(material_name))
                else:
                    print('[ERROR] Cannot change material: No {} attribute in asset {}'.format(material_name, asset['resource_name']))

    #_______________________________________________________________
    def filterCharacters(self, characters, key, value):
        filtered_characters = [c for c in characters if key.lower() in c and c[key.lower()] == value]

        elegible_chars = filtered_characters.copy()
        # Discard the characters already used
        for character in filtered_characters:
            if character['resource_name'] in self._already_used_characters:
                print('[WARN]: Character {} used. Removing from elegible...'.format(character['resource_name']))
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
    def getBeltAssetsForCar(self, brand, model, assetList):
        result = []
        if model == '0076_20220809':
            prefix = "{}".format(model)
        elif brand != 'Unbranded' and brand != 'Hyundai':
            prefix = "{}_{}".format(brand, model)
        else:
            prefix = "{}".format(brand)

        for item in assetList:
            if (prefix in item.name and "belt" in item.name and "Off" in item.name) :
                result.append(item)

        return result

    #_______________________________________________________________
    def getClipAssetForCar(self, brand, model,assetList):
        if model == '0076_20220809':
            beltName = "{}_ClipOn".format(model)
        else:
            beltName = "{}ClipOn".format(brand)
            
        for item in assetList:
            if item.name == beltName :
                return item

        return None

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
    def setIllumination(self, day, conditions, background, simulation_id, multiple_cameras = False, active_light = False):
        if conditions == 'scattered' or conditions == 'overcast':
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','cloud_cover', conditions.title())
        else:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','cloud_cover', 'Clear')

        scattering = 600
        if background != None:
            scattering = background['scattering']

        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','scatteringIntensity', scattering)

        incabin_light = None
        incabin_lights = self._workspace.get_entities_by_type('Light')
        if multiple_cameras:
            for incabin_light in incabin_lights:
                if active_light and incabin_light != None:
                    print('Active light {} ({}) turned on'.format(self._workspace.get_entity_name(incabin_light), incabin_light))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', True)
                elif incabin_light == None:
                    print('WARN: Active light set to True, but no active light defined in the workspace')
                else:
                    print('Active light {} turned off'.format(self._workspace.get_entity_name(incabin_light)))
                    self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', False)
        elif len(incabin_lights) > 0: # No multiple cameras, turn on the first light we find
            incabin_light = incabin_lights[0]
            if active_light:
                print('Active light {} ({}) turned on'.format(self._workspace.get_entity_name(incabin_light), incabin_light))
                self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', True)
            else:
                print('Active light {} turned off'.format(self._workspace.get_entity_name(incabin_light)))
                self._workspace.set_entity_property_value(incabin_light, 'VisibleComponent','visible', False)
        elif active_light:
            print('WARN: Active light set to True, but no active light defined in the workspace')

        if day:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','ilumination_type', 'PhysicalSky')
            if conditions == 'overcast':
                sky_light_intensity = 0.8
                sun_light_intensity = 0.5
            elif conditions == 'scattered':
                sky_light_intensity = 0.8
                sun_light_intensity = 0.8
            else:
                sky_light_intensity = 1
                sun_light_intensity = 1

            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sky_light_intensity', sky_light_intensity)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','sun_light_intensity', sun_light_intensity)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','scatteringIntensity', 600)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','diffractionIntensity', 300)
            return sky_light_intensity, sun_light_intensity
        else:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','ilumination_type', 'Background')
            ibl_light_intensity = random.uniform(1, 1)
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','iblLightIntensity', ibl_light_intensity)

            background_weight = 1
            if background != None:
                self._workspace.set_entity_property_value(background['Entity_id'], 'BackgroundContentComponent','environment_weight', background_weight)
            return background_weight, ibl_light_intensity

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
                print('[WARNING] Cannot find sensor {}, setting the camera to No Sensor'.format(sensor_name))

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
                print('[WARNING] Cannot find ISP {}, setting the camera to No Sensor'.format(isp_name))
                
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
    def setGroundRotationTimeOfDay(self, day, simulation_id, dawn = False):
        time_of_day = self.genTimeOfday(day, dawn)
        ground_rotation = random.uniform(0,360)

        self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','time_of_day', time_of_day)
        self.setGroundRotation(ground_rotation, simulation_id)

        return time_of_day, ground_rotation

    #_______________________________________________________________
    def setBackground(self, background, simulation_id, dawn = False):
        if not dawn:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','fixed_background',background['Entity_id'])
            self._workspace.set_entity_property_value(background['Entity_id'], 'BackgroundContentComponent','environment_weight', background['background_intensity'])
        else:
            self._workspace.set_entity_property_value(simulation_id, 'SimulationEnvironmentComponent','fixed_background',self._no_entry)

        # Dump the background info in the simulation custom metadata
        bkg_info = {}
        bkg_info['background'] = background['name']
        bkg_info['env-weight'] = self._workspace.get_entity_property_value(background['Entity_id'], 'BackgroundContentComponent','environment_weight')

        self.setCustomMetadata(simulation_id, "backgroundInfo", bkg_info)

    #_______________________________________________________________
    def selectBackground(self, day, bg_list = None):
        if bg_list == None:
            if day :
                backgrounds = [ b for b in self._workspace.backgrounds if b['day'] ]
            else:
                backgrounds = [ b for b in self._workspace.backgrounds if not b['day'] ]
        else:
            backgrounds = bg_list

        selected_background_idx = random.randrange(0,len(backgrounds))
        selected_background = backgrounds[selected_background_idx]

        ws_bckgnd_id = self._workspace.create_entity_from_resource(anyverse_platform.WorkspaceEntityType.Background, selected_background["resource_name"], selected_background["resource_id"], anyverse_platform.invalid_entity_id)
        selected_background['Entity_id'] = ws_bckgnd_id

        return selected_background, ws_bckgnd_id

    #_______________________________________________________________
    def selectCar(self, use_probs = False, car_model = None):
        if use_probs:
            probabilities = [ c['probability'] for c in use_probs ]
            idx = self.choiceUsingProbabilities(probabilities)
            car_name = use_probs[idx]['car_name']
            elegible_cars = [ i for i, c in enumerate(self._workspace.cars) if c['brand'].replace(" ", "") in car_name ]
            idx = elegible_cars[random.randrange(len(elegible_cars))]
        else:
            idx = random.randrange(len(self._workspace.cars))

        if not car_model:
            picked_car = self._workspace.cars[idx]
        else:
            picked_car = self._workspace.cars[idx]
            stop = False
            while (car_model not in picked_car['resource_name'] and not stop):
                idx = random.randrange(len(self._workspace.cars))
                picked_car = self._workspace.cars[idx]
                if car_model == 'Unbranded_GenericSUV' and 'Unbranded' in picked_car['resource_name']:
                    stop = True

        new_car_id = self._workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.Asset, picked_car["resource_id"])
        picked_car['Entity_id'] = new_car_id
        self._car_brand = picked_car['brand'].replace(" ", "")
        self._car_model = picked_car['model']
        return picked_car

    #_______________________________________________________________
    def buildCar(self, picked_car, the_car, dynamic_materials = False):
        self._workspace.set_entity_property_value(the_car, 'AssetEntityReferenceComponent','asset_entity_id', picked_car['Entity_id'])
        print('Using car: {}_{}_{}'.format(picked_car['brand'], picked_car['model'], picked_car['version']))

        # Change car interior materials following a color scheme
        color_scheme = self._car_color_schemes[random.randrange(len(self._car_color_schemes))]
        print('Color scheme: {}'.format(color_scheme))
        
        self.changeExposedMaterials(the_car, picked_car, color_scheme = color_scheme)

        self.setCarSeatbeltsOff(picked_car)
        self.setSeats(picked_car, the_car, dynamic_materials, color_scheme)

    #_______________________________________________________________
    def setSeat(self, the_car, seats, seat_locators, seat_pos, color_scheme = None):
        locator = next( (x for x in seat_locators if seat_pos in self._workspace.get_entity_name(x).lower()), None )
        if locator != None:
            # There is a specific locator por this seat
            seat = next((x for x in seats if seat_pos in x["resource_name"].lower()), None)
            if seat != None:
                seat_asset = self._workspace.create_entity_from_resource( anyverse_platform.WorkspaceEntityType.Asset, seat["resource_name"], seat["resource_id"], anyverse_platform.invalid_entity_id )
                seat_id = self._workspace.create_fixed_entity(seat["resource_name"], locator, seat_asset)
                # self.setSplitAction(seat_id, 'Split') # If the assets does not have the the 'compound' tag
            else:
                print("Locator {} exists but not its seat".format(self._workspace.get_entity_name(locator)) )
                seat_id = anyverse_platform.invalid_entity_id
        else:
            # There is not a specific locator por this seat. Create it under the car directly
            seat = next((x for x in seats if seat_pos in x["resource_name"].lower()), None)
            if seat != None:
                seat_asset = self._workspace.create_entity_from_resource( anyverse_platform.WorkspaceEntityType.Asset, seat["resource_name"], seat["resource_id"], anyverse_platform.invalid_entity_id )
                seat_id = self._workspace.create_fixed_entity(seat["resource_name"], the_car, seat_asset)
            else:
                print("No exists locator neither seat for position {}".format(seat_pos) )
                seat_id = anyverse_platform.invalid_entity_id

        return seat_id

    #_______________________________________________________________
    def setSeats(self, picked_car, the_car, dynamic_materials = False, color_scheme = None):
        if (not 'adjustable_seats' in picked_car) or (not picked_car['adjustable_seats'] ):
            return

        # Check if the car is a seven seater
        seven_seater = False
        seat_locators = self._workspace.get_entities_by_name_including('adjustableSeat')
        if len(seat_locators) > 5:
            seven_seater = True

        # Get seats from DDBB and get only the conventional ones for a seven seater
        seats = self.queryCarSeats(picked_car, dynamic_materials)
        if seven_seater:
            seat_locators = [ sl for sl in seat_locators if 'conventional' in self._workspace.get_entity_name(sl) ]
            seats  = [ s for s in seats if 'conventional' in s['resource_name'] ]

        seat_ids_list = []  
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat01", color_scheme))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat02", color_scheme))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat03", color_scheme))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat04", color_scheme))
        seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat05", color_scheme))
        if seven_seater:
            seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat06", color_scheme))
            seat_ids_list.append(self.setSeat(the_car, seats, seat_locators, "seat07", color_scheme))
        
        self.changeExposedMaterialsList(seat_ids_list, seats, color_scheme)
        
    #_______________________________________________________________
    def setCarSeatbeltsOff(self, picked_car):
        belt_locator = self._workspace.get_entities_by_name('belt_locator')[0]
        self.deleteChildren(belt_locator)
        belts = self.getBeltAssetsForCar(picked_car['brand'], picked_car['model'], self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset))
        for belt in belts:
            belt_asset = self._workspace.create_entity_from_resource( anyverse_platform.WorkspaceEntityType.Asset, belt.name, belt.id, anyverse_platform.invalid_entity_id )
            beltoff_id = self._workspace.create_fixed_entity(belt.name, belt_locator, belt_asset)
            self.setExportAlwaysExcludeOcclusion(beltoff_id)
            belt_name = self._workspace.get_entity_name(beltoff_id)
            seat_info = {}
            seat_info['number'] = 'seat{}'.format(belt_name.split('_')[2][-2:])
            self.setCustomMetadata(beltoff_id, "Seat", seat_info)

    #_______________________________________________________________
    def createBeltFor(self, seat_pos, beltUserEntityId, car_brand, car_model, seatbelts_distribution ):
        print("Setting belt on in position {}".format(seat_pos))
        seatId = str(seat_pos).zfill(2)
        clip = self.getClipAssetForCar(car_brand, car_model, self._workspace.get_cache_of_entity_resource_list(anyverse_platform.WorkspaceEntityType.Asset))
        if clip == None:
            print("Cannot find clip for brand " + car_brand)
        clip_asset = self._workspace.create_entity_from_resource( anyverse_platform.WorkspaceEntityType.Asset, clip.name, clip.id, anyverse_platform.invalid_entity_id )
        assert clip_asset != anyverse_platform.invalid_entity_id

        jointsToRemove = None  # For the moment just use the default: both arms

        belt_id, belt_placement = self.createBelt( beltUserEntityId, clip_asset, seatId, jointsToRemove, seatbelts_distribution )
        belt_name = self._workspace.get_entity_name(belt_id)
        print('Placed belt name: {}'.format(belt_name))
        self._workspace.set_entity_name(belt_id, 'SeatBelt0{}_On'.format(seat_pos))
        print('New belt name: {}'.format(self._workspace.get_entity_name(belt_id)))
        # Set the user custom metadata with the belt placement and the 
        seat_info = {}
        seat_info['number'] = 'seat0{}'.format(seat_pos)
        self.setCustomMetadata(belt_id, "Seat", seat_info)

        return belt_placement


    #_______________________________________________________________
    def createBelt( self, beltUserEntityId, clipAsset, seatId="01", joints_to_remove=[], seatbelts_distribution = None ):
        clipLocatorName = "clipOn{}_locator".format( seatId )
        clipLocator = self._workspace.get_entities_by_name( clipLocatorName )[0]

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

        dummy_id = None
        userId = beltUserEntityId

        if beltUserEntityId == anyverse_platform.invalid_entity_id:
            dummy_id = self._workspace.create_fixed_entity("dummy", anyverse_platform.invalid_entity_id, self._workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Asset)[0])
            userId = dummy_id

        args = [ userId,
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
            beltType = ""
            if beltUserEntityId == anyverse_platform.invalid_entity_id:
                beltPlacement = anyverse_platform.SeatBeltPlacement.WithoutCharacter
                beltType = 'WithoutCharacter'
            else:
                toList = [ (key, float(value)) for key, value in seatbelts_distribution['seatbelt_placement_probabilities'].items() ]
                idx = self.choiceUsingProbabilities([x[1] for x in toList])
                beltType = toList[idx][0]
                beltPlacement = self._beltOptions[beltType]
                print('beltPlacement: {}'.format(beltPlacement))

        args.append( beltPlacement )

        beltId = self._workspace.create_seat_belt( *args )
        anyverse_platform.entitiesToClear.append(beltId)

        self.setCustomMetadata(beltId, "Placement", beltType)
        self.removeOffBeltAt(seatId)

        if dummy_id != None:
            self._workspace.delete_entity(dummy_id)

        return beltId, beltType

    #_______________________________________________________________
    def removeOffBeltAt(self, pos):
        offs = self._workspace.get_entities_by_name_including( str(pos) + "_Off")
        for off in offs:
            if self._workspace.get_entity_type(off) == str(anyverse_platform.WorkspaceEntityType.FixedEntity):
                # print('Deleting off belt {}'.format(off))
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
    def selectConditions(self, conditions):
        probabilities = [ float(c['probability']) for c in conditions ]
        cond = conditions[self.choiceUsingProbabilities(probabilities)]

        return cond['Day'], cond['Cond']

    #_______________________________________________________________
    def seatLocator2ChildseatLocator(self, seat_locator, the_car):
        childseat_locators = self.getChildseatLocators(the_car)
        seat_locator_name = self._workspace.get_entity_name(seat_locator)
        childseat_locator_name = 'child' + seat_locator_name

        print('transforming {} to {}'.format(seat_locator_name,childseat_locator_name))

        for childseat_locator in childseat_locators:
            if self._workspace.get_entity_name(childseat_locator).lower() == childseat_locator_name:
                ret = childseat_locator
                break

        return ret


    #_______________________________________________________________
    def fillSeat(self, occupancy, seat_locator, childseat_config, seatbelts_distribution = None, accessories_probabilities = None, gaze_probabilities = None, expression_probabilities = None):
        gaze = None
        the_car = self.getCars()[0]
        car_name = self._workspace.get_entity_name(self._workspace.get_entity_property_value(the_car, 'AssetEntityReferenceComponent','asset_entity_id'))
        if occupancy == 0:
            ret = {}
            self.doNothing(seat_locator)
            if seatbelts_distribution is not None:
                set_seatbel_on = True if random.uniform(0,1) <= seatbelts_distribution["belt_on_without_character_probability"] else False
                if set_seatbel_on and not self._script_console:
                    print('Setting belt on to empty seat {}'.format(self._workspace.get_entity_name(seat_locator).split('_')[0]))
                    self.createBeltFor(self.getSeatPos(seat_locator), anyverse_platform.invalid_entity_id, self._car_brand, self._car_model, seatbelts_distribution)

            ret['isEmpty'] = True
            ret['Seatbelt_on'] = set_seatbel_on
        elif occupancy == 1:
            driver = self.placeDriver(seat_locator, seatbelts_distribution = seatbelts_distribution, accessories_probabilities = accessories_probabilities, gaze_probabilities = None, expression_probabilities = expression_probabilities)
            if driver == None:
                print('[WARN]: Couldnot find a driver to place')
            ret = driver
        elif occupancy == 2:
            childseat_occupancy_probabilities = childseat_config['childseat_occupancy_probabilities']
            childseat = self.placeChildseat(seat_locator, childseat_config, only_baby_in_copilot = False)
            if childseat != None:
                childseat_occupancy = self.decideChildSeatOccupancy(childseat_occupancy_probabilities)
                if childseat_occupancy == 0: # Empty
                    child = None
                    print('[INFO]: Leaving childseat empty')
                    ret = [childseat, child]
                elif childseat_occupancy == 1: # Child
                    if childseat['kind'] != 'BabyChild':
                        child = self.placeChildInChildseat(childseat, seat_locator, seatbelts_distribution = seatbelts_distribution, expression_probabilities = expression_probabilities)
                    else:
                        child = self.placeBabyInChildseat(childseat, seat_locator)
                    ret = [childseat, child]
                elif childseat_occupancy == 2: # Object
                    childseat_locator = self.getEntityLocators(childseat['Entity_id'])[0]
                    object = self.placeObjectInChildseat(childseat_locator, childseat)
                    ret = [childseat, object]
            else:
                print('[WARN]: Could not find a childseat to place')
                ret = {}
                ret['isEmpty'] = True
                ret['Seatbelt_on'] = False
        elif occupancy == 3:
            if gaze_probabilities is not None:
                gaze = gaze_probabilities['copilot_gaze_probabilities']
            passenger = self.placePassenger(seat_locator, seatbelts_distribution = seatbelts_distribution, accessories_probabilities = accessories_probabilities, gaze_probabilities = gaze, expression_probabilities = expression_probabilities)
            if passenger == None:
                print('[WARN]: Couldnot find a passenger to place')
            ret = passenger
        elif occupancy == 4:
            if 'v0' in car_name:
                object = self.placeObjectOnSeat(seat_locator, self.getParent(seat_locator))
            else:
                object = self.placeObject(seat_locator)
            if object == None:
                print('[WARN]: Could not find a object to place')
            ret = object
        else:
            print('Invalid filling seat action')

        # Set the driver gaze if filling copilot seat to take into account what
        # was just placed in it
        if self.isCopilotSeat(seat_locator) and gaze_probabilities is not None:
            gaze = gaze_probabilities['driver_gaze_probabilities']
            self.setDriverGaze(gaze) 

        return ret

    #_______________________________________________________________
    def EmptyDistribution(self, the_car, occupancy_distribution):
        print('Empty distribution, leaving the car empty')
        seat_locators = self.getSeatLocators(the_car)
        occupied_seats = 0
        ret = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            occupancy = 0 # Empty
            # Now we fill the seats to apply the seatbelt logic on empty seats
            seat_occupant = self.fillSeat(occupancy,seat_locator,
                                        childseat_config = occupancy_distribution['childseat_config'],
                                        seatbelts_distribution = occupancy_distribution['seatbelts_distribution'],
                                        accessories_probabilities = occupancy_distribution['accessories_probabilities']
                                        )
            ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': 'None', 'Seatbelt_on': seat_occupant['Seatbelt_on']})
        return ret

    #_______________________________________________________________
    def NormalOccupantDistribution(self, the_car, occupancy_distribution):
        seat_locators = self.getSeatLocators(the_car)
        seven_seater = False
        if len(seat_locators) == 7:
            seven_seater = True
        occupied_seats = 0
        ret = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            if seven_seater and 'seat05' in seat_locator_name:
                break
            occupancy = self.decideSeatOccupancy(seat_locator, occupancy_distribution)
            if occupancy != 0:
                occupied_seats += 1
            if occupancy == 2: # 2 means we are placing a childseat so we need the childseat locator
                seat_locator = self.seatLocator2ChildseatLocator(seat_locator, the_car)

            if 'gaze_probabilities' in occupancy_distribution:
                gaze_distribution = occupancy_distribution['gaze_probabilities']
            else:
                gaze_distribution = None
                print('[WARN] No gaze probabilities')

            if 'expression_probabilities' in occupancy_distribution:
                expression_probabilities = occupancy_distribution['expression_probabilities']
            else:
                expression_probabilities = None

            seat_occupant = self.fillSeat(occupancy,seat_locator,
                                        childseat_config = occupancy_distribution['childseat_config'],
                                        seatbelts_distribution = occupancy_distribution['seatbelts_distribution'],
                                        accessories_probabilities = occupancy_distribution['accessories_probabilities'],
                                        gaze_probabilities = gaze_distribution,
                                        expression_probabilities = expression_probabilities
                                        )

            # Build a return list with a dict with the occupancy of every seat
            if 'isEmpty' in seat_occupant:
                ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': 'None', 'Seatbelt_on': seat_occupant['Seatbelt_on']})
            else:
                if type(seat_occupant) != list:
                    ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': seat_occupant['name'], 'Seatbelt_on': seat_occupant['Seatbelt_on'], 'Accessory': seat_occupant['Accessory']})
                else:
                    if seat_occupant[1] != None:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['name'], 'Occupant': seat_occupant[1]['name'], 'Seatbelt_on': seat_occupant[1]['Seatbelt_on']})
                    else:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['name'], 'Occupant': 'None', 'Seatbelt_on': False})

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
        passenger_l = [ ent for ent in self._workspace.get_hierarchy(passenger_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) ]
        if len(passenger_l) > 0:
            passenger = passenger_l[len(passenger_l)-1]
        else:
            passenger = passenger_seat

        gaze_info = {}
        idx = self.choiceUsingProbabilities([ float(o['probability']) for o in gaze_probabilities ])
        gaze = gaze_probabilities[idx]['gaze']
        gaze_info['direction'] = gaze_probabilities[idx]['name']
        gaze_info['code'] = gaze
        print('Setting the driver to look at {}({})'.format(gaze_probabilities[idx]['name'], gaze_probabilities[idx]['gaze']))
        if driver != anyverse_platform.invalid_entity_id:
            if gaze == 1:
                side = 'left' if random.uniform(0,1) <= 0.5 else 'right'
                self.LookAtExteriorRearViewMirror(driver, the_car, side)
                gaze_info['side'] = side
            elif gaze == 2:
                self.LookAtInsideRearViewMirror(driver, the_car)
            elif gaze == 3:
                self.LookAtInfotainment(the_car, driver)
            elif gaze == 4:
                self.LookAtOtherCharacter(driver, passenger)
            elif gaze == 5:
                self.LookAtRearSeat(driver,the_car, 'right')

            self.setCustomMetadata(driver, 'gaze', gaze_info)

    #_______________________________________________________________
    def setPassengerGaze(self, gaze_probabilities):
        the_car = self.getCars()[0]
        seat_locators = self.getSeatLocators(the_car)
        childseat_locators = self.getChildseatLocators(the_car)
        # We consider the driver what ever is placed in the driver seat:
        # (character or the seat itself if empty)
        driver_seat = self.getParent([ ent for ent in seat_locators if 'seat01' in self._workspace.get_entity_name(ent).lower() ][0])
        driver_l = [ ent for ent in self._workspace.get_hierarchy(driver_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
        if len(driver_l) > 0:
            driver = driver_l[len(driver_l)-1]
        else:
            driver = driver_seat
        passenger_seats = [ ent for ent in seat_locators + childseat_locators if 'seat02' in self._workspace.get_entity_name(ent).lower() ]
        for passenger_seat in passenger_seats:
            passenger_l = [ ent for ent in self._workspace.get_hierarchy(passenger_seat) if 'FixedEntity' == self._workspace.get_entity_type(ent) and 'rp_' in self._workspace.get_entity_name(ent)]
            if len(passenger_l) > 0:
                passenger = passenger_l[0]
                break

        gaze_info = {}
        idx = self.choiceUsingProbabilities([ float(o['probability']) for o in gaze_probabilities ])
        gaze = gaze_probabilities[idx]['gaze']
        gaze_info['direction'] = gaze_probabilities[idx]['name']
        gaze_info['code'] = gaze
        print('Setting the passenger to look at {}({})'.format(gaze_probabilities[idx]['name'], gaze_probabilities[idx]['gaze']))
        if gaze == 1:
            side = 'left' if random.uniform(0,1) <= 0.5 else 'right'
            self.LookAtExteriorRearViewMirror(passenger, the_car, side)
            gaze_info['side'] = side
        elif gaze == 2:
            self.LookAtInsideRearViewMirror(passenger, the_car)
        elif gaze == 3:
            self.LookAtInfotainment(the_car, passenger)
        elif gaze == 4:
            self.LookAtOtherCharacter(passenger, driver)
        elif gaze == 5:
            self.LookAtRearSeat(passenger,the_car, 'left')

        self.setCustomMetadata(passenger, 'gaze', gaze_info)

    #_______________________________________________________________
    def getOccupant(self, seat_locator, occupant_dist):
        seat_name = self._workspace.get_entity_name(seat_locator).split("_")[0]
        for occupant in occupant_dist:
            if occupant['Seat'] == seat_name:
                return occupant

    #_______________________________________________________________
    def applyOccupantDistribution(self, the_car, occupant_dist):
        seat_locators = self.getSeatLocators(the_car)

        ret = []
        for seat_locator in seat_locators:
            seat_locator_name = self._workspace.get_entity_name(seat_locator).split('_')[0]
            occupant = self.getOccupant(seat_locator, occupant_dist)
            childseat_name = occupant['Childseat'] if occupant['Childseat'] != 'None' else None
            occupied = occupant['Occupant'] != 'None'
            seat_occupant = None
            if self.isDriverSeat(seat_locator) and occupied:
                seat_occupant = self.placeDriver(seat_locator, occupant['Occupant'])
            else:
                if childseat_name != None:
                    childseat = self.placeChildseat(seat_locator, childseat_name)
                    if childseat['kind'] == 'BabyChild' and occupied:
                        child = self.placeBabyInChildseat(childseat, seat_locator, occupant['Occupant'])
                    else:
                        child = self.placeChildInChildseat(childseat, seat_locator, occupant['Occupant'])
                    seat_occupant = [childseat, child]
                elif occupied:
                    seat_occupant = self.placePassenger(seat_locator, occupant['Occupant'])

            # Build a return list with adict with the occupancy of every seat
            if seat_occupant == None:
                ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': 'None', 'Seatbelt_on': False})
            else:
                if type(seat_occupant) != list:
                    ret.append({'Seat': seat_locator_name, 'Childseat': 'None', 'Occupant': seat_occupant['name'], 'Seatbelt_on': seat_occupant['Seatbelt_on'], 'Accessory': seat_occupant['Accessory']})
                else:
                    if seat_occupant[1] != None:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['Name'], 'Occupant': seat_occupant[1]['Name'], 'Seatbelt_on': seat_occupant[1]['Seatbelt_on']})
                    else:
                        ret.append({'Seat': seat_locator_name, 'Childseat': seat_occupant[0]['Name'], 'Occupant': 'None', 'Seatbelt_on': False})

        return ret

    #_______________________________________________________________
    def createCCLocator(self, the_car):
        cc_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'cc_info' in self._workspace.get_entity_name(ent) ]
        if len(cc_locators) > 0:
            print('[INFO] Recreating CC locator')
            self._workspace.delete_entity(cc_locators[0])
        cc_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'cc_info_locator', the_car)

        loc_position = anyverse_platform.Vector3D(0.6, 0.0, random.uniform(0.9, 1.0))
        self._workspace.set_entity_property_value(cc_locator,'RelativeTransformToComponent','position', loc_position)
        print('CC locator: {}'.format(self._workspace.get_entity_name(cc_locator)))
        return cc_locator

    #_______________________________________________________________
    def reachInfotainment(self, character_id, hand):
        the_car = self.getCars()[0]
        cc_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'cc_info' in self._workspace.get_entity_name(ent) ]
        if len(cc_locators) > 0:
            cc_locator = cc_locators[0]
            hand_config = 'left_hand_config.locator_entity_id'
            if hand == 'right':
                hand_config = 'right_hand_config.locator_entity_id'
            self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent',hand_config, cc_locator)
        else:
            print('[WARN] Could not find CC infotainment locator.')
        return self._workspace.get_entity_name(cc_locator)

    #_______________________________________________________________
    def reachRVM(self, character_id, hand):
        the_car = self.getCars()[0]
        rvm_inside_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and "rvm_inside_locator" == self._workspace.get_entity_name(ent) ]
        num_locs = len(rvm_inside_locators)
        if num_locs > 0:
            rvm_inside_locator = rvm_inside_locators[0]
            hand_config = 'right_hand_config'
            if hand == 'left':
                hand_config = 'left_hand_config'
            loc_rot = self._workspace.get_entity_property_value(rvm_inside_locator, 'RelativeTransformToComponent','rotation')
            loc_rot.z += 90
            loc_rot.y += 0
            loc_rot.x += 45
            self._workspace.set_entity_property_value(rvm_inside_locator, 'RelativeTransformToComponent','rotation', loc_rot)
            self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent',hand_config+'.locator_entity_id', rvm_inside_locator)
            offset_value = random.uniform(-0.4,0.1)
            offset = anyverse_platform.Vector3D(0,0,offset_value)
            self._workspace.set_entity_property_value(character_id, 'CharacterHandAttachmentComponent',hand_config+'.offset', offset)
        else:
            print('[WARN] Could not find RVM locator.')
        return self._workspace.get_entity_name(rvm_inside_locator)+'({})'.format(offset_value)

    #_______________________________________________________________
    def createRVMLocator(self, the_car, side):
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'rvm_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) == 0:
            rvm_locator = self._workspace.create_entity(anyverse_platform.WorkspaceEntityType.Locator, 'rvm_' + side + '_locator', the_car)
            loc_position = anyverse_platform.Vector3D(0.0, 0.0, 0.0)
            if side == 'right':
                loc_position = anyverse_platform.Vector3D(0.7, -0.9, 1.1)
            elif side == 'left':
                loc_position = anyverse_platform.Vector3D(0.7, 0.9, 1.1)
            elif side == 'inside':
                loc_position = anyverse_platform.Vector3D(0.45, 0.0, 1.3)
            self._workspace.set_entity_property_value(rvm_locator,'RelativeTransformToComponent','position', loc_position)
        else:
            print('[WARN] rvm_{}_locator already created.'.format(side))
            rvm_locator = locators[0]

        print('RVM locator: {}'.format(self._workspace.get_entity_name(rvm_locator)))
        return rvm_locator

    #_______________________________________________________________
    def getRVMLocator(self, the_car, side):
        rvm_locator = None
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'rvm_'+side in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            rvm_locator = locators[0]
        else:
            print('[WARN] Could NOT find rvm_{}_locator.'.format(side))

        print('RVM locator: {}'.format(self._workspace.get_entity_name(rvm_locator)))
        return rvm_locator

    #_______________________________________________________________
    def getCCLocator(self, the_car):
        cc_locator = None
        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'cc_info' in self._workspace.get_entity_name(ent) ]
        if len(locators) > 0:
            cc_locator = locators[0]
        else:
            print('[WARN] Could NOT find cc_infotainmet_locator.')

        print('CC locator: {}'.format(self._workspace.get_entity_name(cc_locator)))
        return cc_locator

    #_______________________________________________________________
    def letGoWheel(self, looker, side):
        if side == 'right':
            self._workspace.set_entity_property_value(looker, 'CharacterHandAttachmentComponent','right_hand_config.locator_entity_id', anyverse_platform.invalid_entity_id)
        if side == 'left':
            self._workspace.set_entity_property_value(looker, 'CharacterHandAttachmentComponent','left_hand_config.locator_entity_id', anyverse_platform.invalid_entity_id)

    #_______________________________________________________________
    def LookAtRearSeat(self, looker, the_car, side):
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 3)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

        seat_number = '01'
        if side == 'right':
            seat_number = '05'
            self.letGoWheel(looker, side)
            animation, weight = self.selectAdultAnimation('right_arm', 0.25, 0.75, 'above_the_head_r')
            self.setAnimation('right_arm', animation, weight, looker)
        elif side == 'left':
            seat_number = '03'
            animation, weight = self.selectAdultAnimation('right_arm', 0.25, 0.35, 'above_the_head_r')
            self.setAnimation('right_arm', animation, weight, looker)

        # Make the character lean forward to some extent
        animation, weight = self.selectAdultAnimation('spine', 0, 1, 'leaning_forward')
        self.setAnimation('spine', animation, weight, looker)

        seat_locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' and 'seat'+seat_number in self._workspace.get_entity_name(ent).lower() ]
        if len(seat_locators) > 0:
            seat_loc = seat_locators[0]
        else:
            seat_loc = anyverse_platform.invalid_entity_id

        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', seat_loc)

    #_______________________________________________________________
    def LookAtOtherCharacter(self, looker, looked_at):
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 2)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

        looked_at_name = self._workspace.get_entity_name(looked_at)
        print('Driver looking at ' + looked_at_name)

        if looked_at != anyverse_platform.invalid_entity_id and 'rp_' in looked_at_name:
            char_locators = [ ent for ent in self._workspace.get_hierarchy(looked_at) if self._workspace.get_entity_type(ent) == 'Locator' ]
            if len(char_locators) >= 1:
                lookat_locator = char_locators[0]
        else:
            lookat_locator = looked_at

        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', lookat_locator)

    #_______________________________________________________________
    def LookAtInsideRearViewMirror(self, looker, the_car):
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 3)
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

        locators = [ ent for ent in self._workspace.get_hierarchy(the_car) if self._workspace.get_entity_type(ent) == 'Locator' ]
        inside_rvm = [ l for l in locators if 'rvm_in' in self._workspace.get_entity_name(l) ][0]
        self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', inside_rvm)

    #_______________________________________________________________
    def LookAtExteriorRearViewMirror(self, looker, the_car, side):
        rvm_locator = self.getRVMLocator(the_car, side)
        if rvm_locator is not None:
            print('Looking at {} exterior rvm'.format(side))
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 3)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', rvm_locator)

    #_______________________________________________________________
    def LookAtInfotainment(self, the_car, looker):
        cc_locator = self.getCCLocator(the_car)

        if cc_locator is not None:
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','apply_ik', True)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','ik_chain_length', 3)
            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','type_gaze_control', 'Entity')

            self._workspace.set_entity_property_value(looker, 'CharacterGazeControlComponent','target_entity', self._ego_id)

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
            jaw_position = 0.8
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
