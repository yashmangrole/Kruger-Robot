#!/usr/bin/env python3
import time
import math
from pylx16a.lx16a import *

# === CONFIGURATION ===
SERVO_PORT = "COM4"
AMPLITUDE  = 35    # ±25° swing
FREQUENCY  = 0.4      # Hz
SLEEP_TIME = 0.02     # sec
HOME_TIME  = 1.0      # seconds to hold home pose

# === Servo Mapping ===
LEGS = {
    "FL": (1, 2),
    "FR": (3, 4),
    "BL": (5, 6),
    "BR": (7, 8)
}

# === Center Angles ===
CENTER_ANGLES = {
    1: 153.16,  2: 106.04,
    3: 147.36,  4: 123.12,
    5: 115.44,  6: 104.16,
    7:  99.12,  8: 122.64
}

# CENTER_ANGLES = {
#     1: 90.16,  2: 115.04,
#     3: 133.36,  4: 131.12,
#     5: 101.44,  6: 112.16,
#     7:  95.12,  8: 130.64 }


def home_position(servos):
    """Move all servos to their center (home) angles."""
    print("[INFO] Moving to home position...")
    move_time_ms = int(HOME_TIME * 1000)
    for sid, servo in servos.items():
        center = CENTER_ANGLES[sid]
        servo.move(center, time=move_time_ms)
    time.sleep(HOME_TIME + 0.1)
    print("[INFO] Home position reached.")

def main():
    LX16A.initialize(SERVO_PORT)
    servos = {i: LX16A(i) for i in CENTER_ANGLES}
    for s in servos.values():
        s.set_angle_limits(0, 240)
    print("[INFO] Initialized servos.")

    # 1) Go to home pose
    home_position(servos)

    # 2) Start diagonal walk
    t = 0.0
    print("[INFO] Starting diagonal walk (FL+BR vs FR+BL brute-force)…")
    try:
        while True:
            cycle = 2 * math.pi * FREQUENCY * t

            for leg, (hip_id, knee_id) in LEGS.items():
                # compute raw offsets
                raw_hip  = math.sin(cycle) * AMPLITUDE
                raw_knee = math.cos(cycle) * AMPLITUDE

                # brute-force flip for diagonal legs
                if leg in ("FR", "FL"):
                    hip_offset  = -raw_hip
                    knee_offset = -raw_knee
                else:  # ("FL", "BR")
                    hip_offset  =  raw_hip
                    knee_offset =  raw_knee

                # apply and clamp
                hip_angle  = max(0, min(240, CENTER_ANGLES[hip_id]  + hip_offset))
                knee_angle = max(0, min(240, CENTER_ANGLES[knee_id] + knee_offset))

                servos[hip_id].move(hip_angle)
                servos[knee_id].move(knee_angle)

            t += SLEEP_TIME
            time.sleep(max(0, SLEEP_TIME - (time.monotonic() - (time.monotonic() - SLEEP_TIME))))
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    finally:
        print("[INFO] Exiting diagonal walk.")

if __name__ == "__main__":
    main()
