# SmartManipulator-X Operator PC: MoveIt 2 and RViz2 on ROS 2 Jazzy.
#
# Build context: this repository. Additional build context `robot_pc_repo`:
# the SmartManipulator-X Robot PC repository, which owns the canonical robot
# description and the Fast DDS profile (see docker/docker-compose.yml).

FROM ros:jazzy-ros-base

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Warsaw
ENV ROS_DISTRO=jazzy
ENV ROS_WS=/ws
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ENV ROS_DOMAIN_ID=42
ENV FASTDDS_DEFAULT_PROFILES_FILE=/etc/smx/fastdds_udp.xml
ENV FASTRTPS_DEFAULT_PROFILES_FILE=/etc/smx/fastdds_udp.xml

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    ros-jazzy-moveit \
    ros-jazzy-pick-ik \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro \
    ros-jazzy-urdf \
    ros-jazzy-ros2controlcli \
    ros-jazzy-control-msgs \
    libgl1-mesa-dri \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${ROS_WS}

# Canonical robot description and DDS profile from the Robot PC repository,
# so both computers always use the same joint contract.
COPY --from=robot_pc_repo ros2_ws/src/smartmanipulator_x/smartmanipulator_x_description \
     ${ROS_WS}/src/smartmanipulator_x_description
COPY --from=robot_pc_repo docker/dds/fastdds_udp.xml /etc/smx/fastdds_udp.xml

# Project-owned Operator PC packages.
COPY ros2_ws/src ${ROS_WS}/src/operator

RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo

COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh && \
    echo 'source /opt/ros/${ROS_DISTRO}/setup.bash' >> /root/.bashrc && \
    echo 'source ${ROS_WS}/install/setup.bash' >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
