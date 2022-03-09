import serial
from pygame import *
import struct
import serial.tools.list_ports as ListPorts

PortList = ListPorts.comports()  # get list of all ports

for i in range(0, len(PortList)):  # run for loop to test every COM port
    ser = serial.Serial(PortList[i].device, 9600, timeout=1, writeTimeout=0)  # open serial
    time.wait(2000)  # wait for connection to establish
    ser.write(struct.pack('>B', 123))  # send ID
    msg = ser.read()  # wait for ID sent back

    # if ID recieved, check if it's  matching
    if msg:
        if msg == b'A':  # if mathcing, terminat for loop
            print('Successfully connected to', PortList[i].description, 'on', PortList[i].device)
            break
    ser.close()
