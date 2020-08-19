import threading
import irsdk

class IDDUItem:
    db = 0

    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    orange = (255, 133, 13)
    grey = (141, 141, 141)
    black = (0, 0, 0)
    cyan = (0, 255, 255)

    ir = irsdk.IRSDK()

    def __init__(self):
        pass

    @staticmethod
    def setDB(rtdb):
        IDDUItem.db = rtdb

class IDDUThread(IDDUItem, threading.Thread):
    def __init__(self, rate):
        IDDUItem.__init__(self)
        threading.Thread.__init__(self)
        self.rate = rate
