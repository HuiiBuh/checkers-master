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
    return None