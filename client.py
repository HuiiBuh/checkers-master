
from socket import socket, AF_INET, SOCK_STREAM, timeout
from message import Message
from threading import Thread
import time


class Client(Thread):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.last_ping = None
        self.timeout = 10000

    def disconnect(self):
        message = Message()
        message.set_type(Message.TYPE_DISCONNECT)
        self.send(message)
        self.socket.close()

    def send(self, msg):
        """
        Send message to server
        :param msg:
        :return:
        """
        print("[OUT]"+str(msg))
        self.socket.sendall(bytes((str(msg)+'\0').encode("utf-8")))

    def on_message(self, msg):
        """
        This event is called if a new message was received.
        :param msg: Message (hopefully in JSON-format as string)
        :type msg: str
        :return: None
        """
        message = Message(msg)
        print("[IN]"+str(message))

        if message.get_type() == Message.TYPE_ERROR:
            return self.on_error(message)

        if message.get_type() == Message.TYPE_CONNECT:
            return self.on_connect()

        if message.get_type() == Message.TYPE_PING:
            return self.on_ping()

        if message.get_type() == Message.TYPE_FEEDBACK:
            return self.on_feedback(message)

        if message.get_type() == Message.TYPE_GAMEDATA:
            return self.on_gamedata(message)

    def on_error(self, message):
        """
        Is called if a error happened on server side
        :param message:
        :return:
        """
        pass

    def on_connect(self):
        """
        Is called after connect
        :return:
        """
        message = Message()
        message.set_type(Message.TYPE_CONNECT)
        message.set_timestamp(int(time.time() * 1000))
        message.set_data({"timeout": self.timeout})
        self.send(message)

    def on_feedback(self, msg):
        pass

    def on_gamedata(self,msg):
        pass

    def on_ping(self):
        self.last_ping = time.time() * 1000
        self.send_pong()

    def send_pong(self):
        """
        Send pong to the client
        :return:
        """
        message = Message()
        message.set_type(Message.TYPE_PONG)
        message.set_timestamp(int(time.time()*1000))
        self.send(message)

    def run(self):
        """
        This functions starts a loop which checks if data was received and append data pieces together til a full
        message was transmitted.
        :return: None
        """
        received_data = ""
        print("start receiving from client")
        while True:
            #self.on_tick()
            try:
                self.socket.settimeout(0.2)
                piece = self.socket.recv(4096).decode("utf-8")
                if piece == '':
                    continue
                find = piece.find('\0')
                while find != -1:
                    received_data += piece[:find]
                    self.on_message(received_data)
                    received_data = ""
                    piece = piece[find+1:]
                    find = piece.find("\0")
                else:
                    received_data += piece
            except timeout:
                pass
            except OSError:
                print("Connection is gone!")
                break

    @staticmethod
    def from_socket(client_socket):
        client = Client(None, None)
        client.start()
        client.socket = client_socket
        return client

