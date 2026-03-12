# Robot Arm Control System (ESP32 + Web + Joystick)

This project is a robotic arm control system developed using ESP32 microcontroller, servo motors, joystick controller, and web interface.  
The system can control the robotic arm in multiple modes including hardware control, WiFi web control, and record & replay mode.

This project was created for robotics / IoT / embedded system learning and research purposes.

---

## Features

- Control robot arm using joystick
- Control robot arm via Web Interface (WiFi Access Point)
- Record and Replay movement
- Multiple operation modes
- OLED display status
- Multi-servo control
- Real-time control

---

## System Overview

The system consists of:

- ESP32 microcontroller
- 4 Servo motors
- Joystick module
- Push buttons
- OLED display
- WiFi Web server
- Robot arm structure

Robot arm can be controlled in 3 modes:

| Mode | Description |
|------|------------|
| Mode 0 | Hardware control (Joystick) |
| Mode 1 | WiFi Web control |
| Mode 2 | Disabled mode |

---

## Hardware Used

- ESP32
- Servo Motor x4
- Joystick Module
- Push Button x7
- OLED SSD1306
- Robot Arm Kit

---

## Software Used

- MicroPython
- ESP32 firmware
- Web server (socket)
- HTML / JS frontend
- Python modules

Main files
