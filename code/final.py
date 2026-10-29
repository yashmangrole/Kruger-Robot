#!/usr/bin/env python3
import time
import math
from pylx16a.lx16a import *

# === ROBOT CONFIGURATION ===
SERVO_PORT = "COM4"  # UPDATE THIS

# Servo ID Mapping: {LegName: (HipID, KneeID)}
LEGS = {
    "FL": (2, 1),  # Front Left
    "FR": (3,4),  # Front Right
    "BL": (5, 6),  # Back Left
    "BR": (7,8)   # Back Right
}

# === DEFAULT STANDING POSTURE ===
# Define the SPECIFIC angle for EACH servo when standing still.
# Adjust these values based on your robot's calibration and desired stance.
DEFAULT_STAND_ANGLES = {
    "FL": {"hip": 120, "knee": 120},
    "FR": {"hip":104,"knee":145},
    "BL": {"hip": 120, "knee": 120},
    "BR": {"hip": 104, "knee": 145},
}

# === GAIT & OTHER POSTURE PARAMETERS ===

# --- Sitting ---
# Define sitting angles (can be uniform or specific like standing)
# Using uniform angles here for simplicity, but could be a specific dictionary too.
SIT_HIP_ANGLE = 120
SIT_KNEE_ANGLE = 50

# --- Trotting Gait ---
# Centers here define the average position DURING the trot gait
TROT_PARAMS = {
    "hip_amplitude": 15,
    "knee_amplitude": 15,
    "lift_amplitude": 20,
    "frequency": 0.7,
    # Adjust trot centers if needed (e.g., slightly lower stance than static stand)
    "center_hip": 120,  # Example: Same as default stand hip
    "center_knee": 105, # Example: Knees slightly more bent than default stand knee
    "phase_stagger": math.pi,
    "knee_phase_offset": math.pi / 2
}

# --- Walking Gait ---
# Centers here define the average position DURING the walk gait
WALK_PARAMS = {
    "hip_amplitude": 15,
    "knee_amplitude": 15,
    "lift_amplitude": 20,
    "frequency": 0.4,
    # Adjust walk centers if needed
    "center_hip": 120,  # Example: Same as default stand hip
    "center_knee": 110, # Example: Knees slightly more bent than default stand knee
    "phase_stagger": math.pi / 2,
    "knee_phase_offset": math.pi / 2
}

# --- General ---
SLEEP_TIME = 0.02

# === MAIN CONTROL CLASS ===
class QuadrupedRobot:
    # Accept custom stand angles during initialization
    def __init__(self, port=SERVO_PORT, stand_angles=None):
        self.stand_angles = stand_angles if stand_angles is not None else DEFAULT_STAND_ANGLES
        # Validate stand_angles structure (basic check)
        if not self._validate_stand_angles(self.stand_angles):
             raise ValueError("Invalid stand_angles dictionary structure.")

        try:
            LX16A.initialize(port)
            self.servos = {}
            for leg, (hip_id, knee_id) in LEGS.items():
                # Check if leg exists in stand_angles (should always if validated)
                if leg not in self.stand_angles:
                     raise KeyError(f"Leg '{leg}' not found in provided stand_angles.")

                hip = LX16A(hip_id)
                knee = LX16A(knee_id)
                hip.set_angle_limits(0, 240)
                knee.set_angle_limits(0, 240)
                self.servos[leg] = {"hip": hip, "knee": knee}
            print(f"[INFO] Initialized servos on port {port}")
            self.is_moving = False
            self.time = 0.0
            # Go to defined standing pose on init
            print("[INFO] Moving to initial standing pose...")
            self.stand(move_time=1000) # Use stand() method to apply individual angles
            print("[INFO] Robot standing.")

        except ServoTimeoutError as e:
            print(f"[ERROR] Servo {e.id_} not responding during initialization on port {port}. Check connections and IDs.")
            raise
        except Exception as e:
            print(f"[ERROR] Failed to initialize servos: {e}")
            raise

    def _validate_stand_angles(self, angles_dict):
        """Basic check if the stand angles dictionary has the required structure."""
        if not isinstance(angles_dict, dict): return False
        for leg_name in LEGS.keys():
            if leg_name not in angles_dict: return False
            if not isinstance(angles_dict[leg_name], dict): return False
            if "hip" not in angles_dict[leg_name]: return False
            if "knee" not in angles_dict[leg_name]: return False
        return True

    def _move_leg(self, leg_name, hip_angle, knee_angle, move_time=0):
        """Moves a single leg to target angles."""
        try:
            hip_servo = self.servos[leg_name]["hip"]
            knee_servo = self.servos[leg_name]["knee"]
            hip_angle = max(0, min(240, hip_angle))
            knee_angle = max(0, min(240, knee_angle))
            hip_servo.move(hip_angle, time=move_time)
            knee_servo.move(knee_angle, time=move_time)
        except ServoTimeoutError as e:
            print(f"[WARN] Timeout moving servo {e.id_} ({leg_name}).")
        except Exception as e:
            print(f"[ERROR] Error moving {leg_name}: {e}")

    def set_pose(self, hip_angle, knee_angle, move_time=500):
        """Moves ALL legs to the SAME specified hip/knee angle."""
        print(f"[INFO] Setting UNIFORM pose: Hip={hip_angle}, Knee={knee_angle}")
        if self.is_moving:
            print("[INFO] Stopping existing movement before setting pose.")
            self.stop()
            time.sleep(SLEEP_TIME * 2)

        # Apply the same angle to all legs
        for leg_name in self.servos.keys():
            self._move_leg(leg_name, hip_angle, knee_angle, move_time=move_time)

        if move_time > 0:
             time.sleep(move_time / 1000.0 + 0.1)
        print("[INFO] Uniform pose set.")

    # Modified stand() method
    def stand(self, move_time=500):
        """Move robot to its defined standing position using individual servo angles."""
        print("[INFO] Moving to defined standing pose...")
        if self.is_moving:
            print("[INFO] Stopping existing movement before standing.")
            # Setting is_moving false should be enough, the stop() method
            # already calls stand() itself, avoid recursion.
            self.is_moving = False
            time.sleep(SLEEP_TIME * 3) # Allow loop to exit if it was running

        # Iterate through the specific stand angles and move each servo
        for leg_name, angles in self.stand_angles.items():
            hip_angle = angles["hip"]
            knee_angle = angles["knee"]
            print(f"[DEBUG] Standing {leg_name}: Hip={hip_angle}, Knee={knee_angle}") # Debug print
            self._move_leg(leg_name, hip_angle, knee_angle, move_time=move_time)

        # Wait for movement
        if move_time > 0:
            time.sleep(move_time / 1000.0 + 0.1)
        print("[INFO] Robot is standing.")

    def sit(self, move_time=800):
        """Move robot to a sitting position (using uniform angles here)."""
        # This uses set_pose for a uniform sit. You could adapt it to use
        # a specific SIT_ANGLES dictionary similar to stand_angles if needed.
        print("[INFO] Moving to sitting pose...")
        self.set_pose(SIT_HIP_ANGLE, SIT_KNEE_ANGLE, move_time)
        print("[INFO] Robot is sitting.")


    def _gait_loop(self, params):
        """Internal loop for executing gaits based on parameters."""
        self.is_moving = True
        self.time = 0.0
        print(f"[INFO] Starting gait with Frequency: {params['frequency']:.2f} Hz")

        # Define leg phase offsets (same as before)
        if params["phase_stagger"] == math.pi: # Trot
            leg_phases = {"FL": 0, "FR": math.pi, "BL": math.pi, "BR": 0}
        elif params["phase_stagger"] == math.pi / 2: # Walk (Crawl)
            leg_phases = {"FL": 0, "FR": math.pi, "BL": 3*math.pi/2, "BR": math.pi/2}
        else:
            print("[WARN] Unknown phase stagger, defaulting to trot phases.")
            leg_phases = {"FL": 0, "FR": math.pi, "BL": math.pi, "BR": 0}

        while self.is_moving:
            loop_start_time = time.monotonic()
            t = 2 * math.pi * self.time * params["frequency"]

            for leg, servos in self.servos.items():
                leg_phase = leg_phases[leg]
                cycle_time = t + leg_phase

                hip_sign = -1 if leg in ["FL", "BL"] else 1

                # Calculate angles relative to the GAIT'S center points
                hip_angle = (hip_sign * math.sin(cycle_time) * params["hip_amplitude"]
                             + params["center_hip"]) # Use gait center_hip

                knee_base = (math.sin(cycle_time + params["knee_phase_offset"])
                             * params["knee_amplitude"])
                lift_factor = (1 - math.cos(cycle_time)) / 2
                knee_lift = lift_factor * params["lift_amplitude"]
                knee_angle = params["center_knee"] + knee_base - knee_lift # Use gait center_knee

                self._move_leg(leg, hip_angle, knee_angle) # move_time=0 default

            self.time += SLEEP_TIME
            elapsed = time.monotonic() - loop_start_time
            sleep_duration = max(0, SLEEP_TIME - elapsed)
            time.sleep(sleep_duration)

        print("[INFO] Gait loop finished.")

    # walk(), trot(), run() methods remain the same - they initiate _gait_loop
    # with their respective PARAMS dictionaries (which define gait centers)

    def walk(self):
        """Start the walking gait."""
        if self.is_moving:
            print("[WARN] Already moving. Stop first to start walk.")
            return
        print("[INFO] Preparing to walk...")
        # Ensure starting from the defined standing pose before gait
        self.stand(move_time=300)
        time.sleep(0.2)
        try:
            self._gait_loop(WALK_PARAMS)
        except Exception as e:
             print(f"[ERROR] Exception during walk loop: {e}")
             self.stop()

    def trot(self):
        """Start the trotting gait."""
        if self.is_moving:
            print("[WARN] Already moving. Stop first to start trot.")
            return
        print("[INFO] Preparing to trot...")
        self.stand(move_time=300)
        time.sleep(0.2)
        try:
            self._gait_loop(TROT_PARAMS)
        except Exception as e:
             print(f"[ERROR] Exception during trot loop: {e}")
             self.stop()

    def run(self):
        """Start a faster 'run' (currently faster trot)."""
        if self.is_moving:
            print("[WARN] Already moving. Stop first to start run.")
            return
        print("[INFO] Preparing to run (faster trot)...")
        run_params = TROT_PARAMS.copy()
        run_params["frequency"] = 1.5 # Faster
        # Adjust run centers if needed, maybe lower?
        # run_params["center_knee"] = 100

        self.stand(move_time=300)
        time.sleep(0.2)
        try:
            self._gait_loop(run_params)
        except Exception as e:
             print(f"[ERROR] Exception during run loop: {e}")
             self.stop()

    # Modified stop() method
    def stop(self):
        """Stops any active gait and returns to the defined standing pose."""
        if self.is_moving:
            print("[INFO] Stopping movement...")
            self.is_moving = False
            # Give the loop a moment to check the flag and exit
            time.sleep(SLEEP_TIME * 3)
            print("[INFO] Movement stop requested. Returning to stand...")
            # Go to defined stand pose after stopping
            self.stand(move_time=300) # stand() now uses individual angles
        else:
            print("[INFO] Robot is not currently moving.")


    # Modified shutdown()
    def shutdown(self, return_to_stand=True):
        """Stops movement and optionally returns to defined stand pose."""
        print("[INFO] Shutting down robot control...")
        if self.is_moving:
             self.is_moving = False
             time.sleep(SLEEP_TIME * 3)

        if return_to_stand:
            print("[INFO] Returning to defined stand pose before shutdown.")
            self.stand(move_time=500) # Uses individual stand angles
        else:
             print("[INFO] Leaving servos in last position.")

        # Optional relaxation omitted for brevity
        print("[INFO] Robot shutdown complete.")


# === ENTRY POINT & DEMO ===
if __name__ == "__main__":
    robot = None
    active_gait = None

    # --- Define YOUR specific standing angles here ---
    # Example: Slightly different angles for calibration or stability
    CUSTOM_STAND_ANGLES = { "FL": {"hip": 120, "knee": 120},
        "FR": {"hip":104,"knee": 145},
        "BL": {"hip": 120, "knee": 120},
        "BR": {"hip": 105, "knee": 145},
    }
       
    # --- --- --- --- --- --- --- --- --- --- --- ---

    def run_gait(gait_function):
        # ... (run_gait function remains the same) ...
        global active_gait
        if active_gait:
            print("[WARN] A gait is already active. Use 'stop' first.")
            return
        active_gait = gait_function
        try:
            gait_function()
        finally:
            active_gait = None


    try:
        # Pass the custom angles to the constructor
        print("[INFO] Initializing robot with CUSTOM standing angles.")
        robot = QuadrupedRobot(port=SERVO_PORT, stand_angles=CUSTOM_STAND_ANGLES)
        # If you want to use the defaults, just do:
        # robot = QuadrupedRobot(port=SERVO_PORT)

        print("\n" + "="*30)
        print(" QUADRUPED ROBOT DEMO")
        print("="*30)
        print("Commands: stand, sit, walk, trot, run, stop, quit")
        print("Robot initialized with specific standing angles.")

        while True:
            command = input("Enter command: ").strip().lower()

            if command == "stand":
                if active_gait: robot.stop() # stop() implicitly calls stand()
                else: robot.stand() # Call stand directly if not moving
            elif command == "sit":
                 if active_gait: robot.stop() # Stop first, then sit
                 robot.sit()
            elif command == "walk":
                run_gait(robot.walk)
            elif command == "trot":
                run_gait(robot.trot)
            elif command == "run":
                 run_gait(robot.run)
            elif command == "stop":
                robot.stop() # Stops gait and returns to defined stand pose
            elif command == "quit":
                break
            else:
                print("Unknown command.")

    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C detected. Stopping robot...")
    except ServoTimeoutError as e:
        print(f"[FATAL ERROR] Servo {e.id_} timed out. Check connection/ID. Cannot continue.")
    except Exception as e:
        print(f"[FATAL ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if robot:
            print("[INFO] Initiating shutdown sequence...")
            # Shutdown will also use the defined stand angles if return_to_stand=True
            robot.shutdown(return_to_stand=True)
        print("[INFO] Program terminated.")