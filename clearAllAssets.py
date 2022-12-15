import random
import anyverseaux.incabin
import importlib
importlib.reload(anyverseaux.incabin)

icu = anyverseaux.incabin.InCabinUtils(workspace, True)

def fixedExistsForAsset(asset_id):
    ret = None
    fixed_ents = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.FixedEntity)
    for fixed in fixed_ents:
        fixed_asset_id = workspace.get_entity_property_value(fixed, 'AssetEntityReferenceComponent','asset_entity_id')
        if asset_id == fixed_asset_id:
            ret = fixed
            break
    return ret
    
the_car = icu.getCars()[0]
the_car_asset_id = workspace.get_entity_property_value(the_car, 'AssetEntityReferenceComponent','asset_entity_id')
asset_ids = workspace.get_entities_by_type(anyverse_platform.WorkspaceEntityType.Asset)
for asset_id in asset_ids:
    if asset_id != the_car_asset_id:
        print('Deleting car asset {}'.format(workspace.get_entity_name(asset_id)))
        fixed_id = fixedExistsForAsset(asset_id)
        if fixed_id != None:
            workspace.delete_entity(fixed_id)
        workspace.delete_entity(asset_id)
            
    else:
        print('Skipping The_Car asset {}'.format(workspace.get_entity_name(asset_id)))
