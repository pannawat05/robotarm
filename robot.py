from machine import Pin, PWM, ADC
import time
import os

pin_15 = 15
pins_others = [16, 17, 18]

servo_15 = PWM(Pin(pin_15), freq=50)
servos_joy1 = [PWM(Pin(p), freq=50) for p in pins_others]

STOP_DUTY = 4915

# สำหรับ servo 15 และ 17
FAST_CW  = 4200
FAST_CCW = 5600

# สำหรับ servo 16 และ 18
SLOW_CW  = 3370
SLOW_CCW = 6700

# ปุ่ม Record (47) และ Replay (48)
btn_record = Pin(47, Pin.IN, Pin.PULL_UP)
btn_replay = Pin(48, Pin.IN, Pin.PULL_UP)

DEADZONE = 800
selected_idx = 0 
servo15_locked = False
system_global_lock = False 

s18_direction_cw = True
is_recording = False
record_file = "replay.txt"
start_time = 0
last_duties = {15: STOP_DUTY, 16: STOP_DUTY, 17: STOP_DUTY, 18: STOP_DUTY}

joy1_x = ADC(Pin(4))
joy1_x.atten(ADC.ATTN_11DB)
joy2_x = ADC(Pin(5))
joy2_x.atten(ADC.ATTN_11DB)

button_pins = [10, 11, 12, 13, 14]
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in button_pins]

def stop_all():
    servo_15.duty_u16(STOP_DUTY)
    for s in servos_joy1:
        s.duty_u16(STOP_DUTY)
    for key in last_duties: last_duties[key] = STOP_DUTY

def write_log(servo_id, duty):
    global start_time
    if is_recording:
        timestamp = time.ticks_diff(time.ticks_ms(), start_time)
        try:
            with open(record_file, "a") as f:
                f.write("{},{},{}\n".format(timestamp, servo_id, duty))
        except: pass

def play_replay():
    if is_recording: return
    try:
        print("\n[START] REPLAYING...")
        stop_all()
        time.sleep(1) 
        
        with open(record_file, "r") as f:
            replay_start = time.ticks_ms()
            for line in f:
                # --- ส่วนเช็คเพื่อยกเลิก ---
                # ถ้ากดปุ่ม 48 (btn_replay) อีกครั้งขณะกำลังเล่น
                if btn_replay.value() == 0:
                    print("\n[STOP] REPLAY ABORTED")
                    stop_all()
                    time.sleep(0.5) # ป้องกันการกดซ้อน
                    return # ออกจากฟังก์ชันทันที
                
                if not line.strip(): continue
                t, s_id, duty = map(int, line.strip().split(','))
                
                # รอจนกว่าจะถึงเวลา แต่ต้องเช็คปุ่มยกเลิกไปด้วย
                while time.ticks_diff(time.ticks_ms(), replay_start) < t:
                    if btn_replay.value() == 0:
                        print("\n[STOP] REPLAY ABORTED!")
                        stop_all()
                        time.sleep(0.5)
                        return
                    time.sleep(0.001) # พักเล็กน้อยเพื่อให้ระบบไม่ค้าง
                
                if s_id == 15:
                    servo_15.duty_u16(duty)
                else:
                    idx = pins_others.index(s_id)
                    servos_joy1[idx].duty_u16(duty)
                    
        stop_all()
        print("[SUCCESS] REPLAY DONE")
    except Exception as e: 
        print("[ERROR] Replay Error:", e)
        stop_all()

print("\n--- SYSTEM READY ---")
stop_all()
cx1, cx2 = joy1_x.read(), joy2_x.read()

try:
    while True:
        # --- Record / Replay Buttons ---
        if btn_record.value() == 0:
            is_recording = not is_recording
            if is_recording:
                print("\n[●] RECORDING STARTED")
                with open(record_file, "w") as f: f.write("") 
                start_time = time.ticks_ms()
                for s_id, duty in last_duties.items(): write_log(s_id, duty)
            else: 
                print("[○] RECORDING STOPPED")
            time.sleep(0.5)

        if btn_replay.value() == 0: 
            play_replay()

        # --- Master Lock (Pin 14) ---
        if buttons[4].value() == 0:
            system_global_lock = not system_global_lock
            stop_all()
            print("\n[!] MASTER LOCK:", "ACTIVE" if system_global_lock else "DISABLED")
            time.sleep(0.5)

        if not system_global_lock:
            # --- ปุ่ม 13: คุมเฉพาะ Servo 18 ---
            if buttons[3].value() == 0:
                s18_direction_cw = not s18_direction_cw
                duty_s18 = SLOW_CW if s18_direction_cw else SLOW_CCW
                print(">>> Servo 18 Toggle:", "CW" if s18_direction_cw else "CCW")
                
                servos_joy1[2].duty_u16(duty_s18)
                write_log(18, duty_s18)
                last_duties[18] = duty_s18
                time.sleep(0.3)
                
                servos_joy1[2].duty_u16(STOP_DUTY)
                write_log(18, STOP_DUTY)
                last_duties[18] = STOP_DUTY
                time.sleep(0.2)

            # --- ปุ่ม 11, 12: เลือก Servo 16, 17 ---
            for i in [1, 2]:
                if buttons[i].value() == 0:
                    servos_joy1[selected_idx].duty_u16(STOP_DUTY)
                    selected_idx = i - 1
                    print(">>> Selected Servo GPIO:", pins_others[selected_idx])
                    time.sleep(0.3)

            # --- Joy 1 Control (16 ช้า / 17 แรง) ---
            val1 = joy1_x.read()
            dx1 = val1 - cx1
            if selected_idx < 2: 
                curr_id1 = pins_others[selected_idx]
                duty1 = STOP_DUTY
                
                if curr_id1 == 17:
                    if dx1 > DEADZONE: duty1 = FAST_CW
                    elif dx1 < -DEADZONE: duty1 = FAST_CCW
                else:
                    if dx1 > DEADZONE: duty1 = SLOW_CW
                    elif dx1 < -DEADZONE: duty1 = SLOW_CCW
                
                servos_joy1[selected_idx].duty_u16(duty1)
                if duty1 != last_duties[curr_id1]:
                    write_log(curr_id1, duty1)
                    last_duties[curr_id1] = duty1

            # --- ปุ่ม 10: Lock Servo 15 ---
            if buttons[0].value() == 0:
                servo15_locked = not servo15_locked
                print(">>> Servo 15 Lock:", "ON" if servo15_locked else "OFF")
                time.sleep(0.3)

            # --- Joy 2 Control (Servo 15) ---
            duty15 = STOP_DUTY
            if not servo15_locked:
                val2 = joy2_x.read()
                dx2 = val2 - cx2
                if dx2 > DEADZONE: duty15 = FAST_CW
                elif dx2 < -DEADZONE: duty15 = FAST_CCW
            
            servo_15.duty_u16(duty15)
            if duty15 != last_duties[15]:
                write_log(15, duty15)
                last_duties[15] = duty15
        else:
            stop_all()

        time.sleep(0.02)

except KeyboardInterrupt:
    stop_all()
    print("\n[STOP] Program Stopped by User")
