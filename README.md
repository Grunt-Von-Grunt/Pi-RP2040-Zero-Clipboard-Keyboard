# PicoKeyboard (CircuitPython version)

A Waveshare RP2040-Zero that acts as a USB keyboard. Two buttons: one types
short built-in macros, the other types out the contents of a text file
that lives directly on the Pico's own drive.

**Design goal:** after the one-time setup below, editing what gets typed
requires no software at all — just drag-and-drop a text file onto the
Pico like it's a USB stick.

## Hardware

- Waveshare RP2040-Zero (RP2040-based, USB-C)
- Button 1 (macro button): one leg to **GP3**, other leg to **GND**
- Button 2 (clipboard button): one leg to **GP0**, other leg to **GND**
  - (internal pull-ups are used in software, no resistors needed)

## One-time setup (the only part that needs a computer)

1. **Flash CircuitPython onto the Pico** (only needs doing once, ever):
   - Download the CircuitPython UF2 for Pico from
     `https://circuitpython.org/board/waveshare_rp2040_zero/`
   - Hold the **BOOT** button on the board while plugging it into USB.
     It will appear as a drive named `RPI-RP2`.
   - Drag the downloaded `.uf2` file onto that drive. The Pico reboots
     automatically and now shows up as a drive named **`CIRCUITPY`**.
     This step is a firmware flash, not "installing an IDE" — after
     this, the Pico permanently understands Python files dropped onto it.

2. **Copy these three items onto the CIRCUITPY drive**, replacing
   anything already there with the same name:
   - `code.py` (runs automatically every time the Pico powers up)
   - `clipboard.txt` (the text that gets typed by button 2)
   - the whole `lib/adafruit_hid/` folder (the keyboard library code.py
     depends on — a plain folder copy, not an install step)

   Your CIRCUITPY drive should look like:
   ```
   CIRCUITPY/
     code.py
     clipboard.txt
     lib/
       adafruit_hid/
         __init__.py
         keyboard.py
         keyboard_layout_us.py
         keycode.py
         ... (etc)
   ```

3. Eject/unplug and plug back in. Wire up the two buttons. Done —
   everything from here on is just drag-and-drop.

## Day-to-day use (no software involved)

- Plug the Pico into any computer. It shows up as **both** a USB
  keyboard and a small USB drive (`CIRCUITPY`) at the same time.
- To change what button 2 types: open `clipboard.txt` on that drive
  in any text editor (Notepad, TextEdit, whatever), edit it, hit save.
  The Pico picks up the new content immediately — no re-flash, no
  IDE, no button-pressing sequence.
- **Button 1, short press** → types `Hello from Pico!` + Enter.
- **Button 1, long press** (held > 1 second) → types a different
  built-in macro string + Enter.
- **Button 2, press** → types out `clipboard.txt`, line by line, using
  Enter for each line break. If the file's missing, the LED flashes
  red a few times instead of typing anything.
- The onboard RGB LED blinks **green** once a second as a heartbeat,
  and flashes **red** if `clipboard.txt` is missing.

## Notes

- CircuitPython briefly restarts `code.py` whenever a file changes on
  the drive (its normal "soft reload" behavior) — this is expected and
  takes under a second.
- The per-line pacing delay (`LINE_PACING_S` near the top of `code.py`)
  can be increased if a particular host seems to drop or scramble
  characters, or decreased for faster typing.
- If you ever do want to change the *behavior* (not just the clipboard
  text) — different macros, more buttons, modifier-key shortcuts — that
  still just means editing `code.py` directly on the drive the same
  way; no compiler step exists in CircuitPython at all.
- No special OS permissions or drivers are needed on Windows, macOS, or
  Linux for either the keyboard or the drive — both are natively
  supported everywhere.

## RP2040-Zero notes

- It has no plain LED; the single onboard WS2812 RGB LED (GP16) is driven
  with the built-in `neopixel_write` module, so no extra library is needed.
- If the LED colors look swapped (e.g. red instead of green), change the
  byte order in `set_led()` in `code.py`.
- GP0 and GP3 are both broken out on the board's edge pads.
