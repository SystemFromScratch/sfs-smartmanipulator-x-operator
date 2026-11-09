#******************************************************************************
# SmartManipulator-X: Operator PC
#
# Description: Generates the figures of the documentation:
#                docs/assets/images/hero-3d.svg       animated isometric hero
#                docs/assets/images/ros-graph.svg      ROS 2 graph across both PCs
#                docs/assets/images/image-build.svg    build contexts of the image
#              Run after a change:
#                  python tools/docs/diagrams.py [--no-hero]
#              The hero draws the real arm from the robot description of the
#              Robot PC repository (SMX_ROBOT_PC_REPO, default: next to this one).
#
# Author:      Anton Vynohradov
# Email:       contact@systemfromscratch.com
# License:     Apache License 2.0
# Copyright (c) 2026 Anton Vynohradov
#
# SPDX-License-Identifier: Apache-2.0
#*****************************************************************************

"""Figures of the SmartManipulator-X Operator PC documentation, built with svgkit.

The hero shows what the Operator PC does differently from the rest of the system: an
operator plans a motion in MoveIt 2 and RViz2 (the planned path on the screen), the
trajectory goes over ROS 2 DDS to the Robot PC (blue packets) and the joint states come
back (green packets); the real arm follows, and its planned tool path glows above it.
The arm and the tool path come from the robot description (URDF + visual meshes) by
forward kinematics (hero_robot.py).

Moving parts start with opacity 0 or at their first pose, because WeasyPrint (PDF cover)
does not run SVG animation. Needs numpy and Pillow (requirements-docs.txt)."""

from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hero_robot import Placement, Robot, smooth_poses, svg_frames  # noqa: E402
from svgkit import (BLUE, GREEN, GREY, HERO_DEFS, HERO_STYLE, LIGHT, LINE, NAVY,  # noqa: E402
                    ORANGE, TEAL, WHITE, Iso, Svg)

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                    "docs", "assets", "images"))

ARM_LIGHT = "#c9d6ea"
ARM_MID = "#8aa0bf"
ARM_DARK = "#6f86a6"
BOX_TOP = "#1b2a40"
BOX_LEFT = "#131f31"
BOX_RIGHT = "#0e1726"
EDGE = "#2a4870"
ACCENT = "#2f8cff"
GLOW = "#5ea6ff"
REPLY = "#3fcf8e"

HERO_LABEL = ("SmartManipulator-X Operator PC: MoveIt 2 and RViz2 plan a motion on the "
              "operator workstation, the trajectory goes over ROS 2 DDS to the Robot PC, the "
              "joint states come back, and the BCN3D Moveo arm follows the planned tool path")


# ==============================================================================
# HERO
# ==============================================================================

SCREEN_Y = 1.36          # front face of the monitor (the face the viewer sees)


def workstation(iso: Iso) -> None:
    """Desk with a monitor showing the MotionPlanning view and a keyboard."""
    p = iso.p
    iso.box(0.0, 5.4, 0.0, 4.6, -0.4, 0.0, "url(#boardTop)", "#0a1628", "#071122", "#1e3a66", 1.2)
    # monitor foot and neck
    iso.box(2.2, 3.2, 0.7, 1.7, 0.0, 0.12, ARM_MID, ARM_DARK, "#5a6f8b")
    iso.box(2.55, 2.85, 1.0, 1.25, 0.12, 0.9, ARM_MID, ARM_DARK, "#5a6f8b")
    # panel
    iso.box(0.5, 4.9, 1.0, SCREEN_Y, 0.7, 3.9, BOX_TOP, BOX_LEFT, BOX_RIGHT, EDGE, 1.2)
    y = SCREEN_Y + 0.001
    iso.parts.append(iso.poly([p(0.7, y, 0.9), p(4.7, y, 0.9), p(4.7, y, 3.7), p(0.7, y, 3.7)],
                              "#071a33", "#1e3a66", 1.0))
    # grid of the RViz view
    for gx in (1.5, 2.3, 3.1, 3.9):
        iso.path([p(gx, y, 1.0), p(gx, y, 2.9)], "#13325c", 0.8)
    for gz in (1.4, 1.9, 2.4):
        iso.path([p(0.8, y, gz), p(4.6, y, gz)], "#13325c", 0.8)
    # planned path: start state, goal state and the trajectory between them
    arc = [p(1.2 + 3.0 * t, y, 1.25 + 1.45 * math.sin(math.pi * t)) for t in np.linspace(0, 1, 24)]
    iso.path(arc, "#0e2a4f", 4.5)
    iso.path(arc, GLOW, 1.8, ' class="flow"')
    for (sx, sy), color in ((arc[0], REPLY), (arc[-1], "#ffb347")):
        iso.parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.6" fill="{color}" '
                         f'filter="url(#glow)"/>')
    iso.text(2.7, y, 3.35, "MOVEIT 2 · RVIZ2", 0.26, "#e6edf7", 800, 0.05, face="y")
    iso.text(2.7, y, 3.03, "PLAN & EXECUTE", 0.18, GLOW, 700, 0.08, face="y")
    # keyboard
    iso.box(1.0, 4.2, 2.3, 3.4, 0.0, 0.14, "#14243c", "#0c182b", "#09121f", EDGE)
    for row in range(3):
        yy = 2.5 + row * 0.32
        iso.path([p(1.2, yy, 0.15), p(4.0, yy, 0.15)], "#22344f", 1.6)
    iso.text(2.7, 4.2, 0.01, "OPERATOR PC", 0.34, "#e6edf7", 800, 0.04)
    iso.led(4.9, 4.4, -0.2)


def dds_link(iso: Iso) -> None:
    """Network cable from the workstation to the Robot PC: a trajectory goes out
    (blue), the joint states come back (green)."""
    p = iso.p
    cable = [p(5.4, 2.6, -0.2), p(6.0, 2.6, -0.35), p(8.6, 2.6, -0.35), p(9.2, 2.6, -0.2)]
    iso.path(cable, "#0e2a4f", 7)
    iso.path(cable, ACCENT, 2.2, ' opacity="0.9"')
    start, stop = p(5.8, 2.6, 0.2), p(8.8, 2.6, 0.2)
    track = f"M{start[0]:.1f},{start[1]:.1f} L{stop[0]:.1f},{stop[1]:.1f}"
    iso.text(7.3, 2.6, 0.75, "ROS 2 DDS", 0.26, "#9aabc4", 700, 0.05, face="y")
    for color, glow, motion, visible in ((ACCENT, "#9cc8ff", "0;1;1;1", "0;1;1;0;0;0"),
                                         (REPLY, "#a6f0cb", "1;1;1;0", "0;0;0;1;1;0")):
        cubes = "".join(f'<rect x="{-11 + k * 8}" y="-3.5" width="6.5" height="6.5" rx="1.3" '
                        f'fill="{color}" stroke="{glow}" stroke-width="0.8" '
                        f'transform="skewY(30)"/>' for k in range(3))
        iso.parts.append(
            f'<g opacity="0" filter="url(#glow)">{cubes}'
            f'<animateMotion dur="4s" repeatCount="indefinite" path="{track}" '
            f'keyPoints="{motion}" keyTimes="0;0.35;0.55;1" calcMode="linear"/>'
            f'<animate attributeName="opacity" dur="4s" repeatCount="indefinite" '
            f'values="{visible}" keyTimes="0;0.05;0.33;0.4;0.95;1"/></g>')


def robot_pc(iso: Iso) -> None:
    """The Robot PC that runs ros2_control."""
    iso.box(9.2, 12.6, 1.0, 4.2, -0.4, 1.1, BOX_TOP, BOX_LEFT, BOX_RIGHT, EDGE, 1.2)
    for i in range(5):
        y = 1.4 + i * 0.55
        iso.path([iso.p(9.6, y, 1.11), iso.p(10.6, y, 1.11)], "#22344f", 1.6)
    iso.text(11.6, 2.0, 1.11, "ROBOT PC", 0.32, "#e6edf7", 800, 0.04)
    iso.text(11.6, 3.0, 1.11, "ROS2_CONTROL", 0.2, GLOW, 600, 0.06)
    iso.led(12.4, 4.2, 0.7)
    iso.led(12.0, 4.2, 0.7, "led-rx", GLOW, 2.4)
    # motor cable to the arm
    cable = [iso.p(12.6, 2.6, 0.1), iso.p(13.2, 2.6, -0.3), iso.p(14.6, 2.6, -0.3),
             iso.p(15.0, 2.6, 0.1)]
    iso.path(cable, "#0e2a4f", 8)
    iso.path(cable, ACCENT, 2.4, ' opacity="0.85"')
    iso.path(cable, "#9cc8ff", 2.2, ' class="flow-bus"')


# Poses of the real arm (joint values in rad, joint names of the robot description). The
# animation runs from START to STOP and back; the first pose is the static picture.
ARM_START = {"j1_base": -0.45, "j2_shoulder": 0.25, "j3_elbow": 0.85, "j4_forearm_roll": 0.0,
             "j5_wrist": 0.70, "gripper": 0.2}
ARM_STOP = {"j1_base": 0.45, "j2_shoulder": 0.55, "j3_elbow": 0.95, "j4_forearm_roll": 0.4,
            "j5_wrist": 0.45, "gripper": 1.1}
ARM_FRAMES = 14
ARM_PERIOD = 6.0
ARM_AT = (16.6, 2.6, 0.0)
ARM_YAW = -math.pi / 4
ARM_UNITS = 13.0
TOOL_LINKS = ("finger_left", "finger_right")


def tool_path(place: Placement, count: int = 40) -> list:
    """Screen points of the fingertip centre along the planned motion (forward kinematics
    of the robot description), the "planned path" drawn over the arm."""
    robot = Robot.load(0.01)
    centres = {link: tris.reshape(-1, 3).mean(axis=0)
               for link, _, tris in robot.meshes if link in TOOL_LINKS}
    pts = []
    for q in smooth_poses(count, ARM_START, ARM_STOP):
        world = robot.transforms(q)
        tip = np.mean([world[l][:3, :3] @ c + world[l][:3, 3] for l, c in centres.items()],
                      axis=0)
        screen, _ = place.project(tip[None, :])
        pts.append((float(screen[0, 0]), float(screen[0, 1])))
    return pts


def moveo_arm(iso: Iso) -> str:
    iso.box(15.0, 18.2, 1.0, 4.2, -0.4, 0.0, BOX_TOP, BOX_LEFT, BOX_RIGHT, EDGE, 1.2)
    iso.led(18.2, 3.8, -0.2, r=2.4)
    place = Placement(*ARM_AT, yaw=ARM_YAW, units=ARM_UNITS, scale=iso.scale)
    groups, css, (x0, y0, x1, y1) = svg_frames(
        place, smooth_poses(ARM_FRAMES, ARM_START, ARM_STOP), ARM_PERIOD)
    iso.points += [(x0, y0), (x1, y1)]
    iso.parts.append(groups)
    path = tool_path(place)
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path)
    iso.parts.append(f'<path d="{d}" fill="none" stroke="#0e2a4f" stroke-width="5" '
                     f'stroke-linecap="round" opacity="0.7"/>')
    iso.parts.append(f'<path d="{d}" fill="none" stroke="{GLOW}" stroke-width="2" '
                     f'stroke-linecap="round" class="flow" filter="url(#glow)"/>')
    for (sx, sy), color in ((path[0], REPLY), (path[-1], "#ffb347")):
        iso.parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4" fill="{color}" '
                         f'filter="url(#glow)"/>')
    return css


def hero() -> None:
    iso = Iso(scale=24.0)
    workstation(iso)
    dds_link(iso)
    robot_pc(iso)
    arm_css = moveo_arm(iso)
    path = os.path.join(OUT, "hero-3d.svg")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(iso.svg(HERO_LABEL, HERO_DEFS, HERO_STYLE + arm_css, glow_at=(9, 2.6)))
    print("wrote", os.path.relpath(path, os.getcwd()))


# ==============================================================================
# 2D DIAGRAMS
# ==============================================================================

def node(s: Svg, x, y, w, h, title, lines=(), fill=WHITE, stroke=BLUE, mono_title=True) -> None:
    s.rect(x, y, w, h, fill=fill, stroke=stroke, rx=8, sw=1.6)
    s.text(x + w / 2, y + 24, title, size=14, weight="bold", fill=NAVY, mono=mono_title)
    for i, value in enumerate(lines):
        s.text(x + w / 2, y + 46 + i * 18, value, size=12, fill=GREY)


def ros_graph() -> None:
    """Nodes, topics and actions between the Operator PC and the Robot PC."""
    s = Svg(1120, 470, "ROS 2 graph of the Operator PC and the Robot PC")
    s.rect(20, 20, 410, 430, fill=LIGHT, stroke=LINE, rx=12)
    s.text(225, 48, "Operator PC · 10.77.0.20", size=15, weight="bold")
    s.rect(690, 20, 410, 430, fill=LIGHT, stroke=LINE, rx=12)
    s.text(895, 48, "Robot PC · 10.77.0.10", size=15, weight="bold")
    s.rect(450, 20, 220, 430, fill="#EAF2FD", stroke=BLUE, rx=12, dash=True)
    s.text(560, 48, "ROS 2 DDS", size=15, weight="bold", fill=BLUE)
    s.text(560, 68, "smx_net · ROS_DOMAIN_ID 42", size=11, fill=GREY)

    node(s, 45, 85, 360, 60, "rviz2", ["MotionPlanning panel · RobotModel · TF"])
    node(s, 45, 200, 360, 120, "move_group",
         ["OMPL planner · pick_ik kinematics", "planning scene monitor",
          "MoveItSimpleControllerManager"])
    node(s, 45, 375, 360, 50, "smartmanipulator_x_moveit_config", [], fill="#FFF7EC",
         stroke=ORANGE)

    node(s, 715, 85, 360, 60, "robot_state_publisher", ["/robot_description · /tf"])
    node(s, 715, 180, 360, 60, "joint_state_broadcaster", ["/joint_states"])
    node(s, 715, 275, 360, 150, "ros2_control_node",
         ["arm_controller: j1_base … j5_wrist", "gripper_controller: gripper",
          "hardware: mock now,", "DYNAMIXEL bus later"])

    s.line(225, 145, 225, 200, TEAL, "teal")
    s.text(235, 177, "goal · Plan & Execute", size=12, fill=TEAL, anchor="start")
    s.line(225, 375, 225, 320, GREY, "end")
    s.text(235, 356, "SRDF · kinematics · limits", size=12, fill=GREY, anchor="start")

    s.line(715, 115, 405, 115, GREEN, "green")
    s.text(560, 108, "/tf", size=12, fill=GREEN, mono=True)
    s.line(715, 210, 405, 230, GREEN, "green")
    s.text(560, 210, "/joint_states", size=12, fill=GREEN, mono=True)
    s.line(405, 280, 715, 310, ORANGE, "orange")
    s.text(560, 284, "arm_controller/", size=11, fill=ORANGE, mono=True)
    s.text(560, 322, "follow_joint_trajectory", size=11, fill=ORANGE, mono=True)
    s.line(405, 305, 715, 385, ORANGE, "orange")
    s.text(560, 368, "gripper_controller/", size=11, fill=ORANGE, mono=True)
    s.text(560, 400, "follow_joint_trajectory", size=11, fill=ORANGE, mono=True)
    s.text(560, 436, "FollowJointTrajectory actions", size=11, fill=GREY)
    s.save(os.path.join(OUT, "ros-graph.svg"))


def image_build() -> None:
    """Where the Operator PC image takes its files from."""
    s = Svg(1000, 330, "Build contexts of the Operator PC image")
    node(s, 20, 30, 330, 120, "Operator PC repository", ["context: ..", "docker/Dockerfile",
                                                          "ros2_ws/src (MoveIt config)",
                                                          "docker/entrypoint.sh"],
         mono_title=False)
    node(s, 20, 180, 330, 120, "Robot PC repository", ["additional context: robot_pc_repo",
                                                        "smartmanipulator_x_description",
                                                        "docker/dds/fastdds_udp.xml"],
         stroke=TEAL, mono_title=False)
    node(s, 420, 30, 220, 270, "ros:jazzy-ros-base",
         ["+ ros-jazzy-moveit", "+ ros-jazzy-pick-ik", "+ ros-jazzy-rviz2", "+ xacro, urdf",
          "+ ros2controlcli", "+ control-msgs", "+ Mesa (llvmpipe)", "colcon build",
          "RelWithDebInfo"], fill=LIGHT, stroke=NAVY)
    node(s, 710, 30, 270, 120, "smartmanipulator-x-operator:jazzy",
         ["/ws/src/operator", "/ws/src/smartmanipulator_x_description", "/ws/install"],
         fill="#EAF2FD", stroke=BLUE)
    node(s, 710, 180, 270, 120, "/etc/smx/fastdds_udp.xml",
         ["FASTDDS_DEFAULT_PROFILES_FILE", "UDPv4 only, no shared memory",
          "same file as the Robot PC"], fill="#EAF2FD", stroke=BLUE)
    s.line(350, 90, 420, 120, GREY, "end")
    s.line(350, 240, 420, 200, TEAL, "teal")
    s.line(640, 110, 710, 90, BLUE, "end")
    s.line(640, 210, 710, 240, BLUE, "end")
    s.save(os.path.join(OUT, "image-build.svg"))


# ------------------------------------------------------------------------------
# System overview, in the style of the system site's overview figure
# (sfs-smartmanipulator-x-robot: docs/images/system-overview.svg), with the
# Operator PC in focus.
# ------------------------------------------------------------------------------

SYS_STYLE = (
    ".pc{fill:#f1f3f4;stroke:#5f6368;stroke-width:1.5}"
    ".op{fill:#e8f0fe;stroke:#1a73e8;stroke-width:2}"
    ".node{fill:#fff;stroke:#1a73e8;stroke-width:1.5}"
    ".rnode{fill:#fff;stroke:#5f6368;stroke-width:1.2}"
    ".kit{fill:#e6f4ea;stroke:#188038;stroke-width:1.5}"
    ".drv{fill:#fef7e0;stroke:#b06000;stroke-width:1.5}"
    ".mech{fill:#fce8e6;stroke:#c5221f;stroke-width:1.5}"
    ".h{font-weight:700;font-size:15px;fill:#202124}"
    ".m{font-family:'JetBrains Mono',Consolas,'DejaVu Sans Mono',monospace;font-weight:700;"
    "font-size:13px;fill:#202124}"
    ".t{fill:#202124}.s{fill:#5f6368;font-size:12px}"
    ".tag{fill:#1a73e8;font-size:11px;font-weight:700;letter-spacing:.06em}"
    ".l{stroke:#3c4043;stroke-width:2;fill:none;marker-end:url(#a)}"
    ".g{stroke:#188038;stroke-width:2;fill:none;marker-end:url(#ag)}"
    ".o{stroke:#b06000;stroke-width:2;fill:none;marker-end:url(#ao)}"
)


class Raw:
    """Plain SVG with a style sheet (the look of the system site's overview figure)."""

    def __init__(self, width: int, height: int, title: str, style: str) -> None:
        markers = "".join(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
            f'fill="{color}"/></marker>'
            for mid, color in (("a", "#3c4043"), ("ag", "#188038"), ("ao", "#b06000")))
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-label="{title}" '
            f'font-family="Inter, Segoe UI, DejaVu Sans, Arial, sans-serif" font-size="13">',
            f"<title>{title}</title><defs>{markers}</defs><style>{style}</style>",
            f'<rect width="{width}" height="{height}" rx="12" fill="#fff"/>']

    def box(self, cls, x, y, w, h) -> None:
        self.parts.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')

    def text(self, cls, x, y, value, anchor="start") -> None:
        value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{value}</text>')

    def path(self, cls, d) -> None:
        self.parts.append(f'<path class="{cls}" d="{d}"/>')

    def save(self, name: str) -> None:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(self.parts + ["</svg>"]) + "\n")
        print("wrote", os.path.relpath(path, os.getcwd()))


def system_overview() -> None:
    s = Raw(1000, 610, "SmartManipulator-X with the Operator PC: MoveIt 2 and RViz2 send "
            "trajectories over ROS 2 DDS to the Robot PC, which drives the SmartFusion2 "
            "controller, the stepper drivers, the gripper servo and the Moveo arm", SYS_STYLE)
    # Operator PC (this repository)
    s.box("op", 20, 20, 400, 300)
    s.text("tag", 36, 42, "THIS REPOSITORY")
    s.text("h", 36, 64, "Operator PC")
    s.text("s", 36, 84, "ROS 2 Jazzy in Docker · 10.77.0.20 · display via WSLg / X11")
    s.box("node", 36, 100, 368, 56)
    s.text("m", 50, 123, "rviz2")
    s.text("s", 50, 143, "MotionPlanning panel · interactive marker · Plan & Execute")
    s.box("node", 36, 176, 368, 72)
    s.text("m", 50, 199, "move_group")
    s.text("s", 50, 219, "OMPL planner · pick_ik (position only)")
    s.text("s", 50, 237, "planning scene · MoveItSimpleControllerManager")
    s.box("node", 36, 266, 368, 40)
    s.text("m", 50, 291, "smartmanipulator_x_moveit_config")
    s.path("l", "M220 156 L220 176")
    s.path("l", "M220 266 L220 248")
    # Robot PC
    s.box("pc", 580, 20, 400, 300)
    s.text("tag", 596, 42, "SFS-SMARTMANIPULATOR-X-ROBOT")
    s.text("h", 596, 64, "Robot PC")
    s.text("s", 596, 84, "ROS 2 Jazzy in Docker · 10.77.0.10 · owns the USB link")
    for i, (name, sub) in enumerate((("robot_state_publisher", "/robot_description · /tf"),
                                      ("joint_state_broadcaster", "/joint_states"),
                                      ("ros2_control_node", "arm_controller · gripper_controller"))):
        y = 100 + i * 68
        s.box("rnode", 596, y, 368, 56)
        s.text("m", 610, y + 23, name)
        s.text("s", 610, y + 43, sub)
    s.text("s", 596, 306, "hardware: mock now, DYNAMIXEL bus later")
    # DDS between the PCs
    s.text("h", 500, 112, "ROS 2 DDS", "middle")
    s.text("s", 500, 130, "smx_net · domain 42", "middle")
    s.text("s", 500, 146, "UDPv4 only", "middle")
    s.path("g", "M596 196 L404 196")
    s.text("s", 500, 188, "/joint_states · /tf", "middle")
    s.path("o", "M404 230 L596 264")
    s.text("s", 500, 274, "FollowJointTrajectory", "middle")
    s.text("s", 500, 290, "arm + gripper", "middle")
    # hardware chain below the Robot PC
    s.path("l", "M780 320 L780 370")
    s.text("s", 792, 342, "USB · DYNAMIXEL Protocol 2.0")
    s.box("kit", 300, 370, 680, 70)
    s.text("h", 316, 396, "SmartFusion2 controller · M2S Hello FPGA Kit")
    s.text("t", 316, 420, "Zephyr firmware: virtual DYNAMIXEL devices · IDs 1–6 stepper axes · ID 7 gripper")
    s.path("l", "M460 440 L460 480")
    s.text("s", 472, 464, "SPI")
    s.path("l", "M820 440 L820 480")
    s.text("s", 832, 464, "CorePWM")
    s.box("drv", 300, 480, 320, 50)
    s.text("h", 316, 510, "6× TMC5160T Pro stepper drivers")
    s.box("drv", 660, 480, 320, 50)
    s.text("h", 676, 510, "MG996R gripper servo")
    s.path("l", "M460 530 L460 550")
    s.path("l", "M820 530 L820 550")
    s.box("mech", 300, 550, 680, 44)
    s.text("h", 316, 577, "BCN3D Moveo mechanics")
    s.text("s", 502, 577, "J1 base · J2 shoulder · J3 elbow · J4 forearm roll · J5 wrist · gripper")
    # note left of the hardware chain
    s.text("s", 30, 400, "The Operator PC has no hardware")
    s.text("s", 30, 418, "connection: no USB device, no")
    s.text("s", 30, 436, "ros2_control, no motor access.")
    s.save("system-overview.svg")


def network() -> None:
    """smx_net: the containers on one computer."""
    s = Svg(1000, 330, "The Docker network smx_net on one computer: robot_pc, operator_pc and "
            "shell containers connected over ROS 2 DDS")
    s.rect(20, 20, 960, 290, fill=LIGHT, stroke=LINE, rx=12)
    s.text(500, 48, "one computer (Docker) · network smx_net 10.77.0.0/24", size=15, weight="bold")
    node(s, 50, 75, 290, 150, "robot_pc · 10.77.0.10",
         ["robot_state_publisher", "ros2_control_node (mock)", "joint_state_broadcaster",
          "arm_ / gripper_controller"], stroke=GREY)
    node(s, 370, 75, 290, 150, "operator_pc · 10.77.0.20",
         ["move_group", "rviz2 → WSLg / X11", "(this repository)"], fill="#EAF2FD")
    node(s, 690, 75, 260, 150, "shell · dynamic address",
         ["profile tools", "ros2 CLI", "rviz2, glxgears"])
    s.rect(50, 245, 900, 40, fill="#EAF2FD", stroke=BLUE, rx=8, dash=True)
    s.text(500, 270, "ROS 2 DDS · Fast DDS UDPv4 only · ROS_DOMAIN_ID 42", size=13,
           weight="bold", fill=BLUE)
    for x in (195, 515, 820):
        s.line(x, 225, x, 245, BLUE, "end")
    s.save(os.path.join(OUT, "smx-net.svg"))


def control_paths() -> None:
    """The three paths one MoveIt configuration drives."""
    s = Svg(1000, 275, "Control paths: real robot, mock hardware and simulation behind the "
            "same MoveIt configuration")
    arrow = {GREY: "end", GREEN: "green", ORANGE: "orange"}
    rows = (("Real robot", ["ROS 2 DDS", "Robot PC: ros2_control", "USB · DYNAMIXEL", "SmartFusion2"],
             GREY, "after hardware verification"),
            ("Mock", ["ROS 2 DDS", "Robot PC: ros2_control", "mock hardware"],
             GREEN, "in use today"),
            ("Simulation", ["Gazebo ros2_control", "simulated Moveo joints"], ORANGE, "planned"))
    for r, (name, steps, color, state) in enumerate(rows):
        y = 30 + r * 85
        s.text(30, y + 26, name, size=14, weight="bold", anchor="start")
        s.text(30, y + 46, state, size=11, fill=color, anchor="start")
        s.rect(190, y, 120, 55, fill="#EAF2FD", stroke=BLUE, sw=1.6)
        s.text(250, y + 33, "MoveIt 2", size=14, weight="bold")
        x, w = 340, (970 - 340 - 30 * (len(steps) - 1)) / len(steps)
        s.line(310, y + 27, x, y + 27, color, arrow[color])
        for i, step in enumerate(steps):
            s.rect(x, y, w, 55, fill=WHITE, stroke=color, sw=1.6)
            s.text(x + w / 2, y + 32, step, size=12)
            if i < len(steps) - 1:
                s.line(x + w, y + 27, x + w + 30, y + 27, color, arrow[color])
            x += w + 30
    s.save(os.path.join(OUT, "control-paths.svg"))


if __name__ == "__main__":
    if "--no-hero" not in sys.argv:
        hero()
    ros_graph()
    image_build()
    system_overview()
    network()
    control_paths()
