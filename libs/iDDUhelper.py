import numpy as np


def convertTimeMMSSsss(sec):
    if type(sec) is int or type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = ''

        m, s = divmod(sec, 60)

        if m == 0:
            return sign + '{0:.3f}'.format(np.round(s, 3))
        else:
            if s < 10:
                return sign + str(int(m)) + ':' + '0' + '{0:.3f}'.format(np.round(s, 3))
            else:
                return sign + str(int(m)) + ':' + '{0:.3f}'.format(np.round(s, 3))
    else:
        return '00:00,000'


def convertDelta(sec):
    if type(sec) is int or type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = '+'

        m, s = divmod(sec, 60)

        if m == 0:
            return sign + '{0:.2f}'.format(np.round(s, 2))
        else:
            if s < 10:
                return sign + str(int(m)) + ':' + '0' + '{0:.2f}'.format(np.round(s, 2))
            else:
                return sign + str(int(m)) + ':' + '{0:.2f}'.format(np.round(s, 2))
    else:
        return '+00:00,00'


def convertTimeHHMMSS(sec):
    if type(sec) is int or type(sec) is float:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = ''

        m, s = divmod(np.round(sec), 60)
        h, m = divmod(m, 60)

        if m < 10:
            if s < 10:
                return sign + str(int(h)) + ':' + '0' + str(int(m)) + ':' + '0' + '{0:.0f}'.format(np.round(s, 0))

            else:
                return sign + str(int(h)) + ':' + '0' + str(int(m)) + ':' + '{0:.0f}'.format(np.round(s, 0))
        else:
            if s < 10:
                return sign + str(int(h)) + ':' + str(int(m)) + ':' + '0' + '{0:.0f}'.format(np.round(s, 0))
            else:
                return sign + str(int(h)) + ':' + str(int(m)) + ':' + '{0:.0f}'.format(np.round(s, 0))
    else:
        return '00:00:00'


def roundedStr0(x):
    if type(x) is int or type(x) is float:
        return '{0:.0f}'.format(np.round(x, 0))
    else:
        return "-"


def roundedStr1(x, n):
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        if n <= 2:
            if np.round(x) >= 10:
                return '{0:.0f}'.format(np.round(x, 1))
            else:
                return '{0:.1f}'.format(np.round(x, 1))
        elif n == 3:
            if np.round(x) >= 100:
                return '{0:.0f}'.format(np.round(x, 1))
            else:
                return '{0:.1f}'.format(np.round(x, 1))
        else:
            return '{0:.1f}'.format(np.round(x, 1))
    else:
        return "-"


def roundedStr2(x):
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        return '{0:.2f}'.format(np.round(x, 2))
    else:
        return "-"


def roundedStr3(x):
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        return '{0:.3f}'.format(np.round(x, 3))
    else:
        return '-'


def getData(ir, L):
    data = {}

    for i in range(0, len(L)):
        data.update({L[i]: ir[L[i]]})

    return data


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



