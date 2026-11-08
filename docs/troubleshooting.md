# Troubleshooting

Most problems fall into four groups: the containers cannot start, the GUI does not show,
the two computers do not see each other, or MoveIt plans but the Robot PC does not
execute. Start every diagnosis with a shell on the network:

```bash
docker compose -f docker/docker-compose.yml run --rm shell
```

## Normal messages

Two `ERROR` lines appear at every start and are harmless:

| Message | Meaning |
| --- | --- |
| `No 3D sensor plugin(s) defined for octomap updates` (`move_group`) | No depth camera is configured |
| `Action server: /recognize_objects not available` (`rviz2`) | No object recognition behind the *Detect* button of the Scene Objects tab |

## Start and build

| Symptom | Cause | Fix |
| --- | --- | --- |
| `network smx_net declared as external, but could not be found` | The Robot PC is not running, so `smx_net` does not exist | Start the Robot PC first (`up robot_pc` in its repository) |
| `additional_contexts` is rejected, or `unknown flag: --build-context` | Docker Compose older than v2.17, or BuildKit disabled | Update Docker Desktop / the Compose plugin; do not set `DOCKER_BUILDKIT=0` |
| `failed to compute cache key: "/ros2_ws/src/smartmanipulator_x/smartmanipulator_x_description": not found` | The Robot PC repository is not at `../SmartManipulator-X-Robot-PC` | Clone it side by side, or set `SMX_ROBOT_PC_REPO` in `docker/.env` |
| `Address already in use` for 10.77.0.20 | A second `operator_pc` container (for example from `run`) holds the fixed address | `docker compose -f docker/docker-compose.yml down`, then start once |
| `/entrypoint.sh: no such file or directory` | The script was checked out with CRLF line endings | The Dockerfile strips CR already; re-clone with `.gitattributes` in effect (LF) and rebuild |

## Display

| Symptom | Cause | Fix |
| --- | --- | --- |
| `could not connect to display :0` / `qt.qpa.xcb: could not connect` | The X11 socket is not mounted, or the wrong `DISPLAY` | Windows: Docker Desktop with WSL 2 backend and WSLg (Windows 11). Linux: set the X11 values in `docker/.env` and run `xhost +local:docker` |
| `Authorization required, but no authorization protocol specified` | The X server refuses the container | Linux: `xhost +local:docker` in the desktop session |
| Window opens, but the 3D view is black or RViz2 crashes on start | OpenGL driver problem | Keep `SMX_LIBGL_ALWAYS_SOFTWARE=1` (default); test with `glxgears` in the `shell` service |
| RViz2 is slow | Software rendering on few cores | Expected with llvmpipe; set up a GPU path and `SMX_LIBGL_ALWAYS_SOFTWARE=0`, or close other displays |

## Discovery and data

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ros2 node list` shows only the local nodes | Different `ROS_DOMAIN_ID`, or not on the same network | Same domain on both sides (default 42); both containers on `smx_net` (`docker network inspect smx_net`) |
| Nodes are listed, but `ros2 topic echo /joint_states` stays silent | Fast DDS chose shared memory between containers | Check `FASTDDS_DEFAULT_PROFILES_FILE=/etc/smx/fastdds_udp.xml` on both sides; rebuild the image if the file is missing |
| Native Windows ROS 2 does not see the containers | Docker Desktop does not route multicast between Windows and container networks | Use the `shell` service instead |
| Discovery works on one computer, not on two | Firewall or different subnets | Allow UDP between the hosts, same subnet, see [Network and DDS](network.md#two-computers-real-ethernet) |

## Planning and execution

| Symptom | Cause | Fix |
| --- | --- | --- |
| `move_group` waits with `Didn't receive robot state (joint angles) with recent timestamp` | No `/joint_states` from the Robot PC | Check the Robot PC is running and the discovery checks above |
| The robot in RViz2 does not move after Execute | The Robot PC did not accept the goal | Look at the Robot PC log; `ros2 control list_controllers` must show `arm_controller` active |
| `Unable to identify any set of controllers that can actuate the specified joints` | Controller names or joints differ between `moveit_controllers.yaml` and the Robot PC's `controllers.yaml` | Make them identical; rebuild |
| `Action client not connected to action server: arm_controller/follow_joint_trajectory` | The controller is not running, or DDS does not deliver actions | `ros2 action list` in the `shell`; restart the Robot PC |
| Execution aborted: start state deviates | The arm is more than 0.02 rad away from the plan's start | Plan again from the current state (*Start State* `<current>`) |
| Execution aborted after a time | The trajectory took longer than 1.5 × planned + 1 s | Lower the speed scaling, or check the Robot PC controller (100 Hz) is not overloaded |
| The marker does not follow, goal turns red | No IK solution: the position is out of reach, or the goal is in collision | Move the marker closer to the base; check joint limits |
| Rotating the marker does nothing | Expected: the IK ignores orientation (`rotation_scale: 0.0`) | See [kinematics](moveit-config.md#kinematics) |
| `Planning failed` for reachable goals | OMPL found no path in the planning time, or the start state is in collision | *Planning Time* up in the Context tab; *Start State* `<current>`; check the collision matrix |

## Model mismatch

If the arm in RViz2 and the Robot PC disagree (different joints, a missing link, errors
about unknown joints), the two images were built from different versions of the robot
description. Rebuild both from the same Robot PC commit:

```bash
# in the Robot PC repository
docker compose -f docker/docker-compose.yml up --build robot_pc
# in this repository
docker compose -f docker/docker-compose.yml up --build operator_pc
```
