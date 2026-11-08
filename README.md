# SmartManipulator-X Operator PC

Operator PC of [SmartManipulator-X](https://github.com/AntonVynohradov/SmartManipulator-X-Robot-PC): MoveIt 2 motion planning and RViz2 for a BCN3D Moveo arm whose stepper motors are driven by DYNAMIXEL-compatible controllers (SmartFusion2 now, Doppelstep later). ROS 2 Jazzy in Docker.

The Operator PC never talks to the motor controllers. It plans in MoveIt and sends the trajectories over ROS 2 DDS to the Robot PC, which runs `ros2_control`:

```text
Operator PC (this repository)                Robot PC (SmartManipulator-X-Robot-PC)
  RViz2 + MotionPlanning panel                 robot_state_publisher  -> /tf, /robot_description
  move_group (OMPL, pick_ik)  ── DDS ──>       ros2_control_node      -> /joint_states
    FollowJointTrajectory                       arm_controller, gripper_controller
                                                hardware: mock now, DYNAMIXEL bus later
```

## Repository layout

| Path | Content |
| --- | --- |
| `docker/Dockerfile` | `ros:jazzy-ros-base` with MoveIt 2, pick_ik, RViz2 |
| `docker/docker-compose.yml` | `operator_pc` (move_group + RViz2) and `shell` (profile `tools`) on the network `smx_net` |
| `docker/env.example` | Template for `docker/.env`: domain ID, address, Robot PC repository path, GUI settings |
| `ros2_ws/src/smartmanipulator_x_moveit_config/` | SRDF, kinematics, joint limits, controller mapping, launch file, RViz configuration |

The robot description is **not** copied into this repository. The image build takes `smartmanipulator_x_description` and the Fast DDS profile from the Robot PC repository (Compose `additional_contexts`, default `../../SmartManipulator-X-Robot-PC`, i.e. both repositories side by side), so both computers always use the same joints and transport settings.

## Requirements

- Docker Desktop with the WSL 2 backend on Windows 11 (RViz2 is shown through WSLg), or Docker Engine on a Linux desktop.
- Docker Compose v2.17 or later (for `additional_contexts`) and BuildKit (the default).
- The Robot PC repository checked out next to this one.

## Running on one computer

1. Start the Robot PC; it creates the network `smx_net` (in the Robot PC repository):

   ```bash
   docker compose -f docker/docker-compose.yml up --build robot_pc
   ```

2. Start the Operator PC (in this repository):

   ```bash
   docker compose -f docker/docker-compose.yml up --build operator_pc
   ```

3. In RViz2, drag the interactive marker at the gripper (`tool_link`), then **Plan & Execute** in the MotionPlanning panel. The Robot PC log shows `arm_controller` accepting the goal; the arm in RViz follows the `/joint_states` that come back from the Robot PC.

`docker compose -f docker/docker-compose.yml run --rm shell` opens a shell on `smx_net` with the same GUI setup, for example for `ros2 node list`, `rviz2` alone, or `glxgears` to check the display.

## Notes

- **Robot model.** The Moveo model in the Robot PC repository is generated from the BCN3D CAD (link lengths, joint axes, meshes, gripper linkage). Joint limits are still placeholders until measured on the real arm. The `cad_pose` group state is the pose of the CAD assembly.
- **5-DOF arm.** The arm cannot reach an arbitrary 6-D pose. `pick_ik` runs with `rotation_scale: 0.0` (position only) so the interactive marker always solves; see `config/kinematics.yaml`.
- **Collision matrix.** `config/smartmanipulator_x.srdf` disables adjacent links and the gripper parts against each other; the reasoning is in the file.
- **Native Windows ROS 2 cannot join.** Docker Desktop does not route multicast between Windows and `smx_net`; run every ROS 2 node in a container on that network.
- **Rendering.** `LIBGL_ALWAYS_SOFTWARE=1` (llvmpipe) is the default because it works on every host. For a Linux desktop, see the X11 section of `docker/env.example`.
- **Real Ethernet later.** When the Robot PC moves to its own board (Raspberry Pi CM4, Jetson), replace `smx_net` by `network_mode: host` on both sides; `ROS_DOMAIN_ID` and the DDS profile stay the same.

## License

Apache License 2.0, see [LICENSE](LICENSE).
