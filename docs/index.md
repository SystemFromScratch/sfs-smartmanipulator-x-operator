---
title: SmartManipulator-X Operator PC — motion planning for a ROS 2 robot arm
description: MoveIt 2 and RViz2 for the SmartManipulator-X arm, ROS 2 Jazzy in Docker, connected to the Robot PC over ROS 2 DDS.
template: home.html
hide:
  - navigation
  - toc
---

<span class="sfs-eyebrow">Quick start</span>

## Plan a motion in three steps

No board and no arm are needed: the Robot PC runs `ros2_control` with mock hardware in
Docker, and the Operator PC joins it on the same Docker network. Clone both repositories
side by side — the Operator PC image takes the robot model from the Robot PC repository.

```bash
git clone https://github.com/SystemFromScratch/sfs-smartmanipulator-x-robot.git SmartManipulator-X-Robot-PC
git clone https://github.com/SystemFromScratch/sfs-smartmanipulator-x-operator.git SmartManipulator-X-Operator-PC

# terminal 1: the Robot PC (creates the network smx_net)
cd SmartManipulator-X-Robot-PC
docker compose -f docker/docker-compose.yml up --build robot_pc

# terminal 2: the Operator PC (move_group + RViz2)
cd SmartManipulator-X-Operator-PC
docker compose -f docker/docker-compose.yml up --build operator_pc
```

RViz2 opens with the MotionPlanning panel. Drag the interactive marker at the gripper,
click **Plan & Execute**, and the Robot PC log shows `arm_controller` accepting the goal;
the arm in RViz2 follows the `/joint_states` that come back over DDS
([Planning in RViz2](rviz.md)).

## Find your way

| If you want to… | Read |
| --- | --- |
| Understand what the Operator PC is and where it sits in SmartManipulator-X | [Overview](overview.md) |
| Run the Operator PC together with the Robot PC | [Getting started](getting-started.md) |
| Plan and execute motions, use the named poses | [Planning in RViz2](rviz.md) |
| See the nodes, topics and actions across both computers | [Architecture](architecture.md) |
| Change planning groups, kinematics, limits or controllers | [MoveIt 2 configuration](moveit-config.md) |
| Change the image, the services or the GUI setup | [Docker image and Compose](docker.md) |
| Connect over a real network or another domain | [Network and DDS](network.md) |
| Fix a black window, a missing robot or a rejected trajectory | [Troubleshooting](troubleshooting.md) |
| Read about the Robot PC, the controller firmware and the hardware | [SmartManipulator-X system documentation](https://systemfromscratch.github.io/sfs-smartmanipulator-x-robot/) |
| Read everything offline or print it | [PDF user manual](https://systemfromscratch.github.io/sfs-smartmanipulator-x-operator/downloads/SmartManipulator-X_Operator_PC_User_Manual.pdf) |
