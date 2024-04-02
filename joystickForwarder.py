# HID\VID_30B7
# PID_1001

from cython_hidapi import hid
import pyvjoy

VID = 12471 # 30B7 
HID = 4097 # 1001

h = hid.device()
h.open(VID, HID)
h.set_nonblocking(0)

vjoy = pyvjoy.VJoyDevice(2)


def valueFromRaw(a, b):
    # left shift 8-bit number by 4 bits
    b_shifted = b << 8

    # compose the two numbers using bitwise OR
    result = b_shifted | a
    
    return result


while True:
    temp = h.read(8)

    # Throttle 1-2 [255 15]
    Throttle = valueFromRaw(temp[1], temp[2])
    # Brake 3 - 4 [255 15]
    Brake = valueFromRaw(temp[3], temp[4])
    # Clutch 5 - 6 [255 15]
    Clutch = valueFromRaw(temp[5], temp[6])

    vjoy.set_axis(48, int(Throttle*8))

h.close()