import connexion
import simplejson as json
import utilities
import requests

from flask import abort, jsonify, request


def getterminfo(mid, tid, bankcode, apikey):
    '''-------------------------------------------------------------------------
    This method fetches the data from the SQL tables

    :return:    Terminal Info Object
    -------------------------------------------------------------------------'''
    terminfo = {}

    terminfo["found"] = True
    terminfo["acq_node_name"] = "ADEMO"
    terminfo["bank_name"] = "DEMOPARTICIPANT"
    terminfo["pdc"] = "51010151414C101"

    return terminfo


def sale(salerequest):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the Sale transaction.

    :return:    Sale response body
    -------------------------------------------------------------------------'''
    apikey = request.headers.get("apikey")
    kvp = {}

    # Fetch Terminal Info
    terminfo = getterminfo(salerequest.get("mid"), salerequest.get(
        "tid"), salerequest.get("bankcode"), apikey)

    if not terminfo["found"]:
        return abort(422)

    msg = {}
    msg["MsgType"] = "0200"

    if salerequest.get("amount_addl"):
        cashamt = int(salerequest.get("amount_addl"))
        if cashamt > 0:
            msg["F003"] = "09" + salerequest.get("fromaccount", "00") + "00"
            kvp["_41_CASHBACK_AMOUNT"] = salerequest.get("amount_addl").rjust(12,'0')
        else:
            msg["F003"] = "00" + salerequest.get("fromaccount", "00") + "00"
    else:
        msg["F003"] = "00" + salerequest.get("fromaccount", "00") + "00"

    msg["F004"] = salerequest.get("amount_tran", "0")
    msg["F007"] = utilities.getF007()
    msg["F011"] = salerequest.get("stan", None)
    msg["F012"] = salerequest.get("time", None)
    msg["F013"] = salerequest.get("date", None)
    msg["F022"] = salerequest.get("posentrymode", None)
    msg["F025"] = "00"
    msg["F035"] = salerequest.get("track2", None)
    msg["F041"] = salerequest.get("tid", None)
    msg["F042"] = salerequest.get("mid", None)

    f043 = salerequest.get("mename").ljust(23)+salerequest.get("mecity").ljust(
        13)+salerequest.get("mestate").ljust(2)+salerequest.get("mecountry").ljust(2)
    msg["F043"] = f043

    msg["F049"] = salerequest.get("ccy_tran", None)

    if salerequest.get("pinblock"):
        msg["F052"] = salerequest.get("pinblock", None)
        kvp["PINUSED"] = "1"
    else:
        kvp["PINUSED"] = "0"

    if salerequest.get("emv_request"):
        msg["F055"] = salerequest.get("emv_request", None)

    msg["F061"] = terminfo["pdc"]
    msg["F062"] = salerequest.get("transactionid", None)

    nodeinfo = terminfo["acq_node_name"].ljust(15) + " ".ljust(15) + \
        salerequest.get("mid").ljust(15)+" ".ljust(15)
    msg["F122"] = nodeinfo

    acq_node_key = msg["MsgType"] + ":" + msg["F041"] + \
        ":" + msg["F011"] + ":" + msg["F007"]

    msg["F123_001"] = acq_node_key
    msg["F123_003"] = salerequest.get("mid")
    msg["F123_004"] = salerequest.get("tid")
    msg["F123_005"] = terminfo["bank_name"]
    msg["F123_006"] = salerequest.get("batchnr")
    msg["F123_008"] = salerequest.get("mid")
    msg["F123_011"] = "003"  # POS

    kvp["ZIPCODE"] = salerequest.get("zipcode")

    msg["F120"] = utilities.getKVPString(kvp)

    tm_request = json.dumps(msg)
    tm_headers = {'Content-Type': 'application/json'}

    saleresponse = {}
    saleresponse['amount_tran'] = salerequest.get("amount_tran", None)
    saleresponse['date'] = salerequest.get("date", None)
    saleresponse['stan'] = salerequest.get("stan", None)
    saleresponse['tid'] = salerequest.get("tid", None)
    saleresponse['time'] = salerequest.get("time", None)
    saleresponse['transactionid'] = salerequest.get("transactionid", None)

    try:
        rsp = requests.post(utilities.getTMURL(),
                            headers=tm_headers, data=tm_request)

        msg_rsp = json.loads(rsp.text)

        if 'F038' in msg_rsp:
            saleresponse['authid'] = msg_rsp["F038"]

        kvobj = utilities.getKVPObject(msg_rsp["F120"])

        if 'bin_owner' in kvobj:
            saleresponse['bin_owner'] = kvobj["bin_owner"]

        if 'card_type' in kvobj:
            saleresponse['cardtype'] = kvobj["card_type"]

        if 'F002' in msg_rsp:
            saleresponse['pan'] = msg_rsp["F002"]

        if 'F037' in msg_rsp:
            saleresponse['rrn'] = msg_rsp["F037"]

        if 'F039' in msg_rsp:
            saleresponse['resp_code'] = msg_rsp["F039"]

        if 'F055' in msg_rsp:
            saleresponse['emv_response'] = msg_rsp["F055"]
    except requests.exceptions.RequestException as e:
        print("Cannot connect to TM")
        print(e)
        saleresponse['resp_code'] = "96"
        abort(503, json.dumps(saleresponse))

    return jsonify(saleresponse)


def preauth(salerequest):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the Sale transaction.

    :return:    Sale response body
    -------------------------------------------------------------------------'''
    apikey = request.headers.get("apikey")
    kvp = {}

    # Fetch Terminal Info
    terminfo = getterminfo(salerequest.get("mid"), salerequest.get(
        "tid"), salerequest.get("bankcode"), apikey)

    if not terminfo["found"]:
        return abort(422)

    msg = {}
    msg["MsgType"] = "0100"
    msg["F003"] = "00" + salerequest.get("fromaccount", "00") + "00"
    msg["F004"] = salerequest.get("amount_tran", "0").rjust(12, '0')
    msg["F007"] = utilities.getF007()
    msg["F011"] = salerequest.get("stan", None)
    msg["F012"] = salerequest.get("time", None)
    msg["F013"] = salerequest.get("date", None)
    msg["F022"] = salerequest.get("posentrymode", None)
    msg["F025"] = "00"
    msg["F035"] = salerequest.get("track2", None)
    msg["F041"] = salerequest.get("tid", None)
    msg["F042"] = salerequest.get("mid", None)

    f043 = salerequest.get("mename").ljust(23)+salerequest.get("mecity").ljust(
        13)+salerequest.get("mestate").ljust(2)+salerequest.get("mecountry").ljust(2)
    msg["F043"] = f043

    msg["F049"] = salerequest.get("ccy_tran", None)

    if salerequest.get("pinblock"):
        msg["F052"] = salerequest.get("pinblock", None)
        kvp["PINUSED"] = "1"
    else:
        kvp["PINUSED"] = "0"

    if salerequest.get("emv_request"):
        msg["F055"] = salerequest.get("emv_request", None)

    msg["F061"] = terminfo["pdc"]
    msg["F062"] = salerequest.get("transactionid", None)

    nodeinfo = terminfo["acq_node_name"].ljust(15) + " ".ljust(15) + \
        salerequest.get("mid").ljust(15)+" ".ljust(15)
    msg["F122"] = nodeinfo

    acq_node_key = msg["MsgType"] + ":" + msg["F041"] + \
        ":" + msg["F011"] + ":" + msg["F007"]

    msg["F123_001"] = acq_node_key
    msg["F123_003"] = salerequest.get("mid")
    msg["F123_004"] = salerequest.get("tid")
    msg["F123_005"] = terminfo["bank_name"]
    msg["F123_006"] = salerequest.get("batchnr")
    msg["F123_008"] = salerequest.get("mid")
    msg["F123_011"] = "003"  # POS

    kvp["ZIPCODE"] = salerequest.get("zipcode")

    msg["F120"] = utilities.getKVPString(kvp)

    tm_request = json.dumps(msg)
    tm_headers = {'Content-Type': 'application/json'}

    saleresponse = {}
    saleresponse['amount_tran'] = salerequest.get("amount_tran", None)
    saleresponse['date'] = salerequest.get("date", None)
    saleresponse['stan'] = salerequest.get("stan", None)
    saleresponse['tid'] = salerequest.get("tid", None)
    saleresponse['time'] = salerequest.get("time", None)
    saleresponse['transactionid'] = salerequest.get("transactionid", None)

    try:
        rsp = requests.post(utilities.getTMURL(),
                            headers=tm_headers, data=tm_request)

        msg_rsp = json.loads(rsp.text)

        if 'F038' in msg_rsp:
            saleresponse['authid'] = msg_rsp["F038"]

        kvobj = utilities.getKVPObject(msg_rsp["F120"])

        if 'bin_owner' in kvobj:
            saleresponse['bin_owner'] = kvobj["bin_owner"]

        if 'card_type' in kvobj:
            saleresponse['cardtype'] = kvobj["card_type"]

        if 'F002' in msg_rsp:
            saleresponse['pan'] = msg_rsp["F002"]

        if 'F037' in msg_rsp:
            saleresponse['rrn'] = msg_rsp["F037"]

        if 'F039' in msg_rsp:
            saleresponse['resp_code'] = msg_rsp["F039"]

        if 'F055' in msg_rsp:
            saleresponse['emv_response'] = msg_rsp["F055"]
    except requests.exceptions.RequestException as e:
        print("Cannot connect to TM")
        print(e)
        saleresponse['resp_code'] = "96"
        abort(503, json.dumps(saleresponse))

    return jsonify(saleresponse)


def preauthcomplete(preauthcompleterequest):
    '''-------------------------------------------------------------------------
    This method takes in the preauth complete request and performs the PreAuth Complete transaction.

    :return:    PreAuth Complete response body
    -------------------------------------------------------------------------'''
    abort(400)


def voidreversal(voidrequest):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the Void/Reversal transaction.

    :return:    Void response body
    -------------------------------------------------------------------------'''
    abort(400)
