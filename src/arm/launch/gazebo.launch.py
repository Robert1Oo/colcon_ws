# import the packages
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
import xacro

def generate_launch_description():
    #include gazebo package to get the launch file of gazebo
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource([os.path.join(
    get_package_share_directory('gazebo_ros'),'launch'),'/gazebo.launch.py']))
    #get the robotic arm package
    package_path = get_package_share_directory('arm')
    #read the urdf file
    urdf_file= os.path.join(package_path, 'urdf', 'arm.urdf')
    doc = xacro.parse(open(urdf_file))
    #get the meshes path
    meshes_path = os.path.join(package_path, 'meshes')
    #get the package file in the install directory
    install_dir = get_package_prefix("arm")
    #include the paths of the meshes and the plugin in gazebo environment path to be read
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] = os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir+ "/share"+ meshes_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = install_dir + "/share" + ':'+ meshes_path
    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir+ "/lib"
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + "/lib"
        
    #create a robot state publisher
    robot_state_publisher_node = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    parameters=[{'use_sim_time': True, 'robot_description': doc.toxml()}],
    output="screen"
    )
    
    #create joint state publisher
    joint_state_publisher_node = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    name='joint_state_publisher'
    )
    
    #create spawn entity node for robotic arm in gazebo
    spawn_entity = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=['-entity', 'arm', '-topic', '/robot_description'],
    output='screen'
    )      
    
    #load the controller manager with the controllers created
    controller_manager_node = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['joint_state_broadcaster',
    'arm_group_controller','hand_group_controller'],
    output='screen'
    )

    #return all the nodes that will be launched
    return LaunchDescription([
    gazebo,
    joint_state_publisher_node,
    robot_state_publisher_node,
    spawn_entity,
    controller_manager_node
    ])
        
    
        
