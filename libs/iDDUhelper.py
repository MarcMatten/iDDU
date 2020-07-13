def getData(ir, L):  # TODO: is this used anywhere?
    data = {}

    for i in range(0, len(L)):
        data.update({L[i]: ir[L[i]]})

    return data