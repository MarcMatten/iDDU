import time
from libs.IDDU import IDDUThread
import serial
import serial.tools.list_ports
import struct

class SteeringWheelComsThread(IDDUThread):
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)
        # connecting to Steering Wheel Arduino
        self.PortList = serial.tools.list_ports.comports()
        self.BPortFound = False
        self.BArduinoConnected = False
        self.COMPort = None
        self.serial = None
        self.rBitePointSent = 0
        self.tThumbWheelErrorL = 0
        self.tThumbWheelErrorR = 0

        for i in range(0, len(self.PortList)):
            if self.PortList[i].device == self.db.config['USBDevices']['SteeringWheel']['COM']:
                self.COMPort = self.PortList[i].device
                self.BPortFound = True

        if self.BPortFound:
            try:
                self.logger.info('{} found! Connecting to {}'.format(self.db.config['USBDevices']['SteeringWheel']['Name'], self.db.config['USBDevices']['SteeringWheel']['COM']))
                self.serial = serial.Serial(self.COMPort, 9600, timeout=1)
                self.rBitePointSent = self.db.config['rBitePoint']/100
                self.serial.write(struct.pack('<f', self.rBitePointSent))

                msg = self.serial.readline()
                if msg:
                    if len(msg) == 1:
                        data = struct.unpack('<b', msg)[0]
                    elif len(msg) == 4:
                        data = struct.unpack('<f', msg)[0]
                    else:
                        data = None

                    if not round(self.rBitePointSent, 3) == round(data, 3):
                        self.logger.error('Could not set Clutch Bite Point!')

                self.BArduinoConnected = True
                self.logger.info('Connection to {} established on {}!'.format(self.db.config['USBDevices']['SteeringWheel']['Name'], self.db.config['USBDevices']['SteeringWheel']['COM']))
                self.BPortFound = True

            except:
                self.BArduinoConnected = False
                self.logger.error('Could not connect to {} on {}!'.format(self.db.config['USBDevices']['SteeringWheel']['Name'], self.db.config['USBDevices']['SteeringWheel']['COM']))

        else:
            self.BArduinoConnected = False
            self.logger.error('Could not connect to {} on {}!'.format(self.db.config['USBDevices']['SteeringWheel']['Name'], self.db.config['USBDevices']['SteeringWheel']['COM']))

    def run(self):
        while self.running:
            # execute this loop while iRacing is running
            while self.db.startUp:

                self.tic() 

                # execute this loop while player is on track
                if self.BArduinoConnected and self.db.IsOnTrack:  
                                     
                    if not self.rBitePointSent == self.db.config['rBitePoint'] / 100:
                        self.rBitePointSent = self.db.config['rBitePoint'] / 100
                        self.serial.write(struct.pack('<f', self.rBitePointSent))
                        self.logger.info('Setting Clutch Bite Point: {}'.format(self.rBitePointSent))

                    msg = self.serial.readline()
                    if msg:
                        try:
                            if len(msg) == 1:
                                data = struct.unpack('<b', msg)[0]
                                if data == 1:
                                    self.logger.info('Entering Dual Clutch Paddle Mode')
                                elif data == 0:                                    
                                    self.logger.info('Leaving Dual Clutch Paddle Mode')
                            elif len(msg) == 4:
                                data = struct.unpack('<f', msg)[0]
                                if not round(self.rBitePointSent, 3) == round(data, 3):
                                    self.logger.error('Could not set Clutch Bite Point!')
                                else:
                                    self.logger.info('Set Clutch Bite Point: {}'.format(round(data, 3)))
                            else:
                                data = msg.decode().split('\r')[0]
                                if data.startswith('TW'):
                                    if data[3] == 'L':
                                        self.db.BThumbWheelErrorL = True
                                        self.tThumbWheelErrorL = self.db.SessionTime
                                        self.logger.error('Thumb Wheel Error Left! {} values read.'.format(data[4:]))
                                    if data[3] == 'R':
                                        self.db.BThumbWheelErrorR = True
                                        self.tThumbWheelErrorR = self.db.SessionTime
                                        self.logger.error('Thumb Wheel Error Right! {} values read.'.format(data[4:]))
                                    if data == 'TWOK':
                                        self.db.BThumbWheelErrorL = False
                                        self.db.BThumbWheelErrorR = False
                                        self.logger.info('Thumb Wheel okay again')
                                    if data == 'TWOFF':
                                        self.db.BThumbWheelErrorL = True
                                        self.db.BThumbWheelErrorR = True
                                        self.db.BThumbWheelActive = False
                                        self.logger.error('Thumb Wheels deactivated because of too many errors!')
                                else:
                                    print(msg)
                                    data = None
                        except:
                            self.logger.error('Could not decode message: {}'.format(msg))
                            data = None
                    else:
                        data = None

                    if self.db.BThumbWheelErrorL and self.db.SessionTime - self.tThumbWheelErrorL > 10:
                        self.db.BThumbWheelErrorL = False
                    if self.db.BThumbWheelErrorR and self.db.SessionTime - self.tThumbWheelErrorR > 10:
                        self.db.BThumbWheelErrorR = False

                    if data == 1 and not self.db.BSteeringWheelStartMode:
                        self.db.BSteeringWheelStartMode = True
                        self.logger.info('Start Mode ON')
                    elif data == 0 and self.db.BSteeringWheelStartMode:
                        self.db.BSteeringWheelStartMode = False
                        self.logger.info('Start Mode OFF')#
                    
                self.toc()

                # time.sleep(0.2)
            
            time.sleep(1)
        
        self.serial.close()