from src.piclient import PiClient

# Setup the PiClient
client = PiClient(
    url='https://boarddetection.nebula.blue',
    token='uhe3xXfev3H3ehjkUswY9QWpiqzhYvH8y5YmpSvMRDoy8yFvH5LXnbY5phJ5tu88'
)


def ping_ip():
    return client.ping()


def print_pieces():
    pieces, _ = client.detect()
    print(pieces)


def check_configuration():
    pass


def check_init_chess_board():
    pass