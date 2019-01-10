from datetime import datetime
import pyodbc
import posconf


def getconnection():
    '''-------------------------------------------------------------------------
    Gets the database connection. Required pyodbc, unixodbc & freetds

    :return:    Database connection object
    -------------------------------------------------------------------------'''
    con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (
        posconf.dsn, posconf.user, posconf.password, posconf.dbname)
    cnxn = pyodbc.connect(con_string)
    return cnxn


def getF007():
    '''-------------------------------------------------------------------------
    Formats the date/time and returns it in ISO8583 - Field 007 format

    :return:    Date/Time in the format MMDDhhmmss
    -------------------------------------------------------------------------'''
    return datetime.now().strftime(("%m%d%H%M%S"))


def getKVPString(kvpobj):
    '''-------------------------------------------------------------------------
    Parses the given object and forms the Key Value Pair String

    :return:    Key/Value pair string
    -------------------------------------------------------------------------'''
    data = ""

    for key in kvpobj:
        data = data+str(len(key)).rjust(3, '0')+key
        data = data+str(len(kvpobj.get(key))).rjust(5, '0')+kvpobj.get(key)

    return data


def getKVPObject(kvpstring):
    '''-------------------------------------------------------------------------
    Parses the given string and forms the Key Value Pair Object

    :return:    Dictionary object
    -------------------------------------------------------------------------'''
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