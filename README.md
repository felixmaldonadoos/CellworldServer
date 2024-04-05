# Adverserial Dynamics in Virtual Reality 


### Project Overview
[**Control a Mouse (Prey) in VR**]
This Virtual-Reality game maps your movement to a real robot in pursuit of a mouse. The purpose of this project is to elicit planning behaviors from mice as they evade a hostile predator in the form of a robot

[**Planning Perspective**]
The purpose of these experiments are to understand planning within mammals. We elicit this behavior in mice by having the mice evade a predator in the form of a robot that emits compressed air when the mice gets too close. This experimental paradigm is based on the ```paper link``` from the ```MacIver Lab at Northwestern University ```
 
One of the problems with the current experiment is that the autonomous robot is purely reactive. When we have a mouse that can outrun the robot, the robot itself needs to start planning in order to better simulate a predator. This is the purpose behind my project, to use a real-time planning agent to control the robot. And what better planning agent than a human!


[**The Task**]
Originally, we have an autonomous robot predator that chases after a mouse. It will move towards non-visible locations until it sees the mouse. After it spots the mouse, it will begin chasing after it. At any point, if it loses sight of the mouse, it will go to the last known location.
<!-- ![Task Diagram](images/task_logic_sq.png) -->


## Robotics Control
<div style="text-align: center;" markdown="1">
   <img src="images/robot_ctrl_2x.gif" alt="2x Speed of Robot Moving"/>
</div>
&nbsp

<div style="text-align: center;" markdown="1">
   <img src="images/robot_sq.png" alt="Breakdown of the Robot"/>
   <figcaption> The Skid Steer Drive Robot, designed by Gabrielle Wink and Dr. Angel Germán Espinosa Coarasa. Image Credits: Lai, et al. (2024). A robot-rodent interaction arena with adjustable spatial complexity for ethologically relevant behavioral studies. Cell Report
</div>
&nbsp

Here’s what the Robot looks like. It’s a skid steer robot, that has two sets of wheels that drive a pair of treads.There are two PCB’s on the robot, one with an ESP32 microcontroller that controls the wheel speed commands, and another PCB   that control three LED’s that are used to track the location of the robot.

<div style="text-align: center;" markdown="1">
   <img src="images/robot_ctrl_diagram.png" alt="Breakdown of the Control of the Robot"/>
   <figcaption> [How Does the Robot Move to a Destination?]
</div>  
&nbsp

The robot receives instructions on where to move from a nearby server, which also holds the tracking information. These are converted into wheel commands that the robot can follow.

## Virtual-Reality
<div style="text-align: center;" markdown="1">
   <img src="images/virtual_arena.png" alt="The Virtual Arena"/>
   <figcaption> Virtual Habitat
</div>
&nbsp
<div style="text-align: center;" markdown="1">
   <img src="images/nav_mesh.png" alt="Navigation Mesh Area"/>
   <figcaption> Depicts the area the real robot and mouse can move
</div>
&nbsp

The Virtual Habitat is a 20-meter-long recreation of the Habitat. As with the original Habitat, you can add in Occlusions - hexagonal obstacles that occlude the view of the mouse. The Virtual Habitat is designed for a player to run in an open field to create a more immersive experience.

Because the Virtual Habitat is designed for a larger environment, there needs to be a way to convert Virtual-Reality Coordinates to Canonical - the coordinates of the Habitat.

Inside the game is a function to convert the Virtual-Reality Coordinates to Canonical and vice-versa. 

The location of the VR Headset is always tracked - and as the player moves around the world, their coordinates are translated and sent to a server 

In the event that the user spawns outside of the arena, there is a **soft-reset** button, that will **reset the orientation, position, yaw, and height** of the player. This is mapped to "X" on the Motion Controller. To reset the entire game, or **hard-reset the game**, the player can press "Y". 

Occlusions are added into the Blueprint of the game itself. Simply specify which Occlusion you want to spawn by giving the location of the file containing the location indicies. 


## Networking
![Networking Diagram](images/networking_diagram.jpg)

Networking is made possible using the TCP Messages Library written by Dr. Angel Germán Espinosa Coarasa. It allows for a **client-server** type of communication. In this case, the Virtual-Reality game is the client, and a server running on the Habitat PC receives all of the information from the client. The server broadcasts out messages, like the tracking information, out to its subscribed clients.

I created a few small scripts in TCPTest, as a way of testing out the communication between the Virtual-Reality world and the server. TCPTest simulates the server itself, intercepting and interpreting messages. This helped confirm that the communication was working end to end. All of TCPTest was written using the TCP Messages library.

As previously mentioned, TCP messages allows the the user to send messages, requests and responses and subscribe to a server. It allows for even more functionality by adding in custom functions. This is similar to the functions that exist in ROS nodes, which allow the user to define specific functionality.
 
[In order to allow Port Forwarding Script to Work]
Set-ExecutionPolicy -ExecutionPolicy Unrestricted

## Step-Up Module
![Step-Up Module Diagram](images/step_up_diagram.png)

**Overview:** The Step-Up Module is a *DC-to-DC converter that steps up 12V from the Virtual Reality (VR) backpack to 19.5V required by the VR Headset*. 
Because there isn't a proprietary cable that connects the HP Reverb G2 VR backpack to the HP Reverb G2 Headset, I made my own!

**Why?** Our Experiment requires a mobile agent moving in a large environment, which required us to extricate ourselves from a tethered power connection. This is because the Virtual Reality gear - the Headset and Backpack - requires a connection to an outlet..

**How it Works:** As mentioned previously, this DC-to-DC converter takes 12V from the VR backpack steps it up to 19.5V, and goes into the headset. This allows the backpack and headset to be completely untethered to a wall outlet.   

### Step-Up Module Bill of Materials
Here is the Bill of Materials as well as pictures depicting how the step-up module is assembled. Not depicted are the spacers and screws necessary, as well as the DC-DC step-up converter itself. 

Lastly is the fully assembled Step-Up Module

[Step-Up Module BoM](https://docs.google.com/spreadsheets/d/1b9FdkY2aQWLmUtxk2oAGR2HAnpVTHtHQpYreBFGOhEA/edit?usp=sharing)

#### Assembly of the Step-Up Module
![Assembly of the Step-Up Module](images/assembly_1.jpg)

#### Assembly with Numbered Parts
![Assembly with numbered parts](images/assembly_2.jpg)

#### Fully Assembled Step-Up Module
![Fully Assembled Module](images/full_assembly.jpg)

### Acknowledgements
Angel Germán Espinosa Coarasa, Gabrielle Wink, Alex Lai, Chris Angeloni, Felix Alexander Maldonado, Selim Chalyshkan, Joe Reed,  Joshua Chi, and of course Dr. MacIver

Further acknowledgement goes towards the MacIver Lab for several figures, which will be available in, Lai, et al. (2024) . A robot-rodent interaction arena with adjustable spatial complexity for ethologically relevant behavioral studies. Cell Reports