import numpy as np
import scipy.signal
import scipy.optimize


def findIntersection(fun1, fun2, x0):
    return scipy.optimize.fsolve(lambda x: fun1(x) - fun2(x), x0)


def polyVal(x, *args):
    if isinstance(args[0], np.ndarray):
        c = args[0]
    else:
        c = args

    r = 0

    for i in range(0, len(c)):
        r += c[i] * np.power(x, i)

    return r


def smartAverageMax(x_in, tol):
    avg_raw = np.mean(x_in)
    if len(x_in) > 3:
        indices = np.where(x_in > (1 + tol) * avg_raw)
        x = x_in.copy()
        for i in range(0, len(indices[0])):
            x.__delitem__(indices[0][len(indices[0]) - i - 1])
        avg = np.mean(x)
        return avg
    else:
        return avg_raw


def smartAverageMinMax(x_in, tol):
    avg_raw = np.mean(x_in)
    if len(x_in) > 3:
        indices = np.where(x_in > (1 + tol) * avg_raw)
        x = x_in.copy()
        for i in range(0, len(indices[0])):
            x.__delitem__(indices[0][len(indices[0]) - i - 1])
        indices = np.where(x < (1 - tol) * avg_raw)
        for i in range(0, len(indices[0])):
            x.__delitem__(indices[0][len(indices[0]) - i - 1])
        avg = np.mean(x)
        return avg
    else:
        return avg_raw


def meanTol(x_in: list, tol: float):
    x_clean = [k for k in x_in if str(k) != 'nan']

    mean = np.mean(x_clean).item()
    if len(x_clean) < 3:
        return float(mean)
    else:
        x = np.array(x_clean)
        dev_abs = np.abs(x - mean)
        dev_rel = dev_abs / mean
        withintolerance = np.greater(tol, dev_rel).tolist()
        indices = [i for i, x in enumerate(withintolerance) if x]
        if len(indices) < 3:
            return float(mean)
        else:
            x_new = x[indices]
            meanWithinTol = np.mean(x_new).item()
            return float(meanWithinTol)


def maxList(L, value):
    if type(L) is list:
        CondBool = np.array(L) < value

        if type(CondBool) is not list:
            CondBool = [CondBool]

        indexes = [i for i, x in enumerate(CondBool) if x]

        for k in indexes:
            L[k] = value

        return L
    elif type(L) is int:
        return max(L, value)

def angleVertical(dx, dy):
    a = 0
    if dx == 0:
        if dy > 0:
            a = np.pi
        else:
            a = 0
    elif dx > 0:
        if dy > 0:
            a = -np.arctan(dx/dy) + np.pi
        elif dy < 0:
            a = -np.arctan(dx/dy)
        else:
            a = np.pi / 2
    elif dx < 0:
        if dy > 0:
            a = -np.arctan(dx/dy) + np.pi
        elif dy < 0:
            a = 2 * np.pi - np.arctan(dx/dy)
        else:
            a = np.pi * 1.5

    return a


def createTrack(x):
    dx = np.array(0)
    dy = np.array(0)

    dx = np.append(dx, np.cos(x['Yaw'][0:-1]) * x['vCarX'][0:-1] * x['dt'] - np.sin(x['Yaw'][0:-1]) * x['vCarY'][0:-1] * x['dt'])
    dy = np.append(dy, np.cos(x['Yaw'][0:-1]) * x['vCarY'][0:-1] * x['dt'] + np.sin(x['Yaw'][0:-1]) * x['vCarX'][0:-1] * x['dt'])

    tempx = np.cumsum(dx, dtype=float).tolist()
    tempy = np.cumsum(dy, dtype=float).tolist()

    xError = tempx[-1] - tempx[0]
    yError = tempy[-1] - tempy[0]

    tempdx = np.array(0)
    tempdy = np.array(0)

    tempdx = np.append(tempdx, dx[1:len(dx)] - xError / (len(dx) - 1))
    tempdy = np.append(tempdy, dy[1:len(dy)] - yError / (len(dy) - 1))

    x = np.cumsum(tempdx, dtype=float)
    y = np.cumsum(tempdy, dtype=float)

    x[-1] = 0
    y[-1] = 0

    return x, y


def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:]))


def strictly_decreasing(L):
    return all(x>y for x, y in zip(L, L[1:]))


def non_increasing(L):
    return all(x>=y for x, y in zip(L, L[1:]))


def non_decreasing(L):
    return all(x<=y for x, y in zip(L, L[1:]))


def monotonic(L):
    return non_increasing(L) or non_decreasing(L)


def makeMonotonic2D(xIn, yIn):
    d = np.diff(xIn)
    idx = [i+1 for i in range(len(d)) if d[i] <= 0]
    xOut = np.delete(xIn, idx)
    yOut = np.delete(yIn, idx)
    return xOut, yOut
