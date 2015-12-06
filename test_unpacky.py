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
        "{short:id}{byte_int:players}{byte_int:max_players}{byte_int:bots}"
        "{byte:server_type}{byte:environment}"
        "{byte_int:visibility}{byte_bool:vac}"
    )
    unpacked = unpacky.Unpacky(pattern, data).data
    assert unpacked['header'] == 'I'
    assert unpacked['environment'] == 'w'
    assert unpacked['folder'] == 'hl2mp'
    assert unpacked['game'] == 'Team Deathmatch'
    assert unpacked['bots'] == 12
