# PicoKeyboard - CircuitPython version
# -------------------------------------
# Runs automatically every time the Pico is powered/plugged in.
# No IDE, compiler, or upload tool needed after the one-time setup.
#
# Hardware:
#   - Button 1 (macro button)     between GP3 and GND
#   - Button 2 (clipboard button) between GP0 and GND
#     (internal pull-ups used, no external resistors needed)
#   - Onboard WS2812 RGB LED (GP16 on the RP2040-Zero) used as a
#     status indicator: green blink = alive, red blink = error
#
# Behavior:
#   - Button 1 short press -> types a short macro string + Enter
#   - Button 1 long press  -> types a different macro string + Enter
#   - Button 2 press       -> reads /clipboard.txt from the CIRCUITPY
#                              drive and types its contents line by line
#   - LED blinks once a second while idle (alive/heartbeat)
#   - LED blinks fast a few times if clipboard.txt is missing
#
# To change what button 2 types: just edit clipboard.txt directly on
# the CIRCUITPY drive with any text editor and save. No re-flash, no
# code changes, no IDE involved.

import time
import board
import digitalio
import neopixel_write
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# ---- Configuration ---------------------------------------------------

SHORT_MACRO = "Hello from Pico!"
LONG_MACRO = "This is the long-press macro."
CLIPBOARD_FILE = "/clipboard.txt"

LONGPRESS_S = 1.0     # seconds held to count as a long press
DEBOUNCE_S = 0.03      # debounce time for both buttons
LINE_PACING_S = 0.01   # small delay between typed lines (increase if
                       # the host drops/scrambles characters)

# ---- Setup -------------------------------------------------------------

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

button = digitalio.DigitalInOut(board.GP3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

clip_button = digitalio.DigitalInOut(board.GP0)
clip_button.direction = digitalio.Direction.INPUT
clip_button.pull = digitalio.Pull.UP

# RP2040-Zero has a single WS2812 RGB LED on GP16 (no plain LED).
# Driven with the built-in neopixel_write module, so no extra library
# is needed. Colors are kept dim on purpose - these LEDs are bright.
pixel_pin = digitalio.DigitalInOut(getattr(board, "NEOPIXEL", board.GP16))
pixel_pin.direction = digitalio.Direction.OUTPUT

GREEN = (0, 20, 0)   # heartbeat
RED = (30, 0, 0)     # error (clipboard.txt missing)
OFF = (0, 0, 0)


def set_led(color):
    r, g, b = color
    # WS2812 on the RP2040-Zero expects GRB byte order
    neopixel_write.neopixel_write(pixel_pin, bytearray([g, r, b]))


set_led(OFF)

# ---- Helpers -------------------------------------------------------------

def type_line(text):
    layout.write(text)
    kbd.press(Keycode.ENTER)
    time.sleep(0.02)
    kbd.release(Keycode.ENTER)


def type_clipboard_file():
    try:
        with open(CLIPBOARD_FILE, "r") as f:
            for line in f:
                line = line.rstrip("\r\n")
                layout.write(line)
                kbd.press(Keycode.ENTER)
                time.sleep(0.01)
                kbd.release(Keycode.ENTER)
                time.sleep(LINE_PACING_S)
    except OSError:
        # File missing - blink red fast a few times instead of typing nothing
        for _ in range(3):
            set_led(RED)
            time.sleep(0.1)
            set_led(OFF)
            time.sleep(0.1)


# ---- Main loop -------------------------------------------------------------

last_button_state = True   # True = released (pulled up)
button_pressed = False
press_start_time = 0.0
last_debounce_time = 0.0

last_clip_state = True
clip_pressed = False
last_clip_debounce_time = 0.0

last_blink = time.monotonic()
led_state = False

while True:
    now = time.monotonic()

    # Heartbeat LED
    if now - last_blink > 1.0:
        last_blink = now
        led_state = not led_state
        set_led(GREEN if led_state else OFF)

    # --- Button 1: macro button (short vs long press) ---
    reading = button.value  # True = released, False = pressed

    if reading != last_button_state:
        last_debounce_time = now

    if now - last_debounce_time > DEBOUNCE_S:
        if reading is False and not button_pressed:
            button_pressed = True
            press_start_time = now

        if reading is True and button_pressed:
            button_pressed = False
            held_for = now - press_start_time
            if held_for >= LONGPRESS_S:
                type_line(LONG_MACRO)
            else:
                type_line(SHORT_MACRO)

    last_button_state = reading

    # --- Button 2: clipboard/file button ---
    clip_reading = clip_button.value  # True = released, False = pressed

    if clip_reading != last_clip_state:
        last_clip_debounce_time = now

    if now - last_clip_debounce_time > DEBOUNCE_S:
        if clip_reading is False and not clip_pressed:
            clip_pressed = True
            type_clipboard_file()

        if clip_reading is True and clip_pressed:
            clip_pressed = False

    last_clip_state = clip_reading

    time.sleep(0.005)
