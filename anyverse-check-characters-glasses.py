
chars_with_glasses = 0
chars_without_glasses = 0
char_anim_entity_id = None
wrong_characters = []
processed = 0
for char in anyverse_platform.characters:
    if char['glasses']:
        chars_with_glasses += 1
        char_entity_id = workspace.add_resource_to_workspace(anyverse_platform.WorkspaceEntityType.CharacterAsset, char['resource_id'])
        if not char_anim_entity_id:
            char_anim_entity_id = workspace.create_animated_entity('character', anyverse_platform.invalid_entity_id, char_entity_id)
        else:
            workspace.set_entity_property_value(char_anim_entity_id, 'CharacterAssetEntityReferenceComponent','character_asset_entity_id', char_entity_id)

        glasses_locator = workspace.get_entities_by_name('glasses_locator') if len(workspace.get_entities_by_name('glasses_locator')) == 1 else None
        if not glasses_locator:
            # print('Character: {} is missing the glasses locator'.format(char['name']))
            wrong_characters.append(char['name'])
        else:
            workspace.delete_entity(char_entity_id)       
    else:
        chars_without_glasses += 1
    processed += 1
    print('{} of {} checked'.format(processed, len(anyverse_platform.characters)))
    if processed == 10:
        break
        
print('Chars with glasses: {}'.format(chars_with_glasses))
print('Wrong characters with glasses ({}): {}'.format(len(wrong_characters), wrong_characters))
print('Chars without glasses: {}'.format(chars_without_glasses))