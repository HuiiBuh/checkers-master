from server import Server
from message import Message
from state import *
from threading import Thread
from ki_client import *
from pi_client import *
import time

IP = "0.0.0.0"
PORT = 11111

CURRENT_STATE = STATE_NOT_CONNECTED
CURRENT_KI_STATE = STATE_NOT_CONNECTED
CURRENT_IP_STATE = STATE_NOT_CONNECTED

# TODO CONSTANT STRINGS
WELCOME_AND_INSTRUCT = "Initialising Completed. Please set up game configuration"

server = Server(IP, PORT)

MSG_ID = {
    "init": -1,
    "welcome": -1,
    "shutdown": -1
}


def check_ki():
    global CURRENT_KI_STATE
    if ping_ki():
        CURRENT_KI_STATE = STATE_CONNECTED


def check_ip():
    global CURRENT_IP_STATE
    if ping_ip():
        CURRENT_IP_STATE = STATE_CONNECTED


def main():
    server.wait_for_connection(on_client_connect)

    Thread(target=check_ki).start()
    Thread(target=check_ip).start()

    while not (CURRENT_IP_STATE == STATE_CONNECTED and CURRENT_KI_STATE == STATE_CONNECTED and CURRENT_STATE == STATE_READY_FOR_SETUP):
        time.sleep(0.2)

    print("IP + KI + RB are rdy!")

    server.send_action_wait()
    MSG_ID["welcome"] = server.get_curr_msg_id()
    server.send_action_speak(WELCOME_AND_INSTRUCT)

    while not CURRENT_STATE == STATE_PLAYER_INTRODUCED:
        time.sleep(0.2)

    while True:
        time.sleep(0.2)

    #server.client.disconnect()


def on_feedback(msg: Message):
    global CURRENT_STATE, MSG_ID
    data = msg.get_data()
    if data["instruction_id"] == MSG_ID["init"]:
        if data["success"] == True:
            CURRENT_STATE = STATE_READY_FOR_SETUP
        else:
            print("Error while initialising")

    if data["instruction_id"] == MSG_ID["welcome"]:
        if data["success"] == True:
            CURRENT_STATE = STATE_PLAYER_INTRODUCED
        else:
            print("Error while speaking")

    if data["instruction_id"] == MSG_ID["shutdown"]:
        server.client.disconnect()


def on_button_pressed(data):
    global CURRENT_STATE
    if data["long_press"]:
        if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
            MSG_ID["shutdown"] = server.get_curr_msg_id()
            server.send_action_speak("Robot will Shutdown")
            return
        if CURRENT_STATE == STATE_PLAYER_CHECK_SETTINGS or CURRENT_STATE == STATE_PLAYER_PREPARE_GAME:
            server.send_action_speak("Back to main menu")
            CURRENT_STATE = STATE_PLAYER_INTRODUCED
            return
    else:
        if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
            server.send_action_speak("I will check the configuration settings")
            if check_configuration():
                CURRENT_STATE = STATE_PLAYER_CHECK_SETTINGS
                server.send_action_speak("Player white will start. KI is set to difficult level 4. Please confirm")
            else:
                server.send_action_speak("Your settings are not correct or could not get processed. Please retry")
            return
        if CURRENT_STATE == STATE_PLAYER_CHECK_SETTINGS:
            server.send_action_speak("Confirmed settings. Please prepare chess board")
            CURRENT_STATE = STATE_PLAYER_PREPARE_GAME
            # drive to reset pos
            server.send_action_reset()
            return
        if CURRENT_STATE == STATE_PLAYER_PREPARE_GAME:
            if check_init_chess_board():
                server.send_action_speak("Let the game begin")
                server.send_action_wait()
                # TODO API CALL K
            else:
                server.send_action_speak("The chess board does not seem correct prepared. Try again")
            return


def on_gamedata(msg):
    data = msg.get_data()
    if data["action"] == "button":
        return on_button_pressed(data["data"])


def on_client_connect(client):
    print("Robot connected, send init instruction...")
    client.on_feedback = on_feedback
    client.on_gamedata = on_gamedata

    global CURRENT_STATE, MSG_ID
    CURRENT_STATE = STATE_INITIALISING

    MSG_ID["init"] = server.get_curr_msg_id()

    server.send_action_init()


def debug():
    print_pieces()

if __name__ == "__main__":
    debug()
    #main()

