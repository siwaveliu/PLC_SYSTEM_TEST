import serial
import time
from formats import *
from construct import *
import binary_helper
import plc_tb_ctrl
import config

S = serial.Serial(config.FADDING_PORT)
cmd_send = '\x7e\x7e\x10\x00\x10'


Fadding_table = [
    '\x7e\x7e\x10\x00\x10','\x7e\x7e\x10\x01\x11','\x7e\x7e\x10\x02\x12','\x7e\x7e\x10\x03\x13',
    '\x7e\x7e\x10\x04\x14','\x7e\x7e\x10\x05\x15','\x7e\x7e\x10\x06\x16','\x7e\x7e\x10\x07\x17',
    '\x7e\x7e\x10\x08\x18','\x7e\x7e\x10\x09\x19','\x7e\x7e\x10\x0a\x1a','\x7e\x7e\x10\x0b\x1b',
    '\x7e\x7e\x10\x0c\x1c','\x7e\x7e\x10\x0d\x1d','\x7e\x7e\x10\x0e\x1e','\x7e\x7e\x10\x0f\x1f',
    '\x7e\x7e\x10\x10\x20','\x7e\x7e\x10\x11\x21','\x7e\x7e\x10\x12\x22','\x7e\x7e\x10\x13\x23',
    '\x7e\x7e\x10\x14\x24','\x7e\x7e\x10\x15\x25','\x7e\x7e\x10\x16\x26','\x7e\x7e\x10\x17\x27',
    '\x7e\x7e\x10\x18\x28','\x7e\x7e\x10\x19\x29','\x7e\x7e\x10\x1a\x2a','\x7e\x7e\x10\x1b\x2b',
    '\x7e\x7e\x10\x1c\x2c','\x7e\x7e\x10\x1d\x2d','\x7e\x7e\x10\x1e\x2e','\x7e\x7e\x10\x1f\x2f',
    '\x7e\x7e\x10\x20\x30','\x7e\x7e\x10\x21\x31','\x7e\x7e\x10\x22\x32','\x7e\x7e\x10\x23\x33',
    '\x7e\x7e\x10\x24\x34','\x7e\x7e\x10\x25\x35','\x7e\x7e\x10\x26\x36','\x7e\x7e\x10\x27\x37',
    '\x7e\x7e\x10\x28\x38','\x7e\x7e\x10\x29\x39','\x7e\x7e\x10\x2a\x3a','\x7e\x7e\x10\x2b\x3b',
    '\x7e\x7e\x10\x2c\x3c','\x7e\x7e\x10\x2d\x3d','\x7e\x7e\x10\x2e\x3e','\x7e\x7e\x10\x2f\x3f',
    '\x7e\x7e\x10\x30\x40','\x7e\x7e\x10\x31\x41','\x7e\x7e\x10\x32\x42','\x7e\x7e\x10\x33\x43',
    '\x7e\x7e\x10\x34\x44','\x7e\x7e\x10\x35\x45','\x7e\x7e\x10\x36\x46','\x7e\x7e\x10\x37\x47',
    '\x7e\x7e\x10\x38\x48','\x7e\x7e\x10\x39\x49','\x7e\x7e\x10\x3a\x4a','\x7e\x7e\x10\x3b\x4b',
    '\x7e\x7e\x10\x3c\x4c','\x7e\x7e\x10\x3d\x4d','\x7e\x7e\x10\x3e\x4e','\x7e\x7e\x10\x3f\x4f',
    '\x7e\x7e\x10\x40\x50','\x7e\x7e\x10\x41\x51','\x7e\x7e\x10\x42\x52','\x7e\x7e\x10\x43\x53',
    '\x7e\x7e\x10\x44\x54','\x7e\x7e\x10\x45\x55','\x7e\x7e\x10\x46\x56','\x7e\x7e\x10\x47\x57',
    '\x7e\x7e\x10\x48\x58','\x7e\x7e\x10\x49\x59','\x7e\x7e\x10\x4a\x5a','\x7e\x7e\x10\x4b\x5b',
    '\x7e\x7e\x10\x4c\x5c','\x7e\x7e\x10\x4d\x5d','\x7e\x7e\x10\x4e\x5e','\x7e\x7e\x10\x4f\x5f',
    '\x7e\x7e\x10\x50\x60','\x7e\x7e\x10\x51\x61','\x7e\x7e\x10\x52\x62','\x7e\x7e\x10\x53\x63',
    '\x7e\x7e\x10\x54\x64','\x7e\x7e\x10\x55\x65','\x7e\x7e\x10\x56\x66','\x7e\x7e\x10\x57\x67',
    '\x7e\x7e\x10\x58\x68','\x7e\x7e\x10\x59\x69','\x7e\x7e\x10\x5a\x6a','\x7e\x7e\x10\x5b\x6b',
    '\x7e\x7e\x10\x5c\x6c','\x7e\x7e\x10\x5d\x6d','\x7e\x7e\x10\x5e\x6e','\x7e\x7e\x10\x5f\x6f'
]

def set_fadding(fad_num):
    cmd_send = Fadding_table[fad_num]
    S.write(cmd_send)
