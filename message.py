import json
import time


class UnknownMessageTypeException(Exception):
    pass


class WrongJSONFormatException(Exception):
    pass


class ConnectingException(Exception):
    pass


class Message(object):
    """
    Message is used to represent information to be transmitted between the client connections.
    """

    TYPE_PING = 'ping'
    TYPE_PONG = 'pong'
    TYPE_TIMEOUT = 'timeout'
    TYPE_DISCONNECT = 'disconnect'
    TYPE_GAMEDATA = 'gamedata'
    TYPE_CONNECT = 'connect'
    TYPE_ERROR = 'error'
    TYPE_FEEDBACK = 'feedback'

    def __init__(self, msg=None):
        """
        Create an instance of message. If parameter msg is provided with a UTF-8 JSON string, the data will be
        extracted. If not possible all variables are set to none.
        :param msg: UTF-8 JSON str
        :type msg: str
        :param source_client: Source Client Connection (if None source is server)
        :type source_client: ClientConnection
        """
        self.type = None
        self.timestamp = int(time.time()*1000)
        self.data = None

        if msg:
            try:
                message = json.loads(msg)
                self.type = message["type"]
                self.timestamp = message["timestamp"]
                self.data = message["data"]
            except KeyError:
                raise WrongJSONFormatException("Required parameter is missing")

    def __repr__(self):
        """
        Represents the message as UTF-8 JSON string.
        :return: UTF-8 JSON string
        """
        msg = {
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data,
        }
        return json.dumps(msg)

    def get_type(self):
        """
        Get type of the message.
        :return: type
        """
        return self.type

    def set_type(self, type):
        """
        Set type of message. Use the pre declared types of message.
        :param type: type of the message
        :type type: str
        :return: None
        """
        self.type = type

    def get_data(self):
        """
        Get data of the message.
        :return: data
        """
        return self.data

    def set_data(self, data):
        """
        Set data of the message, this can be a dict, list or a singe variable.
        :param data: data
        :type data: dict, list, int, float, str or bool
        :return: None
        """
        self.data = data

    def get_timestamp(self):
        """
        Get timestamp in milliseconds as int.
        :return: ms as int
        """
        return self.timestamp

    def set_timestamp(self, timestamp=None):
        """
        Set timestamp in milliseconds as int.
        :param timestamp: ms as int
        :type timestamp: int
        :return: None
        """
        if timestamp is None:
            timestamp = int(time.time()*1000)
        self.timestamp = timestamp
