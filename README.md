# Robot Arm Control System (ESP32 + Web + Joystick)

This project is a robotic arm control system developed using an ESP32 microcontroller, servo motors, joystick controller, and web interface.  
The system supports multiple control modes including hardware control, WiFi web control, and record & replay mode.

This project was created for robotics, IoT, and embedded system learning and research purposes.

---

## Features

- Control robot arm using joystick
- Control robot arm via Web Interface (WiFi Access Point)
- Record and replay movement
- Multiple operation modes
- OLED display status
- Multi-servo control
- Real-time control
- Mode switching with buttons

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
- Socket Web Server
- HTML / JavaScript frontend
- Python modules

---

## Schematics Details & Demo

### 🎥 Demo Video

[![Watch the video](https://img.youtube.com/vi/S12WYTP0wRI/maxresdefault.jpg)](https://youtu.be/S12WYTP0wRI)

▶ Watch on YouTube  
https://youtu.be/S12WYTP0wRI


---

### 📊 Slide Presentation

[View Slide](https://1drv.ms/p/c/b1be4b1a3bdb483a/IQCY_vCY0aerTYscldrCbHtiAX9ekC0YXBMc-wzQp-v9esw)

---

## Main Files

| File | Description |
|------|-----------|
| main.py | Main control program |
| mode.py | Mode control logic |
| wifi.py | WiFi web server |
| record.py | Record movement |
| replay.py | Replay movement |
| servo.py | Servo control |
| oled.py | OLED display |
| joystick.py | Joystick control |

---

## Future Development

- VR control support
- Remote control via Internet
- Camera streaming
- Surgical robot research
- AI assisted movement

---

## Author

Pannawat Lertkomenkul  
Ratchanon Laosamphan
Computer Science  
King Mongkut's Institute of Technology Ladkrabang
