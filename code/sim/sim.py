import pybullet as p
import pybullet_data
import time
import math
from robot_descriptions.loaders.pybullet import load_robot_description

# --- 1. Connect to PyBullet Physics Server ---
# Use p.GUI for visualization, p.DIRECT for non-graphical
physicsClient = p.connect(p.GUI) 
print("Connected to PyBullet GUI.")

# --- 2. Set up the Simulation Environment ---
# Add the PyBullet data path for default objects like the plane
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Set gravity
p.setGravity(0, 0, -9.81)

# Load a ground plane
planeId = p.loadURDF("plane.urdf")

# Set simulation time step (optional, default is 1/240)
p.setTimeStep(1. / 240.)

# Configure the visualizer camera (optional)
p.resetDebugVisualizerCamera(
    cameraDistance=1.5,
    cameraYaw=30,
    cameraPitch=-30,
    cameraTargetPosition=[0, 0, 0.3] 
)

# --- 3. Load the A1 Robot ---
# Define the initial position and orientation for the robot's base
startPos = [0, 0, 0.4]  # Slightly above the ground
startOrientation = p.getQuaternionFromEuler([0, 0, 0])

print("Loading A1 robot description...")
# Use the robot_descriptions loader
# Make sure 'a1_description' is installed (pip install a1_description)
robotId = load_robot_description(
    "a1_description", 
    basePosition=startPos, 
    baseOrientation=startOrientation
)
print(f"A1 Robot loaded with ID: {robotId}")

# --- 4. Prepare for Control ---
# Get information about the robot's joints
num_joints = p.getNumJoints(robotId)
joint_name_to_index = {}
print(f"\nFound {num_joints} joints:")
for i in range(num_joints):
    info = p.getJointInfo(robotId, i)
    joint_index = info[0]
    joint_name = info[1].decode("utf-8")
    joint_type = info[2]
    # We are interested in controlling 'revolute' joints (motors)
    if joint_type == p.JOINT_REVOLUTE:
        joint_name_to_index[joint_name] = joint_index
        print(f"  Index: {joint_index}, Name: {joint_name}, Type: {p.JOINT_TYPES[joint_type]}")

# Define a target "standing" pose (adjust angles as needed)
# These are approximate angles for a basic standing pose
# FR = Front Right, FL = Front Left, RR = Rear Right, RL = Rear Left
# Hip, Thigh, Calf
initial_joint_angles = {
    'FR_hip_joint': 0.0, 'FR_thigh_joint': 0.8, 'FR_calf_joint': -1.5,
    'FL_hip_joint': 0.0, 'FL_thigh_joint': 0.8, 'FL_calf_joint': -1.5,
    'RR_hip_joint': 0.0, 'RR_thigh_joint': 0.8, 'RR_calf_joint': -1.5,
    'RL_hip_joint': 0.0, 'RL_thigh_joint': 0.8, 'RL_calf_joint': -1.5,
}

# --- 5. Set Initial Pose ---
# It's often better to reset the state *before* the simulation loop starts
print("\nSetting initial joint pose...")
for joint_name, target_angle in initial_joint_angles.items():
    if joint_name in joint_name_to_index:
        joint_index = joint_name_to_index[joint_name]
        p.resetJointState(robotId, joint_index, targetValue=target_angle)
        # Also set the control mode to position control with some force
        p.setJointMotorControl2(
            bodyIndex=robotId,
            jointIndex=joint_index,
            controlMode=p.POSITION_CONTROL,
            targetPosition=target_angle,
            force=100 # Adjust force as needed
        )
    else:
        print(f"Warning: Joint '{joint_name}' not found in the loaded model.")

print("Initial pose set.")

# --- 6. Simulation Loop ---
print("\nStarting simulation loop...")
simulation_steps = 10000  # Run for approximately 40 seconds (10000 / 240)

for i in range(simulation_steps):
    # --- Simple Motion Example: Oscillate Hip Joints ---
    # Calculate a target angle based on a sine wave
    amplitude = 0.2  # Radians
    frequency = 1.0  # Hertz
    time_elapsed = i * (1. / 240.)
    angle_offset = amplitude * math.sin(2 * math.pi * frequency * time_elapsed)

    # Apply oscillation to front-left and rear-right hips
    fl_hip_index = joint_name_to_index.get('FL_hip_joint')
    rr_hip_index = joint_name_to_index.get('RR_hip_joint')
    if fl_hip_index is not None:
        target_pos_fl = initial_joint_angles['FL_hip_joint'] + angle_offset
        p.setJointMotorControl2(robotId, fl_hip_index, p.POSITION_CONTROL, targetPosition=target_pos_fl, force=100)
    if rr_hip_index is not None:
        target_pos_rr = initial_joint_angles['RR_hip_joint'] + angle_offset
        p.setJointMotorControl2(robotId, rr_hip_index, p.POSITION_CONTROL, targetPosition=target_pos_rr, force=100)

    # Apply inverse oscillation to front-right and rear-left hips
    fr_hip_index = joint_name_to_index.get('FR_hip_joint')
    rl_hip_index = joint_name_to_index.get('RL_hip_joint')
    if fr_hip_index is not None:
        target_pos_fr = initial_joint_angles['FR_hip_joint'] - angle_offset
        p.setJointMotorControl2(robotId, fr_hip_index, p.POSITION_CONTROL, targetPosition=target_pos_fr, force=100)
    if rl_hip_index is not None:
        target_pos_rl = initial_joint_angles['RL_hip_joint'] - angle_offset
        p.setJointMotorControl2(robotId, rl_hip_index, p.POSITION_CONTROL, targetPosition=target_pos_rl, force=100)

    # --- Keep other joints at their initial standing pose ---
    # (This is implicitly handled because we set them once initially, 
    # but explicitly setting them every step ensures they stay there if perturbed)
    # You could uncomment this block if you need stricter pose holding
    # for joint_name, target_angle in initial_joint_angles.items():
    #     if joint_name not in ['FL_hip_joint', 'RR_hip_joint', 'FR_hip_joint', 'RL_hip_joint']: # Don't override the moving joints
    #         if joint_name in joint_name_to_index:
    #             joint_index = joint_name_to_index[joint_name]
    #             p.setJointMotorControl2(
    #                 bodyIndex=robotId,
    #                 jointIndex=joint_index,
    #                 controlMode=p.POSITION_CONTROL,
    #                 targetPosition=target_angle,
    #                 force=100 
    #             )

    # Step the simulation
    p.stepSimulation()

    # Slow down simulation for visualization (match real-time)
    time.sleep(1. / 240.)

# --- 7. Disconnect from PyBullet ---
p.disconnect()
print("\nSimulation finished. Disconnected from PyBullet.")