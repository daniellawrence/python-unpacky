#!/usr/bin/env python
import struct
import re


def get_byte(data):
    byte = data[0]
    remaining_data = data[1:]
    return byte, remaining_data


def get_bytes(data, number_of_bytes):
    byte = data[number_of_bytes]
    remaining_data = data[number_of_bytes+1:]
    return ord(byte), remaining_data


def get_byte_int(data):
    response, remaining_data = get_byte(data)
    response = ord(response)
    return response, remaining_data


def get_byte_chr(data):
    response, remaining_data = get_byte_int(data)
    return chr(response), remaining_data


def get_byte_bool(data):
    response, remaining_data = get_byte_int(data)
    return bool(int(response)), remaining_data


def get_short(data):
    SHORT_LEN = 2
    short_data = data[0:SHORT_LEN]
    remaining_data = data[SHORT_LEN:]
    return struct.unpack('<h', short_data)[0], remaining_data


def get_long(data):
    return struct.unpack('<l', data[0:4])[0], data[4:]


def get_longlong(data):
    return struct.unpack('<Q', data[0:8])[0], data[8:]


def get_float(data):
    return struct.unpack('<f', data[0:4])[0], data[4:]


def get_string(data, seperator='\x00'):
    index = data.index(seperator) + 1
    string = data[:index].strip(seperator)
    return string, data[index:]


process_map = {
    'byte': get_byte,
    'byte_int': get_byte_int,
    'byte_chr': get_byte_chr,
    'byte_bool': get_byte_bool,
    'int': get_short,
    'short': get_short,
    'long': get_long,
    'float': get_longlong,
    'string': get_string,
}


class Unpacky(object):

    def __init__(self, pattern, data):
        self.pattern = pattern
        self.raw_data = data
        self.data, self.remaining_data = self.process(pattern, data)

    def generate_maps(self, pattern):
        map_types = []
        map_names = []
        pattern = re.sub("-", "{byte:_}", pattern)
        regex_matches = re.findall('{(\w+):(\w+)}', pattern)
        for _type, _name in regex_matches:
            map_types.append(_type)
            map_names.append(_name)
        return map_types, map_names

    def map_values(self, names, values):
        name_values = dict(zip(names, values))
        if '_' in name_values:
            del name_values['_']
        return name_values

    def process(self, pattern, raw_data):
        self.map_types, self.map_names = self.generate_maps(pattern)
        values = []

        remaining_data = raw_data
        for _type in self.map_types:
            value, remaining_data = process_map[_type](remaining_data)
            values.append(value)
        return self.map_values(self.map_names, values), remaining_data


if __name__ == '__main__':
    import binascii
    hex_data = "4911010101010101687474703a2f2f7777772e536169676e732e6465202833292052554e4f464600646d5f72756e6f666600686c326d70005465616d2044656174686d6174636800400119200c647700013330393435343200b0996907984c8df6174001736169676e732c5f726567697374657265642c73746174732c696e637265617365645f6d6178706c617965727300"
    data = binascii.unhexlify(hex_data)

    pattern = (
        "{byte:header}{byte_int:protocol}{string:name}{string:map}{string:folder}{string:game}"
        "{short:id}{byte_int:players}{byte_int:max_players}{byte_int:bots}"
        "{byte:server_type}{byte:environment}"
        "{byte_int:visibility}{byte_bool:vac}"
    )
    d = Decoder(pattern, data).data
    import pprint
    pprint.pprint(d)
