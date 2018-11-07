#!/usr/bin/env python3

import curses
import smbus
import time

bus = smbus.SMBus(1)
addr = 0x40
start = 312
sleep_time = 0.05


class Point:
    def __init__(self, pan, tilt):
        self.pan = pan
        self.tilt = tilt

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

def do_point(p):
    set_pan(p.pan)
    set_tilt(p.tilt)
    time.sleep(sleep_time)

def run_square(p1, p3):
    p2 = Point(p1.pan, p3.tilt)
    p4 = Point(p3.pan, p1.tilt)
    while True:
        do_point(p1)
        do_point(p2)
        do_point(p3)
        do_point(p4)


def runner(win):
    pan = start
    tilt = start
    init_gimbal(start)
    last_key = None
    add_amnt = 1
    p1 = None
    p2 = None

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
        elif key == 49:
            p1 = Point(pan, tilt)
            win.addstr("Set Point 1: {}, {}".format(pan, tilt))
        elif key == 50:
            p2 = Point(pan, tilt)
            win.addstr("Set Point 2: {}, {}".format(pan, tilt))
        elif key == 115:
            run_square(p1, p2)
        else:
            win.addstr("key was {}".format(key))


def main():
    curses.wrapper(runner)

if __name__ == '__main__':
    main()
