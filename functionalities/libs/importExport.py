import json
import csv
import numpy as np
import os, glob

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)

def loadCSV(path):

    with open(path) as csv_file:

        csv_reader = csv.reader(csv_file)

        NLine = 0
        f = {}
        header = []

        for line in csv_reader:
            if NLine == 0:
                header = line[0].split(';')
                for i in range(0, len(header)):
                    f[header[i]] = []
            else:
                temp = line[0].split(';')
                for i in range(0, len(header)):
                    f[header[i]].append(temp[i])

            NLine =+ 1

        return f

def loadJson(path: str):
    try:
        with open(path) as jsonFile:
            data = json.loads(jsonFile.read())

        return data

    except Exception as e:
        print("Exception {}: {} was raised!".format(type(e), e))


def saveJson(data: dict, path: str):

    keys = list(data.keys())

    dataOut = {}

    for i in range(0, len(keys)):
        dataOut[keys[i]] = data[keys[i]]

    with open(path, 'w') as outfile:
        json.dump(dataOut, outfile, indent=4, sort_keys=True, cls=NumpyArrayEncoder)

def getFiles(dirPath, fileType):
    fileList = []
    dirTemp = os.getcwd()

    os.chdir(dirPath)
    for file in glob.glob('*.' + fileType):
        fileList.append(file)
    os.chdir(dirTemp)

    return fileList