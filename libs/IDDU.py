import threading
import irsdk
import pygame
import pyvjoy
import time
import ctypes
import os
from libs.MyLogger import MyLogger

ctypes.windll.kernel32.SetDllDirectoryW(None)


class IDDUItem:
    db = 0

    pygame = pygame
    pygame.init()

    myJoystick = None
    joystickList = []

    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    orange = (255, 133, 13)
    grey = (141, 141, 141)
    black = (0, 0, 0)
    cyan = (0, 255, 255)
    purple = (255, 0, 255)
    GTE = (255, 88, 136)
    LMP1 = (255, 218, 89)
    LMP2 = (51, 206, 255)

    ir = irsdk.IRSDK()

    vjoy = pyvjoy.VJoyDevice(2)

    LogFilePath = os.path.abspath(os.path.join((os.getcwd()).split('iDDU')[0], 'iDDU', 'data', 'iDDU.log'))

    logger = MyLogger()

    def __init__(self):
        pass

    @staticmethod
    def setDB(rtdb):
        IDDUItem.db = rtdb

    def getJoystickList(self):
        pygame.joystick.init()

        self.logger.info(str(pygame.joystick.get_count()) + ' joysticks detected:')

        for i in range(pygame.joystick.get_count()):
            self.joystickList.append(pygame.joystick.Joystick(i).get_name())
            self.logger.info('Joystick {}: {}'. format(i, pygame.joystick.Joystick(i).get_name()))

    def initJoystick(self, name):
        desiredJoystick = None

        for i in range(len(self.joystickList)):
            if pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        for i in range(pygame.joystick.get_count()):
            if pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        self.logger.info('Attempting to connect to {}'.format(name))
        if desiredJoystick:
            IDDUItem.myJoystick = pygame.joystick.Joystick(desiredJoystick)
            IDDUItem.myJoystick.get_name()
            IDDUItem.myJoystick.init()
            self.logger.info('Successfully connected to {} !'.format(name))
        else:
            self.logger.error('{} not found!'.format(name))

    def pressButton(self, ID, t):
        self.vjoy.set_button(ID, 1)
        time.sleep(t)
        self.vjoy.set_button(ID, 0)


class IDDUThread(IDDUItem, threading.Thread):
    def __init__(self, rate):
        IDDUItem.__init__(self)
        threading.Thread.__init__(self)
        self.rate = rate
