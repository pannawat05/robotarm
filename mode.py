from machine import Pin
import time

boot = Pin(0, Pin.IN, Pin.PULL_UP)

mode = 0  # 0=MOBILE, 1=HARDWARE, 2=OFF

press_time = None
LONG_PRESS_MS = 600


def update_mode():
    global mode, press_time

    if boot.value() == 0:  # กดอยู่
        if press_time is None:
            press_time = time.ticks_ms()

    else:  # ปล่อยแล้ว
        if press_time is not None:
            duration = time.ticks_diff(time.ticks_ms(), press_time)
            press_time = None

            # ----- LONG PRESS -----
            if duration > LONG_PRESS_MS:
                if mode == 0:
                    mode = 1
                else:
                    mode = 0

            # ----- SHORT PRESS -----
            else:
                mode = 2

    return mode   # 🔥 ต้อง return ตลอด


# while True:
#     m = update_mode()
#     print("Mode:", m)
#     time.sleep_ms(20)