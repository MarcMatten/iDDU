import threading
import irsdk
import pygame
import pyvjoy
import time
import ctypes
import os
from libs.MyLogger import MyLogger
from cython_hidapi import hid
import numpy as np

import serial
import struct

ctypes.windll.kernel32.SetDllDirectoryW(None)

state = [0, 0, 0, 0]


class JoystickUpdater(threading.Thread):

    running = False

    def __init__(self, h,  *args, **kwargs):
        super(JoystickUpdater, self).__init__(*args, **kwargs)
        threading.Thread.__init__(self)
        self.h = h
        self.running = True

    def run(self):
        global state
        while self.running:
            temp = self.h.read(64)
            state = temp[1:4]

        self.h.close()


class Joystick:
    NButton = 24

    def __init__(self):
        self.vid = 0
        self.pid = 0
        self.oldState = None
        self.ButtonStates = np.array([0]*self.NButton)
        self.BButtonReleased = np.array([0]*self.NButton)
        self.BButtonPressed = np.array([0]*self.NButton)

        # self.serial = serial.Serial('COM8', 9600, timeout=1)
        #
        # msg = struct.pack('>bbbbbbb', 0, 0, 0, 0, 0, 1, 0)
        # self.serial.write(msg)

        self.h = hid.device()


    def connect(self, vid, pid):
        self.vid = vid
        self.pid = pid
        self.h.open(self.vid, self.pid)
        self.h.set_nonblocking(0)

    def update(self):
        global state
        oldState = self.ButtonStates
        self.ButtonStates = np.array([0]*self.NButton)

        for i in range(len(state)):
            x = state[i]
            for k in range(0, 8):
                n = i*8 + k
                if x & np.power(2, k):
                    self.ButtonStates[n] = 1

        self.BButtonReleased = np.clip(oldState - self.ButtonStates, 0, 1)
        self.BButtonPressed = np.clip(self.ButtonStates - oldState, 0, 1)

    def isPressed(self, NButton:int):
        return self.ButtonStates[NButton]

    def ButtonPressedEvent(self, NButton:int):
        if self.BButtonPressed[NButton]:
            self.BButtonPressed[NButton] = 0
            return 1
        else:
            return 0

    def ButtonReleasedEvent(self, NButton: int):
        if self.BButtonReleased[NButton]:
            self.BButtonReleased[NButton] = 0
            return 1
        else:
            return 0

    def close(self):
        self.h.close()
        self.serial.close()

    def Event(self):
        if any(self.BButtonPressed) or any(self.BButtonReleased):
            return True
        else:
            return False


class IDDUItem:
    db = 0

    pygame = pygame
    pygame.init()

    myJoystick = None
    MarcsJoystick = None
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

    vid = 9025
    pid = 32822

    J = Joystick()
    J.connect(vid, pid)

    ju = JoystickUpdater(J.h)
    ju.start()

    MarcsJoystick = J

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
    
    def stopJU(self):
        self.ju.running = False




class IDDUThread(IDDUItem, threading.Thread):
    tStart = 0
    tMin = 1000
    tMax = 0
    tAvg = 0
    NCalls = np.uint64(0)
    running = False
    
    def __init__(self, rate, *args, **kwargs):
        IDDUItem.__init__(self)
        threading.Thread.__init__(self)
        super(IDDUThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.rate = rate
        self.running = True

    def tic(self):
        self.tStart = time.perf_counter()
        self.NCalls = np.uint64(self.NCalls + 1)
    
    def toc(self):
        tExec = time.perf_counter() - self.tStart
        self.tMin = np.min([self.tMin, tExec])
        self.tMax = np.max([self.tMax, tExec])
        self.tAvg = (self.tAvg * (self.NCalls-1) + tExec) / (self.NCalls)
        
    def stop(self):
        self.running = False
        self.logger.info('{} - Avg: {} | Min: {} | Max: {}'.format(type(self).__name__, np.round(self.tAvg, 6), np.round(self.tMin, 6), np.round(self.tMax, 6)))
