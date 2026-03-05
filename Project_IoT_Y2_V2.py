import os
import time
from machine import Pin, PWM, ADC, I2C
# ต้องมีไฟล์ ssd1306.py ในเครื่องเพื่อใช้จอ
# import ssd1306 

# ================= CONFIG =================
RECORD_FILE = "replay.txt"

# Servo Pins (S1-S4)
PIN_SERVO_15 = 15 # S1
PINS_OTHERS  = [16, 17, 18] # S2, S3, S4

STOP_DUTY = 4915
FAST_CW, FAST_CCW = 4200, 5600
SLOW_CW, SLOW_CCW = 3370, 6700
DEADZONE = 800

# ================= HARDWARE SETUP =================

# 1. Servos
servo_15 = PWM(Pin(PIN_SERVO_15), freq=50)
servos = {p: PWM(Pin(p), freq=50) for p in PINS_OTHERS}

# 2. Joysticks (ตาม Schematic: GPIO 4, 5)
joy1_x = ADC(Pin(4)); joy1_x.atten(ADC.ATTN_11DB)
joy2_x = ADC(Pin(5)); joy2_x.atten(ADC.ATTN_11DB)

# 3. Buttons (เรียงตาม Schematic SW1-SW7)
# SW1:GPIO8, SW2:GPIO9, SW3:GPIO10, SW4:GPIO11 (Select Servos)
# SW5:GPIO12 (Lock All), SW6:GPIO13 (Record), SW7:GPIO14 (Play)
btn_pins = [8, 9, 10, 11, 12, 13, 14]
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in btn_pins]

# 4. OLED Display (GPIO 2=SDA, GPIO 3=SCL)
# i2c = I2C(0, sda=Pin(2), scl=Pin(3))
# display = ssd1306.SSD1306_I2C(128, 64, i2c)

# ================= STATE =================
selected_idx = 0
global_lock = False
is_recording = False
start_time = 0
last_sent_duty = {}

cx1, cx2 = joy1_x.read(), joy2_x.read()

# ================= FUNCTIONS =================

def stop_all():
    servo_15.duty_u16(STOP_DUTY)
    for p in servos:
        servos[p].duty_u16(STOP_DUTY)

def get_duty(pin, delta):
    if abs(delta) < DEADZONE: return STOP_DUTY
    # S1 และ S3 เป็น Fast (15, 17) ตาม Logic เดิมของคุณ
    if pin in [15, 17]: return FAST_CW if delta > 0 else FAST_CCW
    return SLOW_CW if delta > 0 else SLOW_CCW

def write_log(pin, duty):
    if not is_recording: return
    ts = time.ticks_diff(time.ticks_ms(), start_time)
    if last_sent_duty.get(pin) == duty: return 
    with open(RECORD_FILE, "a") as f:
        f.write("{},{},{}\n".format(ts, pin, duty))
    last_sent_duty[pin] = duty

def play_replay():
    if is_recording: return
    try:
        if RECORD_FILE not in os.listdir(): return
        stop_all()
        with open(RECORD_FILE, "r") as f:
            replay_start = time.ticks_ms()
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 3: continue
                t, pin, duty = map(int, parts)
                while time.ticks_diff(time.ticks_ms(), replay_start) < t: pass 
                if pin == 15: servo_15.duty_u16(duty)
                elif pin in servos: servos[pin].duty_u16(duty)
        stop_all()
    except: stop_all()

def update():
    global selected_idx, global_lock, is_recording, start_time

    # --- SW7: Play (GPIO 14) ---
    if buttons[6].value() == 0:
        time.sleep_ms(300)
        play_replay()

    # --- SW6: Record (GPIO 13) ---
    if buttons[5].value() == 0:
        is_recording = not is_recording
        if is_recording:
            with open(RECORD_FILE, "w") as f: f.write("")
            start_time = time.ticks_ms()
            last_sent_duty.clear()
        time.sleep_ms(300)

    # --- SW5: Lock All (GPIO 12) ---
    if buttons[4].value() == 0:
        global_lock = not global_lock
        stop_all()
        time.sleep_ms(300)

    if global_lock: return

    # --- SW1-SW4: Select Servo (GPIO 8, 9, 10, 11) ---
    for i in range(4):
        if buttons[i].value() == 0:
            if i == 0: selected_idx = 15 # เลือก S1 โดยตรง
            else: selected_idx = PINS_OTHERS[i-1] # เลือก S2, S3, S4
            time.sleep_ms(200)

    # --- Joystick Control ---
    # บังคับเฉพาะตัวที่เลือกด้วย Joy1
    dx1 = joy1_x.read() - cx1
    d1 = get_duty(selected_idx, dx1)
    
    if selected_idx == 15:
        servo_15.duty_u16(d1)
    else:
        servos[selected_idx].duty_u16(d1)
    
    if is_recording: write_log(selected_idx, d1)

    time.sleep_ms(10)
