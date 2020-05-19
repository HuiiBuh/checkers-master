import requests
import json

URI_KI = "https://checkersai.nebula.blue/"
HEADER_KI = {"X-authentication-token": "NYN4BLE2GBGH8YKJMLTJY6A8XX4XEXLLZXRGU27XT2WV2GSSFT2WBQMA54UUCCSB"}


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


def ki_get_board(game_key):
    response = requests.get(URI_KI+"game/"+game_key, headers=HEADER_KI)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    return None


def pieces_to_move(game_key, pieces):
    response = requests.post(URI_KI+"game/"+game_key+"/pieces-to-move", headers=HEADER_KI, data=json.dumps(pieces))
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print(response.text)
        print(response.status_code)
    return None


def ping_ki():
    response = requests.get(URI_KI+"ping", headers=HEADER_KI)
    if response.status_code == 200:
        return True
    return False


def ki_next_move(game_key):
    response = requests.get("%sgame/%s/move" % (URI_KI, game_key), headers=HEADER_KI)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print(response.text)
    return None


def make_move(game_key, origin, target):
    response = requests.post("%sgame/%s/move" % (URI_KI, game_key), headers=HEADER_KI, data=json.dumps({"origin": origin, "target": target}))
    if response.status_code == 200:
        print(response.text)
        return json.loads(response.text)
    else:
        print(response.text)
    return False
