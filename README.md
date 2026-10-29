# Kruger: Quadrupedal Walking Robot

**Kruger** is a 4-legged walking robot developed as part of the Robotics Studio course (MECE 4611, Spring 2025) at Columbia University. It features a parallel leg linkage and a sinusoidal gait controller written in Python that drives eight LX-16A serial bus servos in real time.

---

## 🦿 Key Features

- Parallel leg linkage for synchronized, efficient walking
- 8 servos: one hip + one knee per leg
- Three gaits: **walk** (crawl), **trot**, and **run**, plus **stand** and **sit** poses
- Per-servo calibrated standing angles to correct for assembly offsets
- Interactive command-line control with servo-disconnect handling and safe shutdown
- Max walking speed: **25.7 cm/sec**

---

## 🛠️ System Architecture

- **Controller**: Raspberry Pi 4 (Raspbian OS); also runs from a PC over USB serial
- **Actuators**: 8 × LX-16A Serial Bus Servo Motors (angle range 0–240°)
- **Control Interface**: Python + [PyLX-16A](https://github.com/ethanlipson/PyLX-16A) over UART
- **Mechanical Design**: Fusion 360 CAD + 3D Printed PLA Components

### Servo Mapping

| Leg | Hip ID | Knee ID |
|-----|--------|---------|
| Front Left (FL)  | 2 | 1 |
| Front Right (FR) | 3 | 4 |
| Back Left (BL)   | 5 | 6 |
| Back Right (BR)  | 7 | 8 |

---

## 🧠 Gait Controller (`final.py`)

Every 20 ms, each joint follows a sinusoid around a gait-specific center angle:

```
t          = 2π · f · time + leg_phase
hip_angle  = center_hip  + hip_sign · A_hip · sin(t)          # hip_sign = -1 for left legs
knee_angle = center_knee + A_knee · sin(t + π/2)
                         - A_lift · (1 - cos(t)) / 2           # lifts the foot in swing
```

All commands are clamped to 0–240°.

### Gait Parameters

| Parameter | Walk (crawl) | Trot | Run |
|-----------|--------------|------|-----|
| Frequency | 0.4 Hz | 0.7 Hz | 1.5 Hz |
| Hip amplitude | ±15° | ±15° | ±15° |
| Knee amplitude | ±15° | ±15° | ±15° |
| Lift amplitude | 20° | 20° | 20° |
| Center hip / knee | 120° / 110° | 120° / 105° | 120° / 105° |
| Leg phases (FL, FR, BL, BR) | 0, π, 3π/2, π/2 | 0, π, π, 0 | 0, π, π, 0 |

Trot and run move diagonal pairs together (FL+BR, then FR+BL). Walk offsets each leg by a quarter cycle.

### Poses

| Pose | FL | FR | BL | BR |
|------|----|----|----|----|
| Stand (hip / knee) | 120° / 120° | 104° / 145° | 120° / 120° | 105° / 145° |
| Sit (hip / knee) | 120° / 50° | 120° / 50° | 120° / 50° | 120° / 50° |

---

## ▶️ Running

```bash
pip install pylx16a pyserial
python final.py
```

Set `SERVO_PORT` at the top of the script to your serial port (e.g. `/dev/ttyUSB0` on the Pi, `COM4` on Windows).

Commands at the prompt:

| Command | Action |
|---------|--------|
| `stand` | Move to calibrated standing pose |
| `sit`   | Move to sitting pose |
| `walk`  | Start crawl gait |
| `trot`  | Start trot gait |
| `run`   | Start fast trot |
| `stop`  | Stop gait and return to stand |
| `quit`  | Exit (robot returns to stand) |

Servo timeouts are caught and reported with the servo ID; Ctrl+C triggers a safe shutdown.

---

## 📂 Repository Structure

```
Kruger-Robot/
├── README.md
├── requirements.txt
├── code/
│   ├── final.py          # Main controller: QuadrupedRobot class, gaits, CLI
│   ├── leg_move.py       # Early diagonal-walk test (±35° swing, 0.4 Hz)
│   ├── servo-test.py     # PyQt6 GUI for testing/calibrating individual servos
│   └── sim/
│       ├── sim.py        # PyBullet gait simulation
│       └── quadruped.urdf
├── cad/
│   ├── DESIGN_1 v33.step # Full assembly
│   ├── Servo sideways mount v4.step
│   └── legs/             # femur, tibia, foot, links, shoulder disks per leg
├── docs/
│   └── Assignment4_LegMotion.pdf  # Leg motion, cable routing, form/fit fixes
└── images/
    ├── Kruger1.png       # Concept art + original sketch
    ├── Krugger.png       # Render, CAD, and leg-motion sequence
    ├── finalcad1.png
    └── finalcad2.png
```

---

## 🧠 My Role

- Designed and modeled the full mechanical leg system using Fusion 360
- Programmed servo control logic in Python using serial communication
- Tuned gait parameters, phase offsets, and per-leg standing calibration
- Tested robot performance and measured walking speed and stability

---

## 🔧 Lessons Learned

- Servo shaft depth was 4 mm on the real part vs. 3.45 mm in the GrabCAD model; mounts had to be adjusted
- 3D-printed screw holes come out undersized and need enlarging in CAD
- Leg-to-servo attachments were thickened and given counterbores for strength

---

## 🧩 Future Extensions

- Add IMU feedback for dynamic stability
- Integrate camera or LiDAR for autonomous navigation
- Replace open-loop sinusoids with inverse-kinematics foot trajectories
