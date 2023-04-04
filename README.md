# PAL Gazebo worlds

This package contains customized world and models that were used for demonstration and events

Worlds and models are using the sdf format; for further information please refer to this website: http://sdformat.org/spec

## Warning

All the worlds are not meant to work perfectly

They can be used for all the robots but it can happen that the robot spawn inside the wall in some configuration

To prevent this from happening you can use the gzpose argument of the robot_gazebo.launch file, for example in the pal_kitchen world with TIAGo:

roslaunch tiago_gazebo tiago_gazebo.launch world:=pal_kitchen gzpose:="-x -1.0 -y 3.0 -z 0.0 -R 0.0 -P 0.0 -Y 0.0"

## World and models

The main folders are the models and the worlds folders:

 - The model folder contains all the models folder with inside at least the model.config and the <object>.sdf. The model.config contains the information about the model and the link to the .sdf file.

 - The worlds folder contains all the .world files

You would find an example of a world and a model under models/custom_object and worlds/custom_world.worlds in order to understand better how to create your own world from what is available and also import new models