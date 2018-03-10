import time
import irsdk
import iDDUhelper
import pygame
import threading

class IRClass:
    ir = irsdk.IRSDK()

class IRUpdate(IRClass):
    def __init__(self, update_list, init_data):
        self.update_list = update_list
        # self.ir = irsdk.IRSDK()
        self.data = {}

        self.data['clockValue'] = time.strftime("%H:%M:%S", time.localtime())
        self.data['clock'] = pygame.time.Clock()

        for i in range(0, len(update_list)):
            self.data.update({update_list[i]: init_data[update_list[i]]})

        self.data['startUp'] = False

    def update(self):

        self.data['clockValue'] = time.strftime("%H:%M:%S", time.localtime())
        self.data['clock'] = pygame.time.Clock()

        if self.ir.startup():
            self.data.update(iDDUhelper.getData(self.ir, self.update_list))
            self.data['startUp'] = True
        else:
            self.data['startUp'] = False


        return self.data

    def getSessionInfo(self):
        self.data['SessionInfo'] = self.ir['SessionInfo']
        return self.data

    def getDriverInfo(self):
        self.data['DriverInfo'] = self.ir['DriverInfo']
        return self.data
