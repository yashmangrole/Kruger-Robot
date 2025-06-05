# Kruger: Quadrupedal Walking Robot

**Kruger** is a 4-legged walking robot developed as part of the Robotics Studio course at Columbia University. It features a unique parallel leg mechanism and a custom gait algorithm implemented on a Raspberry Pi for real-time control of LX-16A servo motors.

---

## 🦿 Key Features

- Parallel leg linkage for synchronized, efficient walking
- Gait control using ±12° swing around calibrated center angles
- Real-time control using **Raspberry Pi + Python**
- Max walking speed: **25.7 cm/sec**
- Designed for terrain stability and modular gait tuning

---

## 🛠️ System Architecture

- **Controller**: Raspberry Pi 4 (Raspbian OS)
- **Actuators**: LX-16A Serial Bus Servo Motors
- **Control Interface**: Python (PySerial) via UART
- **Mechanical Design**: **Fusion 360 CAD** + 3D Printed PLA Components

---

## 📂 Repository Structure

```
Kruger-Robot/
├── README.md
├── code/
│   ├── gait_control.py
│   ├── servo_interface.py
├── images/
│   ├── kruger_cad.png
│   ├── walking_test.gif
├── docs/
│   └── Kruger_TechSpec.pdf (coming soon)
├── cad/
│   ├── kruger_assembly.f3d
│   └── renders/
│       ├── front_view.png
│       ├── isometric_exploded.png
```

---

## 📽️ Demo Video

_Add walking test demo here (GIF or YouTube link)_

---

## 🧠 My Role

- Designed and modeled the full mechanical leg system using Fusion 360
- Programmed servo control logic on Raspberry Pi using Python and serial communication
- Tuned gait parameters and synchronized servo phases
- Tested robot performance and measured walking speed and stability

---

## 📑 Coming Soon

- Full technical specification (design rationale, control diagrams, tuning process)
- Additional gait variations (trot, crawl, stability test)

---

## 🧩 Future Extensions

- Add IMU feedback for dynamic stability
- Integrate camera or LiDAR for autonomous navigation
