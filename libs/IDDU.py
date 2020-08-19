import threading

class IDDUItem:
    db = 0

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


# class IDDU(IDDUThread):
#     mapDDU = {}
#     mapIR = {}
#     NCurrentMapDDU = 0
#     NCurrentMapIR = 0
#     NMultiState = 0
#     tMultiChange = 0
#
#     def __init__(self, RTDB, rate):
#         IDDUThread.__init__(self, rate)
#         IDDUItem.setDB(RTDB)
