import persistance
import threading
from samtar import telegram
import zmq
import zmq_utils
import config
import json

def tokens():
    sqlite = persistance.SQlite(config.db_file)
    return sqlite.all_bots()

def publish_for_token(socket, token):
    for t, update in telegram.updates(token):
        res = {
                'token': t,
                'update': update
                }
        socket.send_string(json.dumps(res))

def all_updates():
    socket = zmq_utils.create_socket(zmq.SUB, config.telegram_incoming_pub_port, False)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        string = socket.recv_string()
        data = json.loads(string)
        yield data['token'], data['update']

def main():
    #creating context for zmq
    socket = zmq_utils.create_socket(zmq.PUB, config.telegram_incoming_pub_port, True)
    for token in tokens():
        t = threading.Thread(target=publish_for_token, args=(socket, token))
        t.start()

if __name__ == '__main__':
    main()
