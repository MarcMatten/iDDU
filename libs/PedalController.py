import time
from libs.IDDU import IDDUThread

class PedalControllerThread(IDDUThread):
    def __init__(self, rate):
        IDDUThread.__init__(self, rate)

    def run(self):
        while self.running:
            # execute this loop while iRacing is running
            while self.db.startUp:

                self.tic() 
                # read pedal value
                pedalsRaw = self.Pedals.h.read(8)
                # Throttle 1-2 [255 15]
                rThrottleRead = valueFromRaw(pedalsRaw[1], pedalsRaw[2])
                # Brake 3 - 4 [255 15]
                # rBrakeRead = valueFromRaw(pedalsRaw[3], pedalsRaw[4])
                # Clutch 5 - 6 [255 15]
                rClutchRead = valueFromRaw(pedalsRaw[5], pedalsRaw[6])
                if self.db.IsOnTrack:
                    if self.db.BForceClutch:
                        self.vjoy.set_axis(49, 4096)
                    else:
                        self.vjoy.set_axis(49, int(rClutchRead))
                    
                    if self.db.BForceLift:
                        self.vjoy.set_axis(48, 0) 
                    else:
                        self.vjoy.set_axis(48, int(rThrottleRead)) 
                    
                self.db.rThrottleRead = rThrottleRead/4096
                self.db.rClutchRead = rClutchRead/4096
                    
                self.toc()
                # time.sleep(self.rate)
            
            time.sleep(1)
        
        self.serial.close()


def valueFromRaw(a, b):
    # left shift 8-bit number by 4 bits
    b_shifted = b << 8

    # compose the two numbers using bitwise OR
    result = b_shifted | a
    
    return result