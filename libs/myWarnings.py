import time


class AlertManager:
    version = 18

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
    alarms = []
    
    def __init__(self):
        pass

    def initAlarms(self):
        
        print(self.version)

        self.PITLIMITERACTIVE = Alarm('PIT LIMITER', self.blue, self.white, 4, 92, 10000)
        self.WATERTEMP = Alarm('WATER TEMP HIGH', self.red, self.white, 4, 99, -1)
        self.FUELPRESSURE = Alarm('LOW FUEL PRESSURE', self.red, self.white, 4, 91, 20)
        self.OILPRESSURE = Alarm('LOW OIL PRESSURE', self.red, self.white, 4, 86, 10000)
        
        self.ENGINESTALLED = Alarm('ENGINE STALLED', self.yellow, self.black, 4, 99, -1)
        self.FLASH = Alarm('FLASH', self.green, self.white, 5, 8)

        self.CROSSED = Alarm('CROSSED', self.white, self.black, 4, 9)
        self.RANDOMWARING = Alarm('RANDOM WAVING', self.white, self.black, 0, 8)
        self.DISQUALIFIED = Alarm('DISQUALIFIED', self.white, self.black, 0, 94)

        self.PITLIMITEROFF = Alarm('PIT LIMITER OFF', self.red, self.white, 4, 99, -1)

        self.THUMBWHEELERRORL = Alarm('THMBWHL ERROR Left', self.red, self.white, 4, 78)
        self.THUMBWHEELERRORR = Alarm('THMBWHL ERROR Right', self.red, self.white, 4, 18)
        self.LOADRACESETUP = Alarm('LOAD RACE SETUP!', self.yellow, self.black, 3, 18)

        self.TCOFF = Alarm('TC OFF', self.white, self.black, 10, 70, 7)

    def rasieAlert(self):

        self.tRaised = time.time()
               
        if not self.BActive and not self.BActive and not self.BSurpress:
            self.BActive = True

        if self in AlertManager.alarms:
            print('Alarm already raised!')
        else:
            AlertManager.alarms.append(self)

    def ignore(self):
        self.BIgnore = True

    def surpress(self):
        self.BSurpress = True
        self.tSurpress = time.time()

    def reset(self):
        self.BSurpress = False
        self.BIgnore = False
        self.tRaised = 0
        self.tSurpress = 0
        self.cancelAlert()

    def cancelAlert(self):
        idx = []

        for i in range(len(self.alarms)):
            if self.alarms[i].name == self.name:
                idx.append(i)

        for i in idx:
            AlertManager.alarms.pop(i)
            self.BActive = False

    def update(self):

        AlertManager.alarms = sorted(self.alarms, key=lambda d: d.priority, reverse=True)

        i = 0
        while i <len(self.alarms):
            if self.alarms[i].BSurpress:
                if time.time() - self.alarms[i].tSurpress > self.alarms[i].tSurpressDuration:
                    self.alarms[i].BSurpress = False
                    self.alarms[i].tSurpress = 0
        
            if self.alarms[i].tDuration:
                if self.alarms[i].tDuration == -1:
                    if self.alarms[i].tRaised:
                        self.alarms[i].tRaised = 0
                    else:
                        self.alarms[i].BActive = False
                        self.alarms[i].cancelAlert()
                        i = min(0,i-1)
                    return
                if time.time() - self.alarms[i].tRaised >= self.alarms[i].tDuration:
                    self.alarms[i].BActive = False
                    self.alarms[i].tRaised = 0
                    self.alarms[i].cancelAlert()
                    i = min(0,i-1)
            i += 1

    def display(self, n: int = 1):
        i = 0
        k = 0
        result = [None] * n
        while i < len(self.alarms) and k < n:
            if not (self.alarms[i].BIgnore or self.alarms[i].BSurpress) and self.alarms[i].BActive:
                print('{}: {} | {} s left ...'.format(self.alarms[i].name, self.alarms[i].priority, time.time() - self.alarms[i].tRaised - self.alarms[i].tDuration))
                result[k] = (self.alarms[i].name, self.alarms[i].labelcolour, self.alarms[i].textcolour, self.alarms[i].f)
                k += 1

            i += 1
        return result


class Alarm(AlertManager):

    BActive = False

    def __init__(self,
                 name: str,
                 labelcolour: tuple,
                 textcolour: tuple,
                 f: float = 0,
                 priority: int = 0,
                 tDuration:float = 0,               # how long to be active
                 tRaised:float = 0,                 # when it became active
                 tSurpress:float = 0,               # when it was surpressed
                 tSurpressDuration:float = 5,       # for how long to surpress
                 BIgnore: bool = False,             # ignore completely
                 BSurpress: bool = False):          # surpress

        AlertManager.__init__(self)
        self.name = name
        self.labelcolour = labelcolour
        self.textcolour = textcolour
        self.f = f
        self.priority = priority
        self.tDuration = tDuration
        self.tSurpressDuration = tSurpressDuration
        self.tRaised = tRaised
        self.tSurpress = tSurpress
        self.BIgnore = BIgnore
        self.BSurpress = BSurpress

    def active(self):
        print('Alarm: {}, Priotity {}'.format(self.name, self.priority))
