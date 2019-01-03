from datetime import datetime


def getF007():
    '''
    Formats the date/time and returns it in ISO8583 - Field 007 format
    '''
    return datetime.now().strftime(("%m%d%H%M%S"))


def getTMURL():
    '''
    Returns the TM URL
    '''
    url = "http://127.0.0.1:15000/V001/01/transaction"
    
    return url


def getKVPString(kvpobj):
    '''
    Parses the given object and forms the Key Value Pair String
    '''
    data = ""

    for key in kvpobj:
        data = data+str(len(key)).rjust(3, '0')+key
        data = data+str(len(kvpobj.get(key))).rjust(5, '0')+kvpobj.get(key)

    return data


def getKVPObject(kvpstring):
    '''
    Parses the given string and forms the Key Value Pair Object
    '''
    kvpobj = {}

    datalen = len(kvpstring)
    dlen = 0
    startpos = 0

    while startpos < datalen:
        dlen = 3
        key_len = int(kvpstring[startpos:startpos + dlen])
        startpos = startpos + dlen
        dlen = key_len
        key = kvpstring[startpos:startpos + dlen]
        startpos = startpos + dlen
        dlen = 5
        value_len = int(kvpstring[startpos:startpos + dlen])
        startpos = startpos + dlen
        dlen = value_len
        value = kvpstring[startpos:startpos + dlen]
        startpos = startpos + dlen

        kvpobj[key] = value

    return kvpobj
