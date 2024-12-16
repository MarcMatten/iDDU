import csv
from libs.auxiliaries import importExport, maths
import matplotlib.pyplot as plt
import numpy as np
import time
from libs import IDDU


class Track:
    def __init__(self, name):
        self.name = name
        self.sTrack = 0
        self.x = []
        self.y = []
        self.LapDistPct = []
        self.a = 0
        self.aNorth = 0
        self.ds = 10
        self.map = []
        self.SFLine = [[0, 0], [0, 0], [0, 0]]
        self.tLap = {}
        self.LapDistPctPitIn = None
        self.LapDistPctPitOut = None
        self.LapDistPctPitDepart = None
        self.LapDistPctPitRemerged = None
        self.path = None

    def createTrack(self, x, y, LapDistPct, aNorth, sTrack):
        self.x = x
        self.y = -y
        self.LapDistPct = LapDistPct
        self.sTrack = sTrack
        self.aNorth = aNorth
        self.a = maths.angleVertical(self.x[3] - self.x[0], self.y[3] - self.y[0])

        self.scale()
        self.sample()
        self.createMap()

    def save(self, *args):
        if len(args) == 0:
            filepath = self.path
        elif len(args) == 1:
            filepath = args[0] + '/data/track/' + self.name + '.json'
        elif len(args) == 2:
            filepath = args[0] + '/' + args[1] + '.json'
        else:
            IDDU.IDDUItem.logger.error('Invalid number if arguments. Max 2 arguments accepted!')
            return

        # get list of track object properties
        variables = list(self.__dict__.keys())
        variables.remove('map')
        variables.remove('path')

        # create dict of track object properties
        data = {}

        for i in range(0, len(variables)):
            if type(self.__dict__[variables[i]]) == np.ndarray:
                data[variables[i]] = self.__dict__[variables[i]].tolist()
            else:
                data[variables[i]] = self.__dict__[variables[i]]

        importExport.saveJson(data, filepath)

        IDDU.IDDUItem.logger.info('Saved track ' + filepath)

    def loadFromCSV(self, path):  # TODO: no longer used, put this in a library

        x = []
        y = []
        LapDistPct = []

        with open(path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                LapDistPct.append(float(line[0]))
                x.append(float(line[1]))
                y.append(float(line[2]))

        self.x = np.array(x)
        self.y = np.array(y)
        self.LapDistPct = np.array(LapDistPct)
        self.a = maths.angleVertical(self.x[3] - self.x[0], self.y[3] - self.y[0])
        self.sTrack = len(self.LapDistPct)*self.ds

        self.sample()
        self.scale()
        self.createMap()

    def createMap(self):
        self.map = []
        for i in range(0, len(self.x)):
            self.map.append([float(self.x[i]), float(self.y[i])])

        self.calcSFLine()

    def rotate(self, a):
        x_temp = np.array(self.x) - 400
        y_temp = np.array(self.y) - 240

        self.x = x_temp * np.cos(-a) + y_temp * np.sin(-a)
        self.y = -x_temp * np.sin(-a) + y_temp * np.cos(-a)

        self.a = self.a + a

        self.scale()

    def scale(self):
        width = np.max(np.array(self.x)) - np.min(np.array(self.x))
        height = np.max(np.array(self.y)) - np.min(np.array(self.y))

        scalingFactor = min(400 / height, 720 / width)

        self.x = 400 + (scalingFactor * self.x - (min(scalingFactor * self.x) + max(scalingFactor * self.x)) / 2)
        self.y = (240 + (scalingFactor * self.y - (min(scalingFactor * self.y) + max(scalingFactor * self.y)) / 2))

        self.createMap()

    def plot(self):
        plt.plot(self.x, self.y)
        plt.xlim(0, 800)
        plt.ylim(0, 480)
        plt.title(self.name)
        plt.show()

    def sample(self):
        self.LapDistPct[0] = 0
        self.x = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.LapDistPct, self.x)
        self.y = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.LapDistPct, self.y)
        self.LapDistPct = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.LapDistPct, self.LapDistPct)
        self.createMap()

    def load(self, path):
        # TODO: error management
        IDDU.IDDUItem.logger.info('Loading track ' + path)

        data = importExport.loadJson(path)
        
        self.path = path

        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])

        IDDU.IDDUItem.logger.info('Track loaded, creating map.')

        self.createMap()
        
        IDDU.IDDUItem.logger.info('Loaded track {}'.format(path))

    def calcSFLine(self):

        a = -self.a + np.pi/2
        x1 = 15 * np.cos(a) + 0 * np.sin(a)
        y1 = -15 * np.sin(a) + 0 * np.cos(a)

        x2 = 0 * np.cos(a) + 15 * np.sin(a)
        y2 = -0 * np.sin(a) + 15 * np.cos(a)

        x3 = 0 * np.cos(a) - 15 * np.sin(a)
        y3 = -0 * np.sin(a) - 15 * np.cos(a)

        self.SFLine = [[x1+self.x[0], y1+self.y[0]], [x2+self.x[0], y2+self.y[0]], [x3+self.x[0], y3+self.y[0]]]

    def setLapTime(self, car, tLap):
        if car in self.tLap:
            if self.tLap[car] < tLap:
                self.tLap[car] = tLap
        else:
            self.tLap[car] = tLap

    def setPitIn(self, LapDistPctPitIn):
        if not self.LapDistPctPitIn:
            self.LapDistPctPitIn = LapDistPctPitIn
            self.save()

    def setPitOut(self, LapDistPctPitOut):
        if not self.LapDistPctPitOut:
            self.LapDistPctPitOut = LapDistPctPitOut
            self.save()

    def setPitDepart(self, LapDistPctPitDepart):
        if not self.LapDistPctPitDepart:
            self.LapDistPctPitDepart = LapDistPctPitDepart
            self.save()

    def setPitRemerged(self, LapDistPctPitRemerged):
        if not self.LapDistPctPitRemerged:
            self.LapDistPctPitRemerged = LapDistPctPitRemerged
            self.save()