import zmq
import zmq_utils
import threading
import config
import json
from queue import Queue
from samtar import telegram


CONQ = 30
q = Queue()

def worker():
    global q
    while True:
        token, chat_id, text, parsed_text, reply_markup = q.get()
        res = telegram.send_message(token, chat_id, text, parsed_text=parsed_text, reply_markup=reply_markup)
        print(res)
        q.task_done()

def send_message(socket, token, chat_id, text, parsed_text=None, reply_markup=None):
    data = json.dumps([token, chat_id, text, parsed_text, reply_markup])
    socket.send_string(data)

def main():
    global q
    global CONQ
    socket = zmq_utils.create_socket(zmq.SUB, config.telegram_outgoing_pub_port, True)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    # start threads
    for i in range(CONQ):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
    while True:
        msg = socket.recv_string()
        print(msg)
        args = tuple(json.loads(msg))
        q.put(args)


if __name__ == '__main__':
    main()
