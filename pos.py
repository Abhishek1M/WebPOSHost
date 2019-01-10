import connexion
import simplejson as json
import utilities
import requests
import posconf

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


def processtransaction(ptrequest, mti, apikey):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the transaction.

    :return:    Transaction response body
    -------------------------------------------------------------------------'''
    kvp = {}

    # Fetch Terminal Info
    terminfo = getterminfo(ptrequest.get("mid"), ptrequest.get(
        "tid"), ptrequest.get("bankcode"), apikey)

    if not terminfo["found"]:
        return abort(422)

    msg = {}
    msg["MsgType"] = mti

    if ptrequest.get("amount_addl"):
        cashamt = int(ptrequest.get("amount_addl"))
        if cashamt > 0:
            msg["F003"] = "09" + ptrequest.get("fromaccount", "00") + "00"
            kvp["_41_CASHBACK_AMOUNT"] = ptrequest.get(
                "amount_addl").rjust(12, '0')
        else:
            msg["F003"] = "00" + ptrequest.get("fromaccount", "00") + "00"
    else:
        msg["F003"] = "00" + ptrequest.get("fromaccount", "00") + "00"

    msg["F004"] = ptrequest.get("amount_tran", "0")
    msg["F007"] = utilities.getF007()
    msg["F011"] = ptrequest.get("stan", None)
    msg["F012"] = ptrequest.get("time", None)
    msg["F013"] = ptrequest.get("date", None)
    msg["F018"] = ptrequest.get("mcc", None)
    msg["F022"] = ptrequest.get("posentrymode", None)
    msg["F025"] = "00"
    msg["F035"] = ptrequest.get("track2", None)
    msg["F041"] = ptrequest.get("tid", None)
    msg["F042"] = ptrequest.get("mid", None)

    f043 = ptrequest.get("mename").ljust(23)+ptrequest.get("mecity").ljust(
        13)+ptrequest.get("mestate").ljust(2)+ptrequest.get("mecountry").ljust(2)
    msg["F043"] = f043

    msg["F049"] = ptrequest.get("ccy_tran", None)

    if ptrequest.get("pinblock"):
        msg["F052"] = ptrequest.get("pinblock", None)
        kvp["PINUSED"] = "1"
    else:
        kvp["PINUSED"] = "0"

    if ptrequest.get("emv_request"):
        msg["F055"] = ptrequest.get("emv_request", None)

    msg["F061"] = terminfo["pdc"]
    msg["F062"] = ptrequest.get("transactionid", None)

    nodeinfo = terminfo["acq_node_name"].ljust(15) + " ".ljust(15) + \
        ptrequest.get("mid").ljust(15)+" ".ljust(15)
    msg["F122"] = nodeinfo

    acq_node_key = msg["MsgType"] + ":" + msg["F041"] + \
        ":" + msg["F011"] + ":" + msg["F007"]

    msg["F123_001"] = acq_node_key
    msg["F123_003"] = ptrequest.get("mid")
    msg["F123_004"] = ptrequest.get("tid")
    msg["F123_005"] = terminfo["bank_name"]
    msg["F123_006"] = ptrequest.get("batchnr")
    msg["F123_008"] = ptrequest.get("mid")
    msg["F123_011"] = "003"  # POS

    kvp["ZIPCODE"] = ptrequest.get("zipcode")
    kvp["MERCHANTTYPE"] = ptrequest.get("merchanttype")

    msg["F120"] = utilities.getKVPString(kvp)

    tm_request = json.dumps(msg)
    tm_headers = {'Content-Type': 'application/json'}

    saleresponse = {}
    saleresponse['amount_tran'] = ptrequest.get("amount_tran", None)
    saleresponse['date'] = ptrequest.get("date", None)
    saleresponse['stan'] = ptrequest.get("stan", None)
    saleresponse['tid'] = ptrequest.get("tid", None)
    saleresponse['time'] = ptrequest.get("time", None)
    saleresponse['transactionid'] = ptrequest.get("transactionid", None)

    try:
        rsp = requests.post(posconf.tmurl,
                            headers=tm_headers, data=tm_request, timeout=100)

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


def sale(salerequest):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the Sale transaction.

    :return:    Sale response body
    -------------------------------------------------------------------------'''
    apikey = request.headers.get("apikey")

    return processtransaction(salerequest, '0200', apikey)


def preauth(salerequest):
    '''-------------------------------------------------------------------------
    This method takes in the request and performs the Pre-Auth transaction.

    :return:    Pre-Auth response body
    -------------------------------------------------------------------------'''
    apikey = request.headers.get("apikey")

    return processtransaction(salerequest, '0100', apikey)


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
