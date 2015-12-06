import unpacky
import binascii


def test_get_byte():
    bindata = binascii.unhexlify('49')
    r = unpacky.get_byte(bindata)
    assert r == ('I', '')


def test_get_byte_int():
    bindata = binascii.unhexlify('10')
    r = unpacky.get_byte_int(bindata)
    assert r == (16, '')


def test_a2s_info_request():
    # https://developer.valvesoftware.com/wiki/Server_queries#Simple_Response_Format
    raw_hex = "FF FF FF FF 54 53 6F 75 72 63 65 20 45 6E 67 69 6E 65 20 51 75 65 72 79 00"
    raw_hex = raw_hex.replace(' ', '')
    data = binascii.unhexlify(raw_hex)
    pattern = "----{byte:header}{string:payload}"
    unpacked = unpacky.Unpacky(pattern, data).data
    assert unpacked['header'] == 'T'
    assert unpacked['payload'] == 'Source Engine Query'


def test_a2s_info_response():
    # https://developer.valvesoftware.com/wiki/Server_queries#Simple_Response_Format
    raw_hex = (
        "FF FF FF FF 49 02 67 61 6D 65 32 78 73 2E 63 6F"
        "6D 20 43 6F 75 6E 74 65 72 2D 53 74 72 69 6B 65"
        "20 53 6F 75 72 63 65 20 23 31 00 64 65 5F 64 75"
        "73 74 00 63 73 74 72 69 6B 65 00 43 6F 75 6E 74"
        "65 72 2D 53 74 72 69 6B 65 3A 20 53 6F 75 72 63"
        "65 00 F0 00 05 10 04 64 6C 00 00 31 2E 30 2E 30"
        "2E 32 32 00"
    )
    raw_hex = raw_hex.replace(' ', '')
    data = binascii.unhexlify(raw_hex)
    pattern = (
        "----{byte:header}{byte_int:protocol}{string:name}{string:map}{string:folder}"
        "{string:game}{int:id}{byte_int:players}{byte_int:max_players}{byte_int:bots}"
        "{byte:server_type}{byte:environment}"
        "{byte_int:visibility}{byte_bool:vac}"
    )
    unpacked = unpacky.Unpacky(pattern, data).data
    assert unpacked['header'] == 'I'
    assert unpacked['environment'] == 'l'
    assert unpacked['folder'] == 'cstrike'
    assert unpacked['game'] == 'Counter-Strike: Source'
    assert unpacked['bots'] == 4
    assert unpacked['server_type'] == 'd'
    assert unpacked['environment'] == 'l'
    assert unpacked['visibility'] == 0
    assert unpacked['vac'] is False


def test_a2s_player_challenge_response():
    raw_hex = "FF FF FF FF 41 4B A1 D5 22"
    raw_hex = raw_hex.replace(' ', '')
    data = binascii.unhexlify(raw_hex)
    pattern = "----{byte:header}{long:challenge}"
    unpacked = unpacky.Unpacky(pattern, data).data
    assert unpacked['header'] == 'A'
    assert unpacked['challenge'] == 584425803


def test_a2s_player_info():
    raw_hex = (
        "FF FF FF FF 44 02 01 5B 44 5D 2D 2D 2D 2D 3E 54"
        "2E 4E 2E 57 3C 2D 2D 2D 2D 00 0E 00 00 00 B4 97"
        "00 44 02 4B 69 6C 6C 65 72 20 21 21 21 00 05 00"
        "00 00 69 24 D9 43"
    )
    raw_hex = raw_hex.replace(' ', '')
    data = binascii.unhexlify(raw_hex)
    pattern = "----{byte:header}{byte_int:number_of_players}"
    unpacked = unpacky.Unpacky(pattern, data)
    player_dict = unpacked.data
    assert player_dict['header'] == 'D'
    assert player_dict['number_of_players'] == 2
    number_of_players = player_dict['number_of_players']

    player_list = []
    player_pattern = "{byte_int:index}{string:name}{long:score}{long:duration}"
    for _ in range(number_of_players):
        print len(unpacked.remaining_data)
        unpacked = unpacky.Unpacky(player_pattern, unpacked.remaining_data)
        player_dict = unpacked.data
        player_list.append(player_dict)

    # player 1
    assert player_list[0]['index'] == 1
    assert player_list[0]['name'] == '[D]---->T.N.W<----'
    assert player_list[0]['score'] == 14
    assert player_list[0]['duration'] == 1140889524

    # player 2
    assert player_list[1]['index'] == 2
    assert player_list[1]['name'] == 'Killer !!!'
    assert player_list[1]['score'] == 5
    assert player_list[1]['duration'] == 1138304105


def test_unpack_end_to_end():
    hex_data = (
        "4911010101010101687474703a2f2f7777772e536169676e732e6465202833292052554e4f464"
        "600646d5f72756e6f666600686c326d70005465616d2044656174686d6174636800400119200c64770001333"
        "0393435343200b0996907984c8df6174001736169676e732c5f726567697374657265642c73746174732c696"
        "e637265617365645f6d6178706c617965727300"
    )
    data = binascii.unhexlify(hex_data)

    pattern = (
        "{byte:header}{byte_int:protocol}{string:name}{string:map}{string:folder}{string:game}"
        "{int:id}{byte_int:players}{byte_int:max_players}{byte_int:bots}"
        "{byte:server_type}{byte:environment}"
        "{byte_int:visibility}{byte_bool:vac}"
    )
    unpacked = unpacky.Unpacky(pattern, data).data
    assert unpacked['header'] == 'I'
    assert unpacked['environment'] == 'w'
    assert unpacked['folder'] == 'hl2mp'
    assert unpacked['game'] == 'Team Deathmatch'
    assert unpacked['bots'] == 12
