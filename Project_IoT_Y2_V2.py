# hardware.py
from machine import Pin, PWM, ADC
import time

# ================= CONFIG =================
PIN_SERVO_15 = 15
PINS_OTHERS = [16, 17, 18]

STOP_DUTY = 4915
FAST_CW, FAST_CCW = 4200, 5600
SLOW_CW, SLOW_CCW = 3370, 6700
DEADZONE = 800

# ================= HARDWARE =================
servo_15 = PWM(Pin(PIN_SERVO_15), freq=50)
servos = {p: PWM(Pin(p), freq=50) for p in PINS_OTHERS}

joy1_x = ADC(Pin(4)); joy1_x.atten(ADC.ATTN_11DB)
joy2_x = ADC(Pin(5)); joy2_x.atten(ADC.ATTN_11DB)

buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in [10,11,12,13,14]]

# ================= STATE =================
selected_idx = 0
servo15_locked = False
global_lock = False

cx1, cx2 = joy1_x.read(), joy2_x.read()

# ================= FUNCTIONS =================
def stop_all():
    servo_15.duty_u16(STOP_DUTY)
    for p in servos:
        servos[p].duty_u16(STOP_DUTY)

def get_duty(pin, delta):
    if abs(delta) < DEADZONE:
        return STOP_DUTY
    if pin in [15,17]:
        return FAST_CW if delta > 0 else FAST_CCW
    return SLOW_CW if delta > 0 else SLOW_CCW

def start_all():
    print("[HARDWARE MODE]")
    stop_all()

def update():
    global selected_idx, servo15_locked, global_lock

    if buttons[4].value() == 0:
        global_lock = not global_lock
        stop_all()
        time.sleep_ms(300)

    if global_lock:
        stop_all()
        return

    # Select servo
    for i in [1,2]:
        if buttons[i].value() == 0:
            selected_idx = i - 1
            time.sleep_ms(300)

    # Joy1
    current_pin = PINS_OTHERS[selected_idx]
    dx1 = joy1_x.read() - cx1
    servos[current_pin].duty_u16(get_duty(current_pin, dx1))

    # Lock Servo15
    if buttons[0].value() == 0:
        servo15_locked = not servo15_locked
        time.sleep_ms(300)

    # Joy2
    if not servo15_locked:
        dx2 = joy2_x.read() - cx2
        servo_15.duty_u16(get_duty(15, dx2))
    else:
        servo_15.duty_u16(STOP_DUTY)