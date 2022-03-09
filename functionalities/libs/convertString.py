import numpy as np


def convertTimeMMSSsss(sec):
    if type(sec) is int or type(sec) is float or type(sec).__module__ == np.__name__:
        if sec < 0:
            sign = '-'
            sec = -sec
        else:
            sign = ''

        m, s = divmod(sec, 60)

        if m == 0:
            return sign + '{0:.3f}'.format(np.round(s-0.0005, 3))
        else:
            if s < 10:
                return sign + str(int(m)) + ':' + '0' + '{0:.3f}'.format(np.round(s-0.0005, 3))
            else:
                return sign + str(int(m)) + ':' + '{0:.3f}'.format(np.round(s-0.0005, 3))
    else:
        return '00:00,000'


def convertDelta(sec):
    if type(sec) is int or type(sec) is float or type(sec).__module__ == np.__name__:
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
    if type(sec) is int or type(sec) is float or type(sec).__module__ == np.__name__:
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
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        return '{0:.0f}'.format(np.round(x, 0))
    else:
        if type(x) is bool:
            return str(x)
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


def roundedStr2(x, BPlus=False):
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        if BPlus:
            if x > 0:
                return '+{0:.2f}'.format(np.round(x, 2))
        return '{0:.2f}'.format(np.round(x, 2))
    return "-"


def roundedStr3(x):
    if type(x) is int or type(x) is float or type(x).__module__ == np.__name__:
        return '{0:.3f}'.format(np.round(x, 3))
    else:
        return '-'

