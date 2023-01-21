> This is under active development and changes can appear at anypoint. Feel free to create issues. If other people start using this i will start creating tests and a branching strategy. This package is created for my master thesis and aims for integrety but not for performance.

# spatial-transform
Lightweight libary for creating spatial space hierarchies, to have diffrent rotations, scale and positions which also rely on their parent transforms. This is inteded to be used like transform objects in game engines like Unity or Unreal. The package [PyGLM](https://github.com/Zuzu-Typ/PyGLM) is used for the matrix, quaternion and vector calculations.


## Install
``` batch
pip install spatial-transform
 ```
## Features
- Space properties in local and world space
    - Position
    - Rotation (Quaternion & Euler)
    - Scale
    - Space 4x4 matrix
    - Axes direction (Forward, Up, Right)
- Hierarchical
    - Transforms can have a parent and children
    - World space depends on the parent
    - Transforms can be easily attached / detachatched
- Python
    - Every method is documented in code with docstrings
    - Every method has type hinting
    - ([Fluent Interface](https://de.wikipedia.org/wiki/Fluent_Interface)) design
- Includes a static class for euler angle conversions.

## Notes
This libary uses the same coordination space as [openGL and GLM](https://www.evl.uic.edu/ralph/508S98/coordinates.html), which is:
- right handed
- Y+ is up
- Z- is forward
- Positive rotation is counter clockwise

Euler angles can be set with methods on the transform. ``SetEuler()`` and ``GetEuler()``. They support any instrinic or extrinsic rotation order. Angles are degrees in the ``Transform`` class but radians in the ``Euler`` class.

## Examples and code

### Create and attach transforms
``` python
from SpatialTransform import Transform

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
print('\nPositions:')
for item, index, depth in hips.layout():
    print(f'{item.PositionWorld} {item.PositionLocal} {item.Name}')

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
root.ScaleLocal = .1                # accepts either a single value or a tuple of three
root.RotationWorld = (1, 0, 0, 0)   # rotations are in quaternions

# the rotation can be also read and changed with extra methods for simplified usage
root.setEuler((0, 90, 0))
root.getEuler(order='ZYX')
root.lookAtWorld((1, 1, 1))

# some methods do update the transform and keep childrens spatially unchanged
root.clearParent(keepPosition=True, keepRotation=True, keepScale=True)
root.clearChildren(keepPosition=True, keepRotation=True, keepScale=True)
root.applyPosition()
root.applyRotation(recursive=True)
root.appyScale(recursive=True, includeLocal=True)

# the transform provide two methods to convert arbitrary points and direction from an to the spaces
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
    print(f'{item.PositionWorld} {item.PositionLocal} {item.Name}')

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
