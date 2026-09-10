import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
    package_path = get_package_share_directory('fast_lio')
    default_config_path = os.path.join(package_path, 'config')
    default_rviz_config_path = os.path.join(
        package_path, 'rviz', 'fastlio.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_livox_driver = LaunchConfiguration('use_livox_driver')
    robot_ns = LaunchConfiguration('robot_ns')
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')
    livox_launch_path = os.path.join(
        get_package_share_directory('livox_ros_driver2'),
        'launch_ROS2', 'msg_MID360s_launch.py')
    map_frame = PythonExpression(
        ["(('", robot_ns, "'.strip('/') + '/') if '", robot_ns,
         "'.strip('/') else '') + 'camera_init'"])
    lidar_imu_frame = PythonExpression(
        ["(('", robot_ns, "'.strip('/') + '/') if '", robot_ns,
         "'.strip('/') else '') + 'lidar_imu'"])

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    declare_use_livox_driver_cmd = DeclareLaunchArgument(
        'use_livox_driver', default_value='true',
        description='Start the Livox MID360s driver when true'
    )
    declare_robot_ns_cmd = DeclareLaunchArgument(
        'robot_ns', default_value='',
        description='Namespace and TF prefix for this robot'
    )
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )
    decalre_config_file_cmd = DeclareLaunchArgument(
        'config_file', default_value='mid360s.yaml',
        description='Config file'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz to monitor results'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config file path'
    )

    livox_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(livox_launch_path),
        launch_arguments={
            'robot_ns': robot_ns,
            'frame_id': lidar_imu_frame,
        }.items(),
        condition=IfCondition(use_livox_driver)
    )

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        namespace=robot_ns,
        parameters=[PathJoinSubstitution([config_path, config_file]),
                    {
                        'common.frame_prefix': robot_ns,
                        'use_sim_time': use_sim_time,
                    }],
        output='screen'
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        namespace=robot_ns,
        arguments=['-d', rviz_cfg, '-f', map_frame],
        condition=IfCondition(rviz_use)
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_use_livox_driver_cmd)
    ld.add_action(declare_robot_ns_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(decalre_config_file_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)

    ld.add_action(livox_driver_launch)
    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)

    return ld
