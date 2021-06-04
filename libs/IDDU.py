import threading
import irsdk
import pygame
import pyvjoy
import time
import ctypes

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

    def __init__(self):
        pass

    @staticmethod
    def setDB(rtdb):
        IDDUItem.db = rtdb

    def getJoystickList(self):
        pygame.joystick.init()

        print(self.db.timeStr + ': ' + str(pygame.joystick.get_count()) + ' joysticks detected:')

        for i in range(pygame.joystick.get_count()):
            self.joystickList.append(pygame.joystick.Joystick(i).get_name())
            print(self.db.timeStr + ':\tJoystick ', i, ': ', pygame.joystick.Joystick(i).get_name())



    def initJoystick(self, name):
        # self.getJoystickList()
        desiredJoystick = 9999

        for i in range(len(self.joystickList)):
            if pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        for i in range(pygame.joystick.get_count()):
            print(self.db.timeStr + ':\tJoystick ', i, ': ', pygame.joystick.Joystick(i).get_name())
            if pygame.joystick.Joystick(i).get_name() == name:
                desiredJoystick = i

        if not desiredJoystick == 9999:
            print(self.db.timeStr + ':\tConnecting to', pygame.joystick.Joystick(desiredJoystick).get_name())
            IDDUItem.myJoystick = pygame.joystick.Joystick(desiredJoystick)
            IDDUItem.myJoystick.get_name()
            IDDUItem.myJoystick.init()
            print(self.db.timeStr + ':\tSuccessfully connected to', pygame.joystick.Joystick(desiredJoystick).get_name(), '!')
        else:
            print(self.db.timeStr + ':\tFANATEC ClubSport Wheel Base not found!')

    def pressButton(self, ID, t):
        self.vjoy.set_button(ID, 1)
        time.sleep(t)
        self.vjoy.set_button(ID, 0)

class IDDUThread(IDDUItem, threading.Thread):
    def __init__(self, rate):
        IDDUItem.__init__(self)
        threading.Thread.__init__(self)
        self.rate = rate
