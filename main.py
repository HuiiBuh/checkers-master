from server import Server
from message import Message
from state import *
from threading import Thread
from ki_client import *
from ip_client import *
import time

IP = "0.0.0.0"
PORT = 11111

CURRENT_STATE = STATE_NOT_CONNECTED
CURRENT_KI_STATE = STATE_NOT_CONNECTED
CURRENT_IP_STATE = STATE_NOT_CONNECTED

# TODO CONSTANT STRINGS
WELCOME_AND_INSTRUCT = "Initialising Completed. Please set up game configuration"

server = Server(IP, PORT)

DIFFICULTY = -1
BUTTON_DATA = None
GAME_KEY = None

MSG_ID = {
    "init": -1,
    "welcome": -1,
    "shutdown": -1,
    "move": -1
}


# Color Black
PLAYER_KI = 1
# Color White
PLAYER_PLAYER = 2

CURRENT_PLAYER = PLAYER_KI


def check_ki():
    global CURRENT_KI_STATE
    if ping_ki():
        CURRENT_KI_STATE = STATE_CONNECTED
    else:
        print("KI False")


def check_ip():
    global CURRENT_IP_STATE
    if ping_ip():
        CURRENT_IP_STATE = STATE_CONNECTED
    else:
        CURRENT_IP_STATE = STATE_CONNECTED
        print("IP False")


def main():
    global CURRENT_IP_STATE, CURRENT_KI_STATE, CURRENT_STATE, BUTTON_DATA, DIFFICULTY, GAME_KEY
    server.wait_for_connection(on_client_connect)

    check_ki()
    check_ip()

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
        data = BUTTON_DATA
        if not data:
            continue
        else:
            long_pressed = data["long_press"]
            BUTTON_DATA = None

            print("Current State: %d" % CURRENT_STATE)

            if long_pressed:
                if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
                    MSG_ID["shutdown"] = server.get_curr_msg_id()
                    server.send_action_speak("Robot will Shutdown")
                    continue
                if CURRENT_STATE == STATE_PLAYER_CHECK_SETTINGS or CURRENT_STATE == STATE_PLAYER_PREPARE_GAME\
                        or CURRENT_STATE == STATE_PLAYING:
                    server.send_action_speak("Back to main menu")
                    CURRENT_STATE = STATE_PLAYER_INTRODUCED
                    DIFFICULTY = -1
                    GAME_KEY = None
                    server.send_action_wait()
                    continue
            else:
                if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
                    server.send_action_speak("I will check the configuration settings")
                    DIFFICULTY = check_configuration()
                    if DIFFICULTY >= 1:
                        CURRENT_STATE = STATE_PLAYER_CHECK_SETTINGS
                        server.send_action_speak("Player black will start. KI is set to difficult level %s. Please confirm" % DIFFICULTY)
                    else:
                        server.send_action_speak("Your settings are not correct or could not get processed. Please retry")
                    continue
                if CURRENT_STATE == STATE_PLAYER_CHECK_SETTINGS:
                    server.send_action_speak("Confirmed settings. Please prepare chess board")
                    CURRENT_STATE = STATE_PLAYER_PREPARE_GAME
                    # drive to reset pos
                    server.send_action_reset()
                    continue
                if CURRENT_STATE == STATE_PLAYER_PREPARE_GAME:
                    problems = check_init_chess_board()
                    if len(problems) == 0:
                        server.send_action_speak("Let the game begin")
                        server.send_action_wait()
                        GAME_KEY = ki_init_game(DIFFICULTY)
                        if GAME_KEY is None:
                            raise RuntimeError("API Error, could not create game!")
                        CURRENT_STATE = STATE_PLAYING
                        play()
                    else:
                        print("Following problems detected")
                        print(problems)
                        for problem in problems:
                            print(problem)
                        server.send_action_speak("The chess board does not seem correct prepared. Try again")
                    continue

                if CURRENT_STATE == STATE_PLAYING:
                    play()

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
        # TODO Shutdown
        server.client.disconnect()

    if data["instruction_id"] == MSG_ID["move"]:
        MSG_ID["move"] = -1


def play():
    global CURRENT_PLAYER, GAME_KEY

    if CURRENT_PLAYER == PLAYER_PLAYER:
        pieces = ip_get_board()
        print(pieces)
        moves = pieces_to_move(GAME_KEY, pieces)
        if moves is None:
            server.send_action_speak("Your move was incorrect. Make a correct move and press button to continue")
            return
        print(moves)
        make_move(GAME_KEY, moves["move_list"][0]["origin"], moves["move_list"][0]["target"])
        CURRENT_PLAYER = PLAYER_KI

        server.send_action_speak("Your move was correct")

    if CURRENT_PLAYER == PLAYER_KI:
        next_move = ki_next_move(GAME_KEY)
        if next_move is None:
            raise RuntimeError("No next move possible")
        # {'move': {'origin': 11, 'target': 16}, 'score': 0}

        MSG_ID["move"] = server.get_curr_msg_id()
        server.send_action_move(next_move["move"]["origin"], next_move["move"]["target"])

        make_move(GAME_KEY, next_move["move"]["origin"], next_move["move"]["target"])
        # todo remove?

        while MSG_ID["move"] != -1:
            time.sleep(0.2)

        CURRENT_PLAYER = PLAYER_PLAYER
        server.send_action_speak("Now it is your turn. Press button if finished")

def on_button_pressed(data):
    global BUTTON_DATA
    BUTTON_DATA = data
    """global CURRENT_STATE, DIFFICULTY, GAME_KEY
    if data["long_press"]:
        if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
            MSG_ID["shutdown"] = server.get_curr_msg_id()
            server.send_action_speak("Robot will Shutdown")
            return
        if CURRENT_STATE == STATE_PLAYER_CHECK_SETTINGS or CURRENT_STATE == STATE_PLAYER_PREPARE_GAME:
            server.send_action_speak("Back to main menu")
            CURRENT_STATE = STATE_PLAYER_INTRODUCED
            DIFFICULTY = -1
            GAME_KEY = None
            return
    else:
        if CURRENT_STATE == STATE_PLAYER_INTRODUCED:
            server.send_action_speak("I will check the configuration settings")
            DIFFICULTY = check_configuration()
            if DIFFICULTY >= 1:
                CURRENT_STATE = STATE_PLAYER_CHECK_SETTINGS
                server.send_action_speak("Player black will start. KI is set to difficult level %s. Please confirm" % DIFFICULTY)
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
            if len(check_init_chess_board()) == 0:
                server.send_action_speak("Let the game begin")
                server.send_action_wait()
                GAME_KEY = ki_init_game(DIFFICULTY)
                if GAME_KEY is None:
                    raise RuntimeError("API Error, could not create game!")
                play()
            else:
                server.send_action_speak("The chess board does not seem correct prepared. Try again")
            return"""


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
    for problem in check_init_chess_board():
        print(problem)


if __name__ == "__main__":
    debug()
    #main()

