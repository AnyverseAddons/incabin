
dic_to_delete = 'objects'
if dic_to_delete is None:
    if hasattr(anyverse_platform, 'cars'):
        delattr(anyverse_platform, 'cars')
                        
    if hasattr(anyverse_platform, 'characters'):
        delattr(anyverse_platform, 'characters')
        
    if hasattr(anyverse_platform, 'babies'):
        delattr(anyverse_platform, 'babies')
        
    if hasattr(anyverse_platform, 'childseats'):
        delattr(anyverse_platform, 'childseats')
            
    if hasattr(anyverse_platform, 'objects'):
        delattr(anyverse_platform, 'objects')

    if hasattr(anyverse_platform, 'accessories'):
        delattr(anyverse_platform, 'accessories')

    if hasattr(anyverse_platform, 'backgrounds'):
        delattr(anyverse_platform, 'backgrounds')
else:
    if hasattr(anyverse_platform, dic_to_delete):
        delattr(anyverse_platform, dic_to_delete)

