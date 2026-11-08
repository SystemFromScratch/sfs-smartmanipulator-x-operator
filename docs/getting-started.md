# Getting started

This guide takes you from two fresh clones to RViz2 planning motions for the
SmartManipulator-X arm. Everything runs in Docker on one computer: the Robot PC with
mock hardware (every commanded joint position becomes the joint state at once) and the
Operator PC on the same Docker network. No controller board and no arm are needed.

## Prerequisites

| Where | What |
| --- | --- |
| Windows 11 | Docker Desktop with the WSL 2 backend. RViz2 is shown through WSLg, which Docker Desktop shares with its containers |
| Linux desktop | Docker Engine and an X11 session (Wayland desktops with XWayland work too) |
| Both | Git, Docker Compose **v2.17 or later** (for `additional_contexts`) and BuildKit (the default) |
| Optional | VS Code |

ROS 2 is not installed on the host: it comes with the images
(`ros:jazzy-ros-base`). Check the Compose version with `docker compose version`.

## Clone both repositories side by side

The Operator PC image takes the robot description and the Fast DDS profile from the
Robot PC repository. By default it looks for it next to this repository, under the name
`SmartManipulator-X-Robot-PC`:

```bash
git clone https://github.com/SystemFromScratch/sfs-smartmanipulator-x-robot.git SmartManipulator-X-Robot-PC
git clone https://github.com/SystemFromScratch/sfs-smartmanipulator-x-operator.git SmartManipulator-X-Operator-PC
```

```text
SmartManipulator-X/
├── SmartManipulator-X-Robot-PC/       Robot PC: ros2_control, robot description, DDS profile
└── SmartManipulator-X-Operator-PC/    Operator PC: this repository
```

If the Robot PC checkout lives elsewhere, set `SMX_ROBOT_PC_REPO` in `docker/.env`
(see [Docker image and Compose](docker.md#environment)).

## 1. Start the Robot PC

In the Robot PC repository:

```bash
docker compose -f docker/docker-compose.yml up --build robot_pc
```

The first run builds the image, which takes several minutes. Compose creates the Docker
network `smx_net` (10.77.0.0/24), which stands in for the Ethernet link between the two
computers, and starts the Robot PC at 10.77.0.10 with `robot_state_publisher`,
`ros2_control_node` (mock hardware), `joint_state_broadcaster`, `arm_controller` and
`gripper_controller`. Leave the terminal open.

!!! note "Start the Robot PC first"
    The Operator PC declares `smx_net` as an **external** network. If the Robot PC has
    not created it yet, Compose stops with `network smx_net declared as external, but
    could not be found`.

## 2. Start the Operator PC

In this repository, in a second terminal:

```bash
docker compose -f docker/docker-compose.yml up --build operator_pc
```

The first build installs MoveIt 2, pick_ik and RViz2 on top of `ros:jazzy-ros-base` and
builds the workspace (several minutes). The container joins `smx_net` at 10.77.0.20 and
runs:

```bash
ros2 launch smartmanipulator_x_moveit_config operator.launch.py
```

which starts `move_group` and RViz2. The log of `move_group` ends with
`You can start planning now!` once it has received the robot state from the Robot PC.

## 3. Plan and execute

RViz2 opens with the **MotionPlanning** display, planning group `arm`: the current state
of the arm (as reported by the Robot PC) is opaque, the goal state is orange and
semi-transparent.

1. Drag the interactive marker at the gripper (`tool_link`) to a new position.
2. In the **Planning** tab, click **Plan & Execute**.
3. The Robot PC log shows `arm_controller` accepting and finishing the goal. The arm in
   RViz2 follows the `/joint_states` that come back from the Robot PC.

For the named poses, the gripper and the planning options, see
[Planning in RViz2](rviz.md).

## Shell on the same network

The `shell` service (profile `tools`) is a second container with the same image, network
and GUI setup, for the ROS 2 command line:

```bash
docker compose -f docker/docker-compose.yml run --rm shell
```

```bash
ros2 node list                    # /move_group, /rviz2 and the Robot PC nodes
ros2 control list_controllers     # arm_controller, gripper_controller, joint_state_broadcaster
ros2 topic echo /joint_states --once
glxgears                          # checks the display path
```

## Stop and rebuild

Stop with **Ctrl+C**, or remove the Operator PC containers (the network belongs to the
Robot PC project and stays):

```bash
docker compose -f docker/docker-compose.yml down
```

The workspace and the robot description are built **into** the image, not mounted.
After changing the MoveIt configuration here, or the robot description in the Robot PC
repository, start with `up --build` again.

## Next steps

- [Planning in RViz2](rviz.md): named poses, the gripper, planning options.
- [Architecture](architecture.md): which node runs where and what goes over DDS.
- [Network and DDS](network.md): two computers on a real network.
