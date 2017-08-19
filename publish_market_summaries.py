import zmq
import next
import sys
import json

from datetime import datetime

def create_socket(socket_type, port, bind=True):
    context = zmq.Context()
    socket = context.socket(socket_type)
    if bind:
        socket.bind("tcp://*:%s" % port)

    return socket

def publish(socket, topic, data):
    data_as_string = json.dumps(data)
    socket.send_string("%s" % data_as_string)

def main():
    try:
        port = sys.argv[1]
    except IndexError:
        port = 5555
    socket = create_socket(zmq.PUB, str(port))
    prev_market_summary_tick = {}
    for summaries in next.marketsummaries():
        for ms in summaries:
            market = ms['MarketName']
            prev_ms = prev_market_summary_tick.get(market, None)
            if prev_ms:
                prev_timestamp = datetime.strptime(prev_ms['TimeStamp'], "%Y-%m-%dT%H:%M:%S.%f" if '.' in prev_ms['TimeStamp'] else "%Y-%m-%dT%H:%M:%S")
                curr_timestamp =  datetime.strptime(ms['TimeStamp'], "%Y-%m-%dT%H:%M:%S.%f" if '.' in ms['TimeStamp'] else "%Y-%m-%dT%H:%M:%S")
                if curr_timestamp > prev_timestamp:
                    prev_ms = ms
                    publish(socket, market, prev_ms)
            else:
                prev_ms = ms
                publish(socket, market, prev_ms)
            prev_market_summary_tick[market] = prev_ms


if __name__ == "__main__":
    main()
