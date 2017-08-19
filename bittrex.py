import json
import time
import hmac
import requests

BASE_URL = "https://bittrex.com/api/v1.1"

def markethistory(market):

    end_point = "/public/getmarkethistory"
    res = requests.get(BASE_URL + end_point, { "market": market }).json()

    return res.get('result', [])

def tick(market):

    end_point = "/public/getticker"
    res = requests.get(BASE_URL + end_point, { "market": market }).json()

    return res['result']

def marketsummary(market=None):

    if not market:
        end_point = "/public/getmarketsummaries"
        res = requests.get(BASE_URL + end_point).json()

        return res['result']

    else:
        end_point = "/public/getmarketsummary"
        res = requests.get(BASE_URL + end_point, { "market": market }).json()

        return res['result']

def orderbook(market):

    end_point = "/public/getorderbook"
    res = requests.get(BASE_URL + end_point, { "market": market, "type": "both" }).json()

    return res.get('result', {})
