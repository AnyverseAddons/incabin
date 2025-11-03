import math

#_______________________________________________________________
def getSunDirection(azimuth, elevation):
    sun_direction = anyverse_platform.Vector3D(0,0,0)

    sun_direction.x = math.cos(elevation) * math.sin(azimuth)
    sun_direction.y = math.cos(elevation) * math.cos(azimuth)
    sun_direction.z = math.sin(elevation)

    return sun_direction

azimuth = math.radians(-22.21)
elevation = math.radians(43.76)
sun_direction = getSunDirection(azimuth, elevation)

print(sun_direction)