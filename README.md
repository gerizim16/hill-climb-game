# 2D physics-based arcade game

This game is made using **[pymunk](https://www.pymunk.org/)** physics in **[pyglet](https://bitbucket.org/pyglet/pyglet/wiki/Home)**. It is tested working on **python 3.7.0**. 

#  Third-party modules
The follwing are third-party modules used in this project.

## pyglet
Pyglet was used for the main structure of the game. It handles the main loop and keyboard and mouse event handling. It also acted as the camera for the physics engine module, pymunk. More information about pyglet is available at https://pyglet.readthedocs.io/. Its source code with examples is available at https://bitbucket.org/pyglet/pyglet/wiki/Home. Also, the module may be installed using the 
```
pip install pyglet 
```
command. This game works as of **pyglet 1.3.2**.

## pymunk
Pymunk is a 2D physics engine that is built on top of c-library, chipmunk. It was made to be “Pythonic” such that it works just like a python library. For this game, it was used for the physics engine only. Sprites and primitive drawing were handled by pyglet. Also, pymunk supports pyglet debugging using the submodule, 
```
pymunk.pyglet_util
```
This allows for fast prototyping by handling the drawing in pyglet. However, this is not optimized and should not be used for the final program. More information about pymunk is available at https://www.pymunk.org/. The module may be installed using the 
```
pip install pymunk 
```
command. This game works as of **pymunk 5.4.0**.

# Resources

- Royalty free looping background music (Breeze) found at https://www.youtube.com/watch?v=5GfW9eIGcpY.
- Sidescroller tileable background set made by https://bevouliin.com/ found at https://opengameart.org/users/bevouliincom. Used under the **CC0 1.0 Universal (CC0 1.0) Public Domain Dedication**. (no copyright)


