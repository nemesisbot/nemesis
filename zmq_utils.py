import zmq

def create_socket(socket_type, port, bind=True):

    context = zmq.Context()
    socket = context.socket(socket_type)
    if bind:
        socket.bind("tcp://*:%s" % port)
    else:
        socket.connect("tcp://127.0.0.1:%s" % port)

    return socket
