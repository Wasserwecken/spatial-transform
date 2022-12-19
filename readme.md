# spatial-transform

Libary for creating spatial space hierarchies, like game engines and renderes would do, to have diffrent rotations, scale and positions which can also rely on their parent.

This package was created for my master thesis and only aims about integrety but not performance. For the most of the calculations the package [PyGLM](https://github.com/Zuzu-Typ/PyGLM) is used.

## Install
```pip install spatial-transform```

## Features
- Transforms as stackable in form of trees.
- Transforms reactor to attaching and detaching.
- Support Translation, Rotation and Scale.
- Includes a static class for euler angle conversions.
- Space is defined as: Y+ is Up and right handed like openGL

## Examples


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
