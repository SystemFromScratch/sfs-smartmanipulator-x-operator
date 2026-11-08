# MoveIt 2 configuration

`smartmanipulator_x_moveit_config` is the only ROS 2 package of the Operator PC. It holds
the semantic description, the kinematics, the planning limits, the controller mapping, the
launch file and the RViz2 layout. The robot description itself (URDF/Xacro, meshes) comes
from the Robot PC repository.

The configuration is loaded with `MoveItConfigsBuilder` in `launch/operator.launch.py`:

| Builder call | File |
| --- | --- |
| `robot_description` | `smartmanipulator_x_description/urdf/smartmanipulator_x.urdf.xacro` (Robot PC) |
| `robot_description_semantic` | `config/smartmanipulator_x.srdf` |
| `robot_description_kinematics` | `config/kinematics.yaml` |
| `joint_limits` | `config/joint_limits.yaml` |
| `trajectory_execution` | `config/moveit_controllers.yaml` |
| `planning_pipelines` | `ompl` only, default `ompl` (MoveIt's default OMPL settings) |
| `planning_scene_monitor` | publishes the robot description, the semantic description, the planning scene, geometry, state and transform updates |

## Semantic description (SRDF)

`config/smartmanipulator_x.srdf`. Link and joint names come from
`smartmanipulator_x_description`.

### Planning groups

| Group | Definition | Joints |
| --- | --- | --- |
| `arm` | chain `base_link` → `tool_link` | `j1_base`, `j2_shoulder`, `j3_elbow`, `j4_forearm_roll`, `j5_wrist` |
| `gripper` | joint `gripper` | `gripper` (the other gripper joints mimic it) |

The end effector `gripper` is attached to `link5`, with `arm` as parent group.

### Named states

| Group | State | `j1_base` | `j2_shoulder` | `j3_elbow` | `j4_forearm_roll` | `j5_wrist` |
| --- | --- | --- | --- | --- | --- | --- |
| `arm` | `home` | 0 | 0 | 0 | 0 | 0 |
| `arm` | `ready` | 0 | 0.5 | 0.8 | 0 | 0.6 |
| `arm` | `cad_pose` | 0 | 0.7416 | 0.4674 | 0.1426 | 0.9151 |

| Group | State | `gripper` |
| --- | --- | --- |
| `gripper` | `open` | 0.0 |
| `gripper` | `closed` | 1.4 |

Values in rad. `cad_pose` is the pose of the BCN3D CAD assembly from which the robot
description was generated.

### Collision matrix

The SRDF disables collision checking only where contact is part of the design:

- **Adjacent links:** `base_link`–`link1`, `link1`–`link2`, `link2`–`link3`,
  `link3`–`link4`, `link4`–`link5`, and `link5` against every gripper part.
- **Gripper parts against each other** (`servo_gear`, `idler_gear`, `pivot_left`,
  `pivot_right`, `finger_left`, `finger_right`): gears, pivot arms and fingers touch by
  design.

All other pairs are checked. The convex-hull collision meshes of the description overlap
nowhere else at the zero, `ready` and CAD assembly poses (checked with
`tools/cad/collide.py` in the Robot PC repository). Re-check after the description
changes, and add a pair only with its reason.

## Kinematics

`config/kinematics.yaml` — pick_ik for the `arm` group:

| Parameter | Value | Meaning |
| --- | --- | --- |
| `kinematics_solver` | `pick_ik/PickIkPlugin` | |
| `kinematics_solver_timeout` | 0.05 s | Per IK call |
| `kinematics_solver_attempts` | 3 | |
| `mode` | `global` | Global search (finds solutions far from the seed) |
| `position_scale` | 1.0 | The tool position counts fully |
| `rotation_scale` | **0.0** | The tool orientation is ignored |
| `position_threshold` | 0.001 m | A solution must be within 1 mm |
| `orientation_threshold` | 0.01 rad | Not relevant with `rotation_scale` 0 |
| `cost_threshold` | 0.001 | |
| `minimal_displacement_weight` | 0.0 | No preference for small joint motions |
| `gd_step_size` | 0.0001 | Gradient descent step |

**Why position-only:** the Moveo has five arm joints, so it cannot reach an arbitrary 6-D
pose. With a full pose goal, most marker positions in RViz2 would have no solution. With
`rotation_scale: 0.0` the marker always solves for the tool position. For a best-effort
orientation, raise `rotation_scale` (for example to 0.5): pick_ik then trades position and
orientation error, and the result may miss the position by more than 1 mm.

## Joint limits

The position and velocity limits come from the robot description (all arm joints and
the gripper: 1.0 rad/s). `config/joint_limits.yaml` adds what the URDF cannot express:

| Setting | Value |
| --- | --- |
| `default_velocity_scaling_factor` | 0.3 |
| `default_acceleration_scaling_factor` | 0.3 |
| `max_velocity` (every joint) | 1.0 rad/s |
| `max_acceleration` (every joint) | 1.0 rad/s² |

The default scaling factors apply to requests that do not set their own scaling, for
example from scripts. The RViz2 MotionPlanning panel always sends its own *Velocity
Scaling* and *Accel. Scaling*, which start at 0.10 (see
[Planning in RViz2](rviz.md#8-speed-of-the-motion)).

| Joint | Position limits in the description (rad) |
| --- | --- |
| `j1_base` | −π … π |
| `j2_shoulder` | −π/2 … π/2 |
| `j3_elbow` | −π/2 … π/2 |
| `j4_forearm_roll` | −π … π |
| `j5_wrist` | −π/2 … π/2 |
| `gripper` | 0 … 1.45 |

!!! warning "Placeholders"
    All limits are placeholders until the Moveo axes are measured on the real arm. Update
    the position and velocity limits in the robot description (Robot PC repository) and
    the accelerations here, then rebuild both images.

## Controllers

`config/moveit_controllers.yaml` maps the planning groups to the action servers of the
Robot PC. The names must match `controllers.yaml` of the Robot PC repository.

| MoveIt controller | Type | Action | Joints |
| --- | --- | --- | --- |
| `arm_controller` | `FollowJointTrajectory` | `arm_controller/follow_joint_trajectory` | `j1_base` … `j5_wrist` |
| `gripper_controller` | `FollowJointTrajectory` | `gripper_controller/follow_joint_trajectory` | `gripper` |

Both are `default: true`. The controller manager is `MoveItSimpleControllerManager`: it
only needs the action servers, no access to the Robot PC's controller manager.

| Execution setting | Value | Effect |
| --- | --- | --- |
| `allowed_execution_duration_scaling` | 1.5 | Execution may take 1.5 × the planned duration… |
| `allowed_goal_duration_margin` | 1.0 s | …plus 1 s, then MoveIt cancels it |
| `allowed_start_tolerance` | 0.02 rad | The arm must start within this of the plan's first point |

On the Robot PC side, `arm_controller` and `gripper_controller` are
`joint_trajectory_controller/JointTrajectoryController` with a `position` command
interface and `position` + `velocity` state interfaces, at 100 Hz.

## Launch file

`launch/operator.launch.py` starts two nodes:

| Node | Parameters | Condition |
| --- | --- | --- |
| `move_group` (`moveit_ros_move_group`) | the complete MoveIt configuration | always |
| `rviz2` | `-d rviz/moveit.rviz`; robot description, semantic description, kinematics, planning pipelines, joint limits | `rviz:=true` (default) |

```bash
ros2 launch smartmanipulator_x_moveit_config operator.launch.py            # move_group + RViz2
ros2 launch smartmanipulator_x_moveit_config operator.launch.py rviz:=false  # move_group only
```

## Changing the configuration

1. Edit the files under `ros2_ws/src/smartmanipulator_x_moveit_config/`.
2. Rebuild and restart: `docker compose -f docker/docker-compose.yml up --build operator_pc`
   (the package is built into the image).
3. If joint names, groups or controllers change, change the Robot PC (`controllers.yaml`,
   the description) in the same step, and rebuild both images.
