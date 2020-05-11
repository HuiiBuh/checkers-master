from server import Server
from message import Message
from state import *
from threading import Thread
import requests
import json
import time

IP = "0.0.0.0"
PORT = 11111

CURRENT_STATE = STATE_NOT_CONNECTED
CURRENT_KI_STATE = STATE_NOT_CONNECTED
CURRENT_IP_STATE = STATE_NOT_CONNECTED

URI_KI = "https://checkersai.nebula.blue/"
HEADER_KI = {"X-authentication-token": "NYN4BLE2GBGH8YKJMLTJY6A8XX4XEXLLZXRGU27XT2WV2GSSFT2WBQMA54UUCCSB"}

# TODO CONSTANT STRINGS
WELCOME_AND_INSTRUCT = "Initialising Completed. Please set up game configuration"

server = Server(IP, PORT)

MSG_ID = {
    "init": -1,
    "welcome": -1,
    "shutdown": -1
}


def ping_ki():
    global CURRENT_KI_STATE
    response = requests.get(URI_KI+"ping", headers=HEADER_KI)
    if response.status_code == 200:
        CURRENT_KI_STATE = STATE_CONNECTED


def check_configuration():
    pass


def check_init_chess_board():
    pass


def ki_init_game(difficulty: int, player_starts: bool = False):
    params = {
        "difficulty": difficulty,
        "player_first": player_starts
    }
    response = requests.put(URI_KI+"game", headers=HEADER_KI, params=params)
    if response.status_code == 201:
        data = json.loads(response.text)
        game_key = data["game_key"]
        return game_key
    return None


def ki_next_move(game_key):
    response = requests.get("%sgame/%s/move" % (URI_KI, game_key), headers=HEADER_KI)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None


def ping_ip():
    global CURRENT_IP_STATE
    CURRENT_IP_STATE = STATE_CONNECTED


def main():
    server.wait_for_connection(on_client_connect)

    Thread(target=ping_ki).start()
    Thread(target=ping_ip).start()

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
    game_key = ki_init_game(4)
    move = ki_next_move(game_key)
    print(move)

if __name__ == "__main__":
    debug()
    #main()

