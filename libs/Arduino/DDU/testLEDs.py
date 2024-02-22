import serial
import struct
import time

ser = serial.Serial('COM15', 9600, timeout=1)

print('===================')
print('INIT')

ser.write(struct.pack('>BBBBBBB', 0,0,0,0,0,1,0))
time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

print('===================')
print('RPM')

for i in range(0,9):
    ser.write(struct.pack('>bbbbbbb', i,0,0,0,0,0,0))
    time.sleep(0.33)

time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

print('===================')
print('FL')

for i in range(0,5):
    ser.write(struct.pack('>bbbbbbb', 0,i,0,0,0,0,0))
    time.sleep(0.33)

time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

print('===================')
print('FR')

for i in range(0,5):
    ser.write(struct.pack('>bbbbbbb', 0,0,i,0,0,0,0))
    time.sleep(0.33)

time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

print('===================')
print('RL')

for i in range(0,5):
    ser.write(struct.pack('>bbbbbbb', 0,0,0,i,0,0,0))
    time.sleep(0.33)

time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

print('===================')
print('RR')

for i in range(0,5):
    ser.write(struct.pack('>bbbbbbb', 0,0,0,0,i,0,0))
    time.sleep(0.33)

time.sleep(1)
ser.write(struct.pack('>bbbbbbb', 0,0,0,0,0,0,0))

ser.close()


