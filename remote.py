import socket
import unpacky


PLAYER_STATS_HEADER = "----{byte_chr:header}{byte_int:number_of_players}"
PLAYER_STATS = "{byte_int:index}{string:name}{long:points}{long:time}"

SERVER_INFO = (
    "----{byte:header}{byte_int:protocol}{string:name}{string:map}{string:folder}"
    "{string:game}{short:id}{byte_int:players}{byte_int:max_players}"
    "{byte_int:bots}{byte:server_type}{byte:environment}"
    "{byte_int:visibility}{byte_bool:vac}"
)

S2A_INFO_SOURCE = chr(0x49)
A2S_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
A2S_PLAYERS = b'\xFF\xFF\xFF\xFF\x55'
A2S_RULES = b'\xFF\xFF\xFF\xFF\x56'

CHALLENGE_PATTERN = "----{byte:header}{short:challenge}"


def hostname2ip(hostname):
    ip = socket.gethostbyname(hostname)
    return ip


class RemoteQuery(object):

    def __init__(self, server_name, port=27015, timeout=5):
        self.server_name = server_name
        ip = hostname2ip(server_name)
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.connect()

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        sock.connect((self.ip, self.port))
        self.socket = sock
        return sock

    def get_info(self):
        self.connect()
        self.socket.send(A2S_INFO)
        data = self.socket.recv(4096)

        # https://developer.valvesoftware.com/wiki/Server_queries
        server_info_dict = unpacky.Unpacky(SERVER_INFO, data).data
        return server_info_dict

    def _get_challenge_socket(self):
        A2S_PLAYER_REQUEST = A2S_PLAYERS + b'0xFFFFFFFF'
        self.socket.send(A2S_PLAYER_REQUEST)
        return self.socket.recv(4096)

    def get_challenge(self):
        self.connect()
        data = self._get_challenge_socket()
        up = unpacky.Unpacky(CHALLENGE_PATTERN, data)
        challenge = data[5:].strip()
        assert up.data['header'] == 'A'
        #
        return challenge

    def get_players(self):
        self.connect()
        challenge = self.get_challenge()
        self.socket.send(A2S_PLAYERS + challenge)
        data = self.socket.recv(4096)
        up = unpacky.Unpacky(PLAYER_STATS_HEADER, data)
        remaining_data = up.remaining_data
        players = []

        while remaining_data:
            player = unpacky.Unpacky(PLAYER_STATS, remaining_data)
            player_dict = player.data
            remaining_data = player.remaining_data
            players.append(player_dict)
        return players


if __name__ == '__main__':
    server = '66.151.138.182'
    rq = RemoteQuery(server, 27015)
    res = rq.get_info()

    print "Server Info"
    print "----------------------------------"
    for key, value in res.items():
        print "{0:<15} {1}".format(key, value)


    print
    print "Player Info"
    print "-----------------------------------------------------"
    for player in rq.get_players():
        print "{index:<2} {name:<35} {points:<3} {time}".format(**player)
