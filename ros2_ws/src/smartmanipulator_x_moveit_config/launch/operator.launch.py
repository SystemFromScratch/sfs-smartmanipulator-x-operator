# Copyright 2026 Anton Vynohradov
# SPDX-License-Identifier: Apache-2.0
"""Operator PC: move_group and RViz2 with the MotionPlanning panel.

    ros2 launch smartmanipulator_x_moveit_config operator.launch.py

The Robot PC provides /joint_states, TF (robot_state_publisher) and the
FollowJointTrajectory action servers of arm_controller and
gripper_controller. Nothing here talks to hardware.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    description_xacro = os.path.join(
        get_package_share_directory("smartmanipulator_x_description"),
        "urdf",
        "smartmanipulator_x.urdf.xacro",
    )

    moveit_config = (
        MoveItConfigsBuilder("smartmanipulator_x", package_name="smartmanipulator_x_moveit_config")
        # Same model as the Robot PC; the hardware block is irrelevant to MoveIt.
        .robot_description(file_path=description_xacro, mappings={"use_mock_hardware": "true"})
        .robot_description_semantic(file_path="config/smartmanipulator_x.srdf")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .planning_scene_monitor(
            publish_robot_description=True,
            publish_robot_description_semantic=True,
            publish_planning_scene=True,
            publish_geometry_updates=True,
            publish_state_updates=True,
            publish_transforms_updates=True,
        )
        .to_moveit_configs()
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    rviz_config = os.path.join(
        get_package_share_directory("smartmanipulator_x_moveit_config"), "rviz", "moveit.rviz",
    )
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
        condition=IfCondition(LaunchConfiguration("rviz")),
    )

    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true", description="Start RViz2."),
        move_group,
        rviz,
    ])
