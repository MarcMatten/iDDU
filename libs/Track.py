import csv
from libs import iDDUhelper
import matplotlib.pyplot as plt
import json
import numpy as np


class Track:
    def __init__(self, name):
        self.name = name
        self.sTrack = 0
        self.x = []
        self.y = []
        self.dist = []
        self.a = 0
        self.aNorth = 0
        self.ds = 10
        self.map = []
        self.SFLine = [[0, 0], [0, 0], [0, 0]]

    def createTrack(self, x, y, dist, aNorth, sTrack):
        self.x = x
        self.y = -y
        self.dist = dist
        self.sTrack = sTrack
        self.aNorth = aNorth
        self.a = iDDUhelper.angleVertical(self.x[3] - self.x[0], self.y[3] - self.y[0])

        self.scale()
        self.sample()
        self.createMap()

    def saveJson(self, *args):
        if len(args) == 1:
            filepath = args[0] + '/track/' + self.name + '.json'
        elif len(args) == 2:
            filepath = args[0] + '/' + args[1] + '.json'
        else:
            print('Invalid number if arguments. Max 2 arguments accepted!')
            return

        variables = list(self.__dict__.keys())
        variables.remove('map')

        data = {}

        for i in range(0, len(variables)):
            if type(self.__dict__[variables[i]]) == np.ndarray:
                data[variables[i]] = self.__dict__[variables[i]].tolist()
            else:
                data[variables[i]] = self.__dict__[variables[i]]

        with open(filepath, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


    def loadFromCSV(self, path):

        x = []
        y = []
        dist = []

        with open(path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                dist.append(float(line[0]))
                x.append(float(line[1]))
                y.append(float(line[2]))

        self.x = np.array(x)
        self.y = np.array(y)
        self.dist = np.array(dist)
        self.a = iDDUhelper.angleVertical(self.x[3] - self.x[0], self.y[3] - self.y[0])
        self.sTrack = len(self.dist)*self.ds

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

        self.x = x_temp * np.cos(a) + y_temp * np.sin(a)
        self.y = -x_temp * np.sin(a) + y_temp * np.cos(a)

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
        self.dist[0] = 0
        self.x = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.dist, self.x)
        self.y = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.dist, self.y)
        self.dist = np.interp(np.linspace(0, 100, int(self.sTrack / self.ds) + 1), self.dist, self.dist)
        self.createMap()

    def loadJson(self, path):
        with open(path) as jsonFile:
            data = json.loads(jsonFile.read())

        temp = list(data.items())
        for i in range(0, len(data)):
            self.__setattr__(temp[i][0], temp[i][1])

        self.createMap()

    def calcSFLine(self):

        a = self.a - np.pi/2
        x1 = 15 * np.cos(a) + 0 * np.sin(a)
        y1 = -15 * np.sin(a) + 0 * np.cos(a)

        x2 = 0 * np.cos(a) + 15 * np.sin(a)
        y2 = -0 * np.sin(a) + 15 * np.cos(a)

        x3 = 0 * np.cos(a) - 15 * np.sin(a)
        y3 = -0 * np.sin(a) - 15 * np.cos(a)

        self.SFLine = [[x1+self.x[0], y1+self.y[0]], [x2+self.x[0], y2+self.y[0]], [x3+self.x[0], y3+self.y[0]]]