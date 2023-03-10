[![PyPI version](https://badge.fury.io/py/spatial-transform.svg)](https://badge.fury.io/py/spatial-transform)
[![PyPI download month](https://img.shields.io/pypi/dm/spatial-transform.svg)](https://pypi.python.org/pypi/spatial-transform/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Main](https://github.com/Wasserwecken/spatial-transform/actions/workflows/build_main.yml/badge.svg?branch=main)](https://github.com/Wasserwecken/spatial-transform/actions)
[![Build Preview](https://github.com/Wasserwecken/spatial-transform/actions/workflows/build_preview.yml/badge.svg?branch=preview)](https://test.pypi.org/project/spatial-transform/)
<a href="https://www.buymeacoffee.com/ericdolch"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" height="20px"></a>

# spatial-transform
Lightweight libary for creating hierarchies in a 3D space, like Unity, Unreal, Blender or any other 3D application.

Properties like positions, rotations, directions and scales can be easily accessed and are calculated based on the parents space for the world space. Individual transforms can be attatched and detatched at any point and have some more comfort methods for easy modifications.

## Why and intention
This libary is a side product of my master thesis, in order to extract conveniently local and world data features from a humanoid skeleton hierarchy. I could not find any libary that could do that, without bloat or the features I required for extraction or modification.

## Installation
``` batch
pip install spatial-transform
 ```

 ## Notes
 - `Pose` is the class for all local space properties and operations. There is no awareness about other related space or hierarchy.
-  `Transform` extend the `Pose` class to add hierarchical wareness and provides additional properties and methods for the world space.
-  `Euler` is a class with static members only for converting euler angle into quaternions or matrices. It supports diffrent rotation orders and can be used to convert between
- The package [PyGLM](https://github.com/Zuzu-Typ/PyGLM) is used for matrix, quaternion and vector calculations.
- Same coordination space as [openGL and GLM](https://www.evl.uic.edu/ralph/508S98/coordinates.html) is used. Which is: Right-Handed, - Y+ is up, Z- is forward and positive rotations are counter clockwise.

## Examples
### Create and attach transforms
``` python
from SpatialTransform import Transform, Euler

# defining the transforms
hips = Transform('Hips', position=(0,2,0))
LeftLegUpper = Transform('LeftLegUpper', position=(+0.2,0,0))
LeftLegLower = Transform('LeftLegLower', position=(0,-1,0))
LeftLegFoot = Transform('LeftLegFoot', position=(0,-1,0))
RightLegUpper = Transform('RightLegUpper', position=(-0.2,0,0))
RightLegLower = Transform('RightLegLower', position=(0,-1,0))
RightLegFoot = Transform('RightLegFoot', position=(0,-1,0))

# defining the hierarchy
hips.attach(LeftLegUpper)
LeftLegUpper.attach(LeftLegLower)
LeftLegLower.attach(LeftLegFoot)

hips.attach(RightLegUpper)
RightLegUpper.attach(RightLegLower)
RightLegLower.attach(RightLegFoot)

# show the created hierarchy
hips.printTree()
print('\nWorld positions, local positions, joint directions:')
for item, index, depth in hips.layout():
    print(f'{item.PositionWorld} {item.Position} {item.ForwardWorld} {item.Name}')

# --------------------------- OUTPUT ---------------------------
# Hips
# +- LeftLegUpper
# |  +- LeftLegLower
# |     +- LeftLegFoot
# +- RightLegUpper
#    +- RightLegLower
#       +- RightLegFoot

# World positions, local positions, joint direction:
# vec3(            0,            2,            0 ) vec3(            0,            2,            0 ) Hips
# vec3(          0.2,            2,            0 ) vec3(          0.2,            0,            0 ) LeftLegUpper
# vec3(          0.2,            1,            0 ) vec3(            0,           -1,            0 ) LeftLegLower
# vec3(          0.2,            0,            0 ) vec3(            0,           -1,            0 ) LeftLegFoot
# vec3(         -0.2,            2,            0 ) vec3(         -0.2,            0,            0 ) RightLegUpper
# vec3(         -0.2,            1,            0 ) vec3(            0,           -1,            0 ) RightLegLower
# vec3(         -0.2,            0,            0 ) vec3(            0,           -1,            0 ) RightLegFoot
```

### Interacting with transforms
``` python
from SpatialTransform import Transform

# the basic properties of the transform as position, scale and rotation can be changed by setting the value
# but the inverse-properties are read only
root = Transform()
root.PositionWorld = (1,2,3)
root.Scale = .1                     # accepts either a single value or a tuple of three
root.RotationWorld = (1, 0, 0, 0)   # rotations are in quaternions

# the rotation can be also read and changed with extra methods for simplified usage
root.setEuler((0, 90, 0))
root.getEuler(order='ZYX')
root.lookAtWorld((1, 1, 1))

# some methods do update the transform and keep childrens spatially unchanged
root.clearParent(keep=['position', 'rotation', 'scale'])
root.clearChildren(keep=['position', 'rotation', 'scale'])
root.applyPosition()
root.applyRotation(recursive=True)
root.appyScale(recursive=True)

# the transform provide two methods to convert arbitrary points and direction from and to the spaces
root.pointToWorld((5,4,3))
root.directionToLocal((2,3,4))
```

### Fluent interface usage
``` python
from SpatialTransform import Transform

# because almost every method on the "Transform" object returns itself,
# the previous code of creating and attaching can also be written like:
hips = Transform('Hips', position=(0,2,0)).attach(
    Transform('LeftLegUpper', position=(+0.2,0,0)).attach(
        Transform('LeftLegLower', position=(0,-1,0)).attach(
            Transform('LeftLegFoot', position=(0,-1,0))
        )
    ),
    Transform('RightLegUpper', position=(-0.2,0,0)).attach(
        Transform('RightLegLower', position=(0,-1,0)).attach(
            Transform('RightLegFoot', position=(0,-1,0))
        )
    )
)

# multiple actions on a transform can be performed on a single line
feets = hips.setEuler((0, 180, 0)).applyRotation().filter('Foot')

# show the created hierarchy
hips.printTree()
print('\nPositions:')
for item, index, depth in hips.layout():
    print(f'{item.PositionWorld} {item.Position} {item.Name}')

# --------------------------- OUTPUT ---------------------------
# Hips
# +- LeftLegUpper
# |  +- LeftLegLower
# |     +- LeftLegFoot
# +- RightLegUpper
#    +- RightLegLower
#       +- RightLegFoot

# Positions:
# vec3(            0,            2,            0 ) vec3(            0,            2,            0 ) Hips
# vec3(         -0.2,            2,  1.74846e-08 ) vec3(         -0.2,            0,  1.74846e-08 ) LeftLegUpper
# vec3(         -0.2,            1,  1.74846e-08 ) vec3(            0,           -1,            0 ) LeftLegLower
# vec3(         -0.2,            0,  1.74846e-08 ) vec3(            0,           -1,            0 ) LeftLegFoot
# vec3(          0.2,            2, -1.74846e-08 ) vec3(          0.2,            0, -1.74846e-08 ) RightLegUpper
# vec3(          0.2,            1, -1.74846e-08 ) vec3(            0,           -1,            0 ) RightLegLower
# vec3(          0.2,            0, -1.74846e-08 ) vec3(            0,           -1,            0 ) RightLegFoot
```

### Euler angles conversions
``` python
# the package also provides the static class 'Euler'
# the 'Transform' does also rely on that to convert between rotation representations
from SpatialTransform import Euler

# rotations are in radians here
matrix = Euler.toMatFrom((1, 2, .5), order='YZX', extrinsic=True)
quaternion = Euler.toQuatFrom((1, 2, .5), order='YZX', extrinsic=True)

angles1 = Euler.fromMatTo(matrix, order='XYZ', extrinsic=False)
angles2 = Euler.fromQuatTo(quaternion, order='XYZ', extrinsic=False)

print(angles1 - angles2)

# --------------------------- OUTPUT ---------------------------
# vec3(            0,            0,            0 )
```
