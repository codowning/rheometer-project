import serial
import threading
import time
from pynput import keyboard

# =======================
# User Settings
# =======================
range_of_motion_deg = 360 # sets oscillation range (in degrees)

port = "COM3"
baud = 115200
microsteps = 2
range_of_motion_deg = 360
step_delay_us = 300     # minimum delay per step for max speed
accel_steps = 100        # steps for acceleration/deceleration
running = True

# derived settings
steps_per_rev = 240 * microsteps
pos_min = 0
pos_max = int(range_of_motion_deg / 360 * steps_per_rev)

# ----------------------
arduino = serial.Serial(port, baud, timeout=0.1)
time.sleep(2)

current_pos = 0

# ----------------------
def read_from_arduino():
    global current_pos
    while running:
        line = arduino.readline().decode(errors='ignore').strip()
        if line.startswith("POS:"):
            try:
                current_pos = int(line[4:])
            except ValueError:
                pass
        time.sleep(0.005)

thread = threading.Thread(target=read_from_arduino, daemon=True)
thread.start()

# ----------------------
# Send configuration
arduino.write(f"SETSPD {step_delay_us}\n".encode())
arduino.write(f"SETACC {accel_steps}\n".encode())
arduino.write(f"SETLIM {pos_min},{pos_max}\n".encode())

print(f"Oscillating {range_of_motion_deg}° at {microsteps}")
print("Controls:")
print("  s: start oscillation")
print("  p: stop oscillation")
print("  ESC: exit")

# ----------------------
def on_press(key):
    try:
        if key.char == 's':
            arduino.write(b"START\n")
            print("\nOscillation started.")
        elif key.char == 'p':
            arduino.write(b"STOP\n")
            print("\nOscillation stopped.")
    except AttributeError:
        pass

def on_release(key):
    global running
    if key == keyboard.Key.esc:
        running = False
        arduino.write(b"STOP\n")
        print("\nExiting...")
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

arduino.close()
print("Serial connection closed.")
