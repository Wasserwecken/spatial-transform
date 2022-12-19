# spatial-transform
Libary for creating spatial space hierarchies, like game engines and renderes would do, to have diffrent rotations, scale and positions which also rely on their parent transformation.

This package is created for my master thesis and aims about integrety but not performance. For the most of the calculations the package [PyGLM](https://github.com/Zuzu-Typ/PyGLM) is used.

## Install
``` batch
pip install spatial-transform
 ```

## Notes
This libary works with the same space as [openGL and GLM](https://www.evl.uic.edu/ralph/508S98/coordinates.html), which is:
- right handed
- Y+ is up
- Z- is forward
- Positive rotation is counter clockwise

Euler angles can be set with methods on the transform.
- ``SetEuler()`` supports any instrinic or extrinsic rotation order
- ``GetEuler()`` supports any rotation order but intrinsic only

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
- Includes a static class for euler angle conversions.

## Examples
## Create and attach transforms
``` python
from SpatialTransform import Transform as T

# create and attach
root = T('Hips', position=(0,2,0)).attach(
    T('LeftLegUpper', position=(+.2, 0, 0)).lookAtLocal((0,-1,0)).attach(
        T('LeftLegLower', position=(0, 0, -1)).attach(
            T('LeftLegFoot', position=(0, 0, -1)).lookAtLocal((-1,0,0)))),
    T('RightLegUpper', position=(-.2, 0, 0)).lookAtLocal((0,-1,0)).attach(
        T('RightLegLower', position=(0, 0, -1)).attach(
            T('RightLegFoot', position=(0, 0, -1)).lookAtLocal((-1,0,0)))))

# print info about created structure
root.printTree()
for item, index, depth in root.layout():
    print(f'Position:{item.pointToWorld((0,0,0))} Forward:{item.ForwardWorld} {item.Name}')
```


### Create and stack transforms
```python
import SpatialTransform as st

root = st.Transform('root')
child1 = st.Transform('child1')

root.append(child1)
```
### Change properties
```python
import SpatialTransform as st

root = st.Transform('root')
root.Position = (1,2,3)
root.SetEuler((0, 45, 0))
root.Scale = (10, 10, 10)
root.Forward = (1, 1, 1)
```
### Read properties
```python
import SpatialTransform as st

root = st.Transform('root')
print(root.Position)
print(root.Rotation)
print(root.Scale)
print(root.ForwardLocal)
print(root.ForwardWorld)
print(root.UpLocal)
print(root.UpWorld)
print(root.RightLocal)
print(root.RightWorld)
print(root.SpaceLocal)
print(root.SpaceWorld)
```
### Convert between spaced
```python
import SpatialTransform as st

root = st.Transform('root')
print(root.pointToWorld((1,1,1)))
print(root.directionToLocal((1,1,1)))
```
