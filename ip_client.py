from src.piclient import PiClient
import math

options = {
    "boarddetector": {
        "prepare": {
            "resize": [512, 512]
        },
        "corners": {
            "maxcorners": 500,
            "qualitylevel": 0.01,
            "mindistance": 20
        },
        "lines": {
            "harris": {
                "rho": 1,
                "theta": 0.01,
                "threshold": 350
            },
            "filter": {
                "rho": 20,
                "theta": 0.15
            }
        },
        "similarpoints": {
            "range": 9
        },
        "correctlines": {
            "amount": 9
        }
    },
    "figuredetector": {
        "circles": {
            "rho": 1,
            "mindist": 40,
            "param1": 150,
            "param2": 15,
            "minradius": 0,
            "maxradius": 30
        },
        "colors": {
            "white": {
                "normal": {
                    "lower": [160, 0, 170],
                    "upper": [180, 120, 255]
                },
                "king": {
                    "lower": [115, 0, 0],
                    "upper": [160, 255, 255]
                },
            },
            "black": {
                "normal": {
                    "lower": [160, 0, 0],
                    "upper": [180, 255, 150]
                },
                "king": {
                    "lower": [160, 120, 160],
                    "upper": [180, 255, 255]
                }
            }
        }
    }
}


# Setup the PiClient
client = PiClient(
    url='https://boarddetection.nebula.blue',
    token='uhe3xXfev3H3ehjkUswY9QWpiqzhYvH8y5YmpSvMRDoy8yFvH5LXnbY5phJ5tu88'
)


def ping_ip():
    return client.ping()


def print_pieces():
    pieces, _ = client.detect(options=options)
    for piece in pieces:
        print(piece)


def ip_get_board():
    pieces, _ = client.detect(options=options)
    return pieces


def check_configuration():
    pieces, _ = client.detect(options=options)
    if not pieces:
        return -1

    pos = -1

    # TODO only one

    for piece in pieces:
        if 13 <= piece["position"] <= 20:
            pos = piece["position"]

    if pos == -1:
        return -1

    pos = pos - 12

    if pos > 4:
        pos = (pos - 4) * 2
    else:
        pos = pos * 2 - 1

    return int(pos)


def _found_piece(problems, piece):
    for problem in problems:
        if problem["position"] == piece["position"]:
            return problems.remove(problem)


def check_init_chess_board():
    pieces, _ = client.detect(options=options)

    if not pieces:
        raise RuntimeError("API ERROR could not fetch current chess board")

    problems = [{"position": i, "player": 1, "king": False, "error": "missing"} for i in range(1, 13)] +\
               [{"position": i, "player": 2, "king": False, "error": "missing"} for i in range(21, 33)]

    for piece in pieces:
        # Player 1
        if piece["position"] <= 12:
            _found_piece(problems, piece)
            if piece["player"] != 1 and piece["king"]:
                piece["error"] = "wrong player and piece is king"
            elif piece["player"] != 1:
                piece["error"] = "wrong player"
            elif piece["king"]:
                piece["error"] = "piece is king"

            if "error" in piece.keys():
                problems.append(piece)
        # Player 2
        elif piece["position"] >= 21:
            _found_piece(problems, piece)
            if piece["player"] != 2 and piece["king"]:
                piece["error"] = "wrong player and piece is king"
            elif piece["player"] != 2:
                piece["error"] = "wrong player"
            elif piece["king"]:
                piece["error"] = "piece is king"

            if "error" in piece.keys():
                problems.append(piece)
        # Piece out of init pos
        else:
            piece["error"] = "incorrect position"
            problems.append(piece)

    return problems
