from machine import Pin, I2C
from time import sleep
from ssd1306 import SSD1306_I2C
import mode
import Project_IoT_Y2_V2
import Project_IoT_Y2_V2_wifi
import test
import _thread

# ================= OLED INIT =================
def init_oled():
    global i2c, oled
    try:
        i2c = I2C(1, scl=Pin(40), sda=Pin(41), freq=100000)
        oled = SSD1306_I2C(128, 64, i2c, addr=0x3c)
        print("OLED Ready")
    except Exception as e:
        print("OLED Error:", e)
        oled = None

# ================= WIFI SERVER CONTROL =================
server_running = False
server_thread = None

def run_wifi_server():
    global server_running
    try:
        Project_IoT_Y2_V2_wifi.start_server()
    except Exception as e:
        print("WiFi Server Error:", e)
    finally:
        server_running = False
        print("WiFi Server Stopped")

# ================= STARTUP =================
oled = None
i2c = None
init_oled()
current_mode = -1
print("=== SYSTEM READY ===")

# ================= MAIN LOOP =================
while True:
    new_m = mode.update_mode()
    
    # -------- Mode Change --------
    if new_m != current_mode:
        current_mode = new_m
        print("Mode:", current_mode)
        
        # ========== หยุดทุกอย่างก่อน ==========
        try:
            Project_IoT_Y2_V2.stop_all()
        except Exception as e:
            print("Error stopping hardware:", e)
        
        # หยุด WiFi server ถ้ากำลังทำงาน
        if server_running:
            try:
                Project_IoT_Y2_V2_wifi.stop_all()
                server_running = False
                sleep(0.5)  
                print("WiFi Server stopped")
            except Exception as e:
                print("Error stopping WiFi server:", e)
                server_running = False
        
        # ========== MODE 0: HARDWARE MODE ========== 
        if current_mode == 0:
            try:
                Project_IoT_Y2_V2.start_all()
                if oled:
                    test.display_mode0(oled)
                print("HARDWARE MODE started")
            except Exception as e:
                print("Error starting hardware mode:", e)
        
        # ========== MODE 1: WIFI MODE ==========
        elif current_mode == 1:
            try:
                if oled:
                    test.display_mode1(oled)
                print("Entering WiFi Mode...")
                sleep(0.5)
                
                # รัน server ใน thread แยก
                server_running = True
                server_thread = _thread.start_new_thread(run_wifi_server, ())
                print("WiFi Server started in background thread")
            except Exception as e:
                print("Error starting WiFi mode:", e)
                server_running = False
        
        # ========== MODE 2: DISABLED ==========
        elif current_mode == 2:
            try:
                if oled:
                    test.display_disabled(oled)
                print("DISABLED MODE")
            except Exception as e:
                print("Error in disabled mode:", e)
    
    # -------- RUN LOOP --------
    try:
        if current_mode == 0:
            # HARDWARE MODE
            Project_IoT_Y2_V2.update()
        elif current_mode == 1:
            # WIFI MODE - server running in background
            sleep(0.1)
        elif current_mode == 2:
            # DISABLED MODE
            sleep(0.1)
    except Exception as e:
        print("Error in main loop:", e)
    
    sleep(0.02)
