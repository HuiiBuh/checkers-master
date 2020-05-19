from socket import socket, AF_INET, SOCK_STREAM, timeout
from message import Message
from client import Client
import time


class Server:

    PORT = 11111
    # IP of the server!
    IP = '10.3.141.1'
    EXIT = False
    CLIENT_TIMEOUT = 10 * 1000

    def __init__(self, ip, port):
        """
        Creates a instance of Server and creates a server_socket.
        :return: Noneserver
        """
        self.client = None

        # Create an INET, STREAMing socket
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        # Bind the socket to a host and port
        self.server_socket.bind((ip, port))
        self.server_socket.listen(1)
        self.msg_id = 0

        print("Socket successfully created.")

    def get_curr_msg_id(self):
        return self.msg_id

    def wait_for_connection(self, callback):
        """
        This function starts a loop which checks if a new client connects to the server.
        :return: None
        """
        print('Wait for connection...')
        while not Server.EXIT:
            try:
                self.server_socket.settimeout(0.5)
                # Accept connection from outside
                client_socket, address = self.server_socket.accept()
            except timeout:
                pass
            else:
                # Create a new ClientConnection and break loop
                self.client = Client.from_socket(client_socket)
                callback(self.client)
                self.server_socket.close()
                Server.EXIT = True
                break

    @staticmethod
    def convert_input(input_str):
        if "," in input_str:
            value_split = input_str.split(",")
            converted_data = {"x": int(value_split[0]), "y": int(value_split[1])}
        else:
            converted_data = int(input_str)

        return converted_data

    def send_instruction(self, action, data={}):
        instruction = {"id": self.msg_id,
                       "type": "instruction",
                       "action": action,
                       "data": data}
        self.msg_id = self.msg_id + 1
        message = Message()
        message.set_type(Message.TYPE_GAMEDATA)
        message.set_data(instruction)
        self.client.send(message)

    def send_interrupt(self, action, data={}):
        instruction = {"id": self.msg_id,
                       "type": "interrupt",
                       "action": action,
                       "data": data}
        self.msg_id = self.msg_id + 1
        message = Message()
        message.set_type(Message.TYPE_GAMEDATA)
        message.set_data(instruction)
        self.client.send(message)

    def send_action_init(self):
        self.send_instruction("init")

    def send_action_speak(self, text):
        self.send_instruction("speak", {"text": text})

    def send_action_wait(self):
        self.send_instruction("wait")

    def send_action_reset(self):
        self.send_instruction("reset")

    def send_action_shutdown(self):
        self.send_interrupt("shutdown")

    def send_action_remove(self, origin, wait=True):
        self.send_instruction("remove", {"src": origin, "wait": wait})

    def send_action_move(self, origin, target, wait=True):
        self.send_instruction("move", {"src": origin, "dest": target, "wait": wait})

    def send_action_replace(self, origin, target, wait=True):
        self.send_instruction("replace", {"src": origin, "dest": target, "wait": wait})

    def wait_for_input(self):
        msg_id = 0

        while True:
            print("-------------------------")
            action_input = input("ACTION: ")
            action = ""
            data = ""
            instruction_type = "instruction"

            if action_input == "mv":
                action = "move_value"
                value_x = float(input("X(cm): "))
                value_y = float(input("Y(cm): "))
                data = {"x": value_x, "y": value_y}
            elif action_input == "mp":
                action = "move_position"
                value = input("POS(num/x,y): ")
                data = self.convert_input(value)
            elif action_input == "m" or action_input == "mr":
                action = "move"
                value_src = input("SRC(num/x,y): ")
                value_dest = input("DEST(num/x,y): ")
                value_src = self.convert_input(value_src)
                value_dest = self.convert_input(value_dest)
                data = {"src": value_src, "dest": value_dest}
                if action_input == "mr":
                    data["wait"] = True
            elif action_input == "rm" or action_input == "rmr":
                action = "remove"
                value = input("SRC(num/x,y): ")
                data = {"src": self.convert_input(value)}
                if action_input == "rmr":
                    data["wait"] = True
            elif action_input == "rp" or action_input == "rpr":
                action = "replace"
                value_src = input("SRC(num/x,y): ")
                value_dest = input("DEST(num/x,y): ")
                value_src = self.convert_input(value_src)
                value_dest = self.convert_input(value_dest)
                data = {"src": value_src, "dest": value_dest}
                if action_input == "rpr":
                    data["wait"] = True
            elif action_input == "reset":
                action = "reset"
            elif action_input == "wait":
                action = "wait"
            elif action_input == "init":
                action = "init"
            elif action_input == "shutdown":
                action = "shutdown"
                instruction_type = "interrupt"
            elif action_input == "sp":
                action = "speak"
                text = str(input("Text: "))
                data = {"text": text}
            else:
                print("Invalid!")
                continue

            instruction = {"id": msg_id,
                           "type": instruction_type,
                           "action": action,
                           "data": data}
            try:
                message = Message()
                message.set_type(Message.TYPE_GAMEDATA)
                message.set_data(instruction)
                self.client.send(message)
                msg_id += 1
            except Exception as e:
                print(e)

            time.sleep(0.1)
