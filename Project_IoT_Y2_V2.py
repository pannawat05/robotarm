from machine import Pin, PWM, ADC
import time
import os

# ================= CONFIG =================
PIN_SERVO_15 = 15
PINS_OTHERS = [16, 17, 18]

STOP_DUTY = 4915
FAST_CW, FAST_CCW = 4200, 5600
SLOW_CW, SLOW_CCW = 3370, 6700
DEADZONE = 800

GRIP = 6700
RELEASE = 3370

RECORD_FILE = "replay.txt"

# ================= HARDWARE =================
servo_15 = PWM(Pin(PIN_SERVO_15), freq=50)
servos = {p: PWM(Pin(p), freq=50) for p in PINS_OTHERS}

joy1_x = ADC(Pin(4)); joy1_x.atten(ADC.ATTN_11DB)
joy2_x = ADC(Pin(5)); joy2_x.atten(ADC.ATTN_11DB)

# ปุ่ม 10, 11, 12, 13, 14
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in [10, 11, 12, 13 , 14]]

# พินตามโค้ดล่าสุดของคุณ (47 = Record, 48 = Replay)
rec_btn = Pin(47, Pin.IN, Pin.PULL_UP)
replay_btn = Pin(48, Pin.IN, Pin.PULL_UP)

# ================= STATE =================
selected_idx = 0
servo15_locked = False
global_lock = False
gripper_closed = False

is_recording = False
start_time = 0
last_duty = {}

cx1, cx2 = joy1_x.read(), joy2_x.read()

# ================= FUNCTIONS =================

def stop_all():
    servo_15.duty_u16(STOP_DUTY)
    for p in servos:
        servos[p].duty_u16(STOP_DUTY)

def get_duty(pin, delta):
    if abs(delta) < DEADZONE:
        return STOP_DUTY
    if pin in [15, 17]:
        return FAST_CW if delta > 0 else FAST_CCW
    return SLOW_CW if delta > 0 else SLOW_CCW

def write_log(pin, duty):

    if not is_recording:
        return

    ts = time.ticks_diff(time.ticks_ms(), start_time)

    if last_duty.get(pin) == duty:
        return

    with open(RECORD_FILE, "a") as f:
        f.write("{},{},{}\n".format(ts, pin, duty))

    last_duty[pin] = duty

def play_replay():

    if RECORD_FILE not in os.listdir():
        print("No replay file")
        return

    stop_all()
    time.sleep_ms(200)

    with open(RECORD_FILE, "r") as f:

        replay_start = time.ticks_ms()

        for line in f:

            parts = line.strip().split(",")

            if len(parts) != 3:
                continue

            t,pin,duty = map(int,parts)

            while time.ticks_diff(time.ticks_ms(), replay_start) < t:
                pass

            if pin == 15:
                servo_15.duty_u16(duty)

            elif pin in servos:
                servos[pin].duty_u16(duty)

    stop_all()
    print("Replay Done")

def toggle_gripper():
    global gripper_closed
    duty = RELEASE if gripper_closed else GRIP
    gripper_closed = not gripper_closed
    
    servos[18].duty_u16(duty)
    write_log(18, duty)
    time.sleep_ms(350)
    servos[18].duty_u16(STOP_DUTY)
    write_log(18, STOP_DUTY)

def start_all():
    print("[HARDWARE MODE]")
    stop_all()

# ================= UPDATE LOOP =================

def update():
    global selected_idx, servo15_locked, global_lock
    global is_recording, start_time

  

    # 1. Global Lock
    if buttons[4].value() == 0:
        global_lock = not global_lock
        stop_all()
        print("Global Lock status:", global_lock)
        time.sleep_ms(300)
    if global_lock: return

    # 2. Select Servo
    for i in [1, 2]: 
        if buttons[i].value() == 0:
            selected_idx = i - 1
            print("Selected Servo:", PINS_OTHERS[selected_idx])
            time.sleep_ms(250)

    # --- JOYSTICK CONTROL ---
    current_pin = PINS_OTHERS[selected_idx]
    dx1 = joy1_x.read() - cx1
    duty1 = get_duty(current_pin, dx1)
    servos[current_pin].duty_u16(duty1)
    write_log(current_pin, duty1)

    if not servo15_locked:
        dx2 = joy2_x.read() - cx2
        duty15 = get_duty(15, dx2)
        servo_15.duty_u16(duty15)
        write_log(15, duty15)
    else:
        servo_15.duty_u16(STOP_DUTY)
    
    # 3. ปุ่มกดอื่นๆ
    if buttons[0].value() == 0: # Lock S15
        servo15_locked = not servo15_locked
        print("Servo15 Locked:", servo15_locked)
        time.sleep_ms(300)

    if buttons[3].value() == 0: # Gripper (Pin 13)
        print("Gripper button pressed!")
        toggle_gripper()
        time.sleep_ms(300)

    # 4. Record (47)
    if rec_btn.value() == 0:
        is_recording = not is_recording
        print("Recording:", "ON" if is_recording else "OFF")
        if is_recording:
            with open(RECORD_FILE, "w") as f: f.write("")
            start_time = time.ticks_ms()
            last_duty.clear()
        time.sleep_ms(400)
        
    # 5. Replay (48)
    if replay_btn.value() == 0:
        print("Replay button pressed!")
        play_replay()
        time.sleep_ms(400)

