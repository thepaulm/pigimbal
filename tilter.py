#!/usr/bin/env python3

import curses
import smbus
import time

bus = smbus.SMBus(1)
addr = 0x40
start = 312

def scale(x, in_min, in_max, out_min, out_max):
    return (x - in_min)*(out_max - out_min)/(in_max - in_min) + out_min

def init_gimbal(start):
    ## enable the PC9685 and enable autoincrement

    bus.write_byte_data(addr, 0, 0x20) # enable the chip
    time.sleep(.1)
    bus.write_byte_data(addr, 0, 0x10) # enable Prescale change as noted in the datasheet
    time.sleep(.1) # delay for reset
    bus.write_byte_data(addr, 0xfe, 0x79) #changes the Prescale register value for 50 Hz, using the equation in the datasheet
    time.sleep(.1)
    bus.write_byte_data(addr, 0, 0x20) # enables the chip

    time.sleep(.1)

    bus.write_word_data(addr, 0x06, 0) # chl 0 start time = 0us
    bus.write_word_data(addr, 0x08, start) # chl 0 end time = 1.5ms

    bus.write_word_data(addr, 0x0a, 0) # chl 1 start time = 0us
    bus.write_word_data(addr, 0x0c, start) # chl 1 end time = 1.5ms

def set_tilt(setting):
    bus.write_word_data(addr, 0x0c, setting) # chl 1 end time = 1.5ms

def set_pan(setting):
    bus.write_word_data(addr, 0x08, setting) # chl 0 end time = 1.5ms

def runner(win):
    pan = start
    tilt = start
    init_gimbal(start)
    last_key = None
    add_amnt = 1

    curses.cbreak()
    win.clear()
    while True:
        key = win.getch()
        win.clear()
        if key == last_key:
            add_amnt += 1
        else:
            add_amnt = 1
        last_key = key
        if key == curses.KEY_UP:
            tilt -= add_amnt
            win.addstr("^")
            set_tilt(tilt)
        elif key == curses.KEY_DOWN:
            tilt += add_amnt
            win.addstr("V")
            set_tilt(tilt)
        elif key == curses.KEY_LEFT:
            pan += add_amnt
            win.addstr("<")
            set_pan(pan)
        elif key == curses.KEY_RIGHT:
            pan -= add_amnt
            win.addstr(">")
            set_pan(pan)

def main():
    curses.wrapper(runner)

if __name__ == '__main__':
    main()
