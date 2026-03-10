from machine import Pin, PWM
import time
import network
import socket
import os

# =========================
# WIFI SETUP
# =========================
ap = None

def start_wifi():
    global ap

    try:
        network.WLAN(network.AP_IF).active(False)
        network.WLAN(network.STA_IF).active(False)
        time.sleep(1)
    except:
        pass

    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESP32-Robot", password="12345678", authmode=3)

    while not ap.active():
        pass

    print("AP IP:", ap.ifconfig()[0])

# =========================
# SERVO CONFIG
# =========================
STOP_DUTY = 4915
FAST_CW   = 4200
FAST_CCW  = 5600
SLOW_CW   = 3370
SLOW_CCW  = 6700

RECORD_FILE = "replay.txt"

servos = {
    15: PWM(Pin(15), freq=50),
    16: PWM(Pin(16), freq=50),
    17: PWM(Pin(17), freq=50),
    18: PWM(Pin(18), freq=50)
}

last_duty = {15: STOP_DUTY,16: STOP_DUTY,17: STOP_DUTY,18: STOP_DUTY}

is_recording = False
start_time = 0

# =========================
# SERVER CONTROL
# =========================
server_running = False
server_socket = None

# =========================
# SERVO CONTROL
# =========================
def set_servo(pin, duty):

    global last_duty

    duty = max(3000, min(7000, duty))

    if pin in servos:

        servos[pin].duty_u16(duty)

        if is_recording and duty != last_duty[pin]:

            write_log(pin,duty)
            last_duty[pin] = duty

def stop_all():

    for pin in servos:
        servos[pin].duty_u16(STOP_DUTY)

    print("All Servos Stopped")

# =========================
# RECORD
# =========================
def write_log(pin,duty):

    ts = time.ticks_diff(time.ticks_ms(),start_time)

    with open(RECORD_FILE,"a") as f:
        f.write("{},{},{}\n".format(ts,pin,duty))

# =========================
# REPLAY
# =========================
def play_replay():

    global is_recording

    if is_recording:
        return

    try:

        stop_all()

        time.sleep(0.5)

        with open(RECORD_FILE,"r") as f:

            replay_start = time.ticks_ms()

            for line in f:

                parts = line.strip().split(",")

                if len(parts) != 3:
                    continue

                t = int(parts[0])
                pin = int(parts[1])
                duty = int(parts[2])

                while time.ticks_diff(time.ticks_ms(),replay_start) < t:
                    time.sleep_ms(1)

                if pin in servos:
                    servos[pin].duty_u16(duty)

        stop_all()

        print("Replay Done")

    except Exception as e:

        print("Replay Error:",e)

        stop_all()

# =========================
# API
# =========================
def handle_api(path):

    global is_recording,start_time

    print("PATH:",path)

    try:

        if path == "/s15_cw":
            set_servo(15,SLOW_CW)

        elif path == "/s15_ccw":
            set_servo(15,SLOW_CCW)

        elif path == "/s16_cw":
            set_servo(16,SLOW_CW)

        elif path == "/s16_ccw":
            set_servo(16,SLOW_CCW)

        elif path == "/s17_cw":
            set_servo(17,FAST_CW)

        elif path == "/s17_ccw":
            set_servo(17,FAST_CCW)

        elif path == "/s18_cw":
            set_servo(18,SLOW_CW)

        elif path == "/s18_ccw":
            set_servo(18,SLOW_CCW)

        elif path == "/stop":
            stop_all()

        elif path == "/record":

            is_recording = not is_recording

            if is_recording:

                with open(RECORD_FILE,"w") as f:
                    f.write("")

                start_time = time.ticks_ms()

                print("Recording Start")

            else:

                print("Recording Stop")

        elif path == "/replay":

            play_replay()

    except Exception as e:

        print("API Error:",e)

# =========================
# STATIC FILE
# =========================
def send_file(cl,filename,content_type):

    try:

        with open(filename,"rb") as f:

            cl.send("HTTP/1.1 200 OK\r\n")
            cl.send("Content-Type: {}\r\n\r\n".format(content_type))

            while True:

                chunk = f.read(1024)

                if not chunk:
                    break

                cl.send(chunk)

    except:

        cl.send("HTTP/1.1 404 Not Found\r\n\r\n")

# =========================
# WEB SERVER
# =========================
def start_server():

    global server_running,server_socket

    start_wifi()

    server_running = True

    s = socket.socket()

    server_socket = s

    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    s.bind(('0.0.0.0',80))

    s.listen(5)

    print("Server Ready")

    while server_running:

        try:

            cl,addr = s.accept()

        except:

            continue

        try:

            req = cl.recv(1024).decode()

            if not req:
                cl.close()
                continue

            path = req.split(" ")[1]

            if path == "/" or path == "/index.html":

                send_file(cl,"dist/index.html","text/html")

            elif path.startswith("/assets/"):

                filename = "dist" + path

                if filename.endswith(".js"):
                    send_file(cl,filename,"application/javascript")

                elif filename.endswith(".css"):
                    send_file(cl,filename,"text/css")

                elif filename.endswith(".svg"):
                    send_file(cl,filename,"image/svg+xml")

                else:
                    send_file(cl,filename,"application/octet-stream")

            elif path.startswith("/s") or path in ["/stop","/record","/replay"]:

                handle_api(path)

                cl.send("HTTP/1.1 200 OK\r\n")
                cl.send("Content-Type: text/plain\r\n\r\n")
                cl.send("OK")

            else:

                cl.send("HTTP/1.1 404 Not Found\r\n\r\n")

        except Exception as e:

            print("Server Error:",e)

        cl.close()

    try:
        s.close()
    except:
        pass

    print("Server Closed")

# =========================
# STOP SERVER
# =========================
def stop_server():

    global server_running,server_socket

    server_running = False

    try:
        if server_socket:
            server_socket.close()
    except:
        pass

    print("WiFi Server stopped")
