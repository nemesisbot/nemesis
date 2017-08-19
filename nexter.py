import zmq
import zmq_utils
import json
import persistance
import config
from samtar import telegram
import telegram_outgoing as tgo
from datetime import datetime

def market_summaries():
    socket = zmq_utils.create_socket(zmq.SUB, "5555", bind=False)
    socket.setsockopt_string(zmq.SUBSCRIBE,'')
    while True:
        string = socket.recv_string()
        yield json.loads(string)

def create_message(cp, ms, prev_ms):
    parsed_text = [
            "[{}](https://bittrex.com/Market/Index?MarketName={})".format(ms['MarketName'], ms['MarketName']),
            "\nvolume changed by",
            "*{:.3f}%*".format(cp),
            "from {}".format(prev_ms['BaseVolume']),
            "to {}".format(ms['BaseVolume']),
            "\nbid: {:.8f}".format(ms['Bid']),
            "\nlast: {:.8f}".format(ms['Low']),
            "\nask: {:.8f}".format(ms['Ask']),
            "\nat {:%c} UTC".format(datetime.strptime(ms['TimeStamp'], "%Y-%m-%dT%H:%M:%S.%f" if '.'  in ms['TimeStamp'] else "%Y-%m-%dT%H:%M:%S"))
            ]
    return ' '.join(parsed_text)

def main():
    import time
    import random
    sqlite = persistance.SQlite(config.db_file)
    socket = zmq_utils.create_socket(zmq.PUB, config.telegram_outgoing_pub_port, False)
    prev = {}
    for ms in market_summaries():
        market = ms['MarketName']
        prev_ms = prev.get(market, None)
        if prev_ms:
            vols = sqlite.get_volumes()
            change_percent = ms['BaseVolume'] - prev_ms['BaseVolume']
            change_percent = 0 if prev_ms['BaseVolume'] == 0 else change_percent/prev_ms['BaseVolume']
            change_percent *= 100
            for vol in vols:
                is_base_btc = ms['MarketName'][:4] == 'BTC-'
                if is_base_btc and (change_percent > vol[2] or change_percent < -1 * vol[3]):
                    tgo.send_message(socket, vol[0], vol[1], create_message(change_percent, ms, prev_ms), 'Markdown')
        prev[market] = ms



if __name__ == "__main__":
    main()
