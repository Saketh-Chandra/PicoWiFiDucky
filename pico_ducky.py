# This file is derived from the file 'duckyinpython.py' in the 'pico-ducky'
# repository (https://github.com/dbisu/pico-ducky), which is licensed
# under GPLv2.0. This modified file is licensed under GPLv3.
#
# Copyright (c) 2023 Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Modified by: Saketh Chandra(Saketh-Chandra, @Saketh-Chandra)



import time
import board
import digitalio

import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode



class PicoDucky:

    def __init__(self,delay = 0) -> None:
        self.kbd = Keyboard(usb_hid.devices)
        self.layout = KeyboardLayout(self.kbd)
        self.defaultDelay = delay
        self.previousLine = ""
        self.duckyCommands = {
            'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
            'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
            'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
            'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
            'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
            'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
            'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
            'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
            'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
            'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
            'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
            'BACKSPACE': Keycode.BACKSPACE,
            'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
            'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
            'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
            'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
            'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
            'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
            'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
            'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
            'F12': Keycode.F12,
        }
        self.led = digitalio.DigitalInOut(board.LED)
        self.led.direction = digitalio.Direction.OUTPUT
        self.led.value = False

    def convertLine(self, line):
        newline = []
        # loop on each key - the filter removes empty values
        for key in filter(None, line.split(" ")):
            key = key.upper()
            # find the keycode for the command in the list
            command_keycode = self.duckyCommands.get(key, None)
            if command_keycode is not None:
                # if it exists in the list, use it
                newline.append(command_keycode)
            elif hasattr(Keycode, key):
                # if it's in the Keycode module, use it (allows any valid keycode)
                newline.append(getattr(Keycode, key))
            else:
                # if it's not a known key name, show the error for diagnosis
                print(f"Unknown key: <{key}>")
        return newline

    def runScriptLine(self, line):
        for k in line:
            self.kbd.press(k)
        self.kbd.release_all()

    def sendString(self, line):
        self.layout.write(line)

    def parseLine(self, line):

        if (line[0:3] == "REM"):
            # ignore ducky script comments
            pass
        elif (line[0:5] == "DELAY"):
            time.sleep(float(line[6:])/1000)
        elif (line[0:6] == "STRING"):
            self.sendString(line[7:])
        elif (line[0:5] == "PRINT"):
            print("[SCRIPT]: " + line[6:])
        elif (line[0:6] == "IMPORT"):
            self.runScript(line[7:])
        elif (line[0:13] == "DEFAULT_DELAY"):
            self.defaultDelay = int(line[14:]) * 10
        elif (line[0:12] == "defaultDelay"):
            self.defaultDelay = int(line[13:]) * 10
        elif (line[0:3] == "LED"):
            if (self.led.value == True):
                self.led.value = False
            else:
                self.led.value = True
        else:
            newScriptLine = self.convertLine(line)
            self.runScriptLine(newScriptLine)

    def runScript(self, line):

        line = line.rstrip()
        if (line[0:6] == "REPEAT"):
            for i in range(int(line[7:])):
                # repeat the last command
                self.parseLine(previousLine)
                time.sleep(float(self.defaultDelay)/1000)
        else:
            self.parseLine(line)
            previousLine = line
        time.sleep(float(self.defaultDelay)/1000)


if __name__ == "__main__":
    # example:
    picoducky = PicoDucky()
    picoducky.runScript("LED")

    picoducky.runScript("DELAY 3000")
    picoducky.runScript("GUI r")
    picoducky.runScript("DELAY 200")
    # Rick Astley - Never Gonna Give You Up (Official Music Video)
    picoducky.runScript("STRING https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    picoducky.runScript("ENTER")
    picoducky.runScript("DELAY 10000")
    picoducky.runScript("STRING f")
    
    picoducky.runScript("LED")

