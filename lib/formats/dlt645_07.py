# -- coding: utf-8 --

"""
DLT645 frame

"""

from construct import *
from construct.lib import *

MtrAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")][::-1],
    decoder = lambda obj,ctx: "-".join("%02x" % b for b in obj[::-1]),
)

code_enum_b5 = "code_enum_b5" / Enum(BitsInteger(5),
                           TIME_CAL=0x08, #广播校时
                           DATA_READ=0x11, #读数据
                           DATA_READ_MORE=0x12, #读后续数据
                           ADDR_READ=0x13, #读通信地址
                           DATA_WRITE=0x14, #写数据
                           ADDR_WRITE=0x15, #写通信地址
                           default=Pass
)


frame_dir_enum_b1 = "frame_dir_enum_b1" / Enum(BitsInteger(1),
                           REQ_FRAME=0, #请求
                           REPLY_FRAME=1, #响应
)

reply_type_enum_b1 = "reply_type_enum_b1" / Enum(BitsInteger(1),
                           NORMAL_REPLY=0, #正确应答
                           ABNORMAL_REPLY=1, #异常应答
)

more_data_flag_enum_b1 = "more_data_flag_enum_b1" / Enum(BitsInteger(1),
                           NO_MORE_DATA=0, #无后续数据
                           MORE_DATA=1, #有后续数据
)

dlt645_07_head = "dlt645_07_head" / Struct(
    "start_char1" /              Const(b"\x68"),
    "addr" / MtrAddress,
    "start_char2" / Const(b"\x68"),
    EmbeddedBitStruct(
        "dir" / frame_dir_enum_b1,
        "reply_flag" / IfThenElse(this.dir=="REPLY_FRAME", reply_type_enum_b1, Padding(1)),
        "more_flag" / IfThenElse(this.dir=="REPLY_FRAME", more_data_flag_enum_b1, Padding(1)),
        "code" / code_enum_b5,
        ),
    "len" / Int8ul
)

dlt645_07_tail = "dlt645_07_tail" / Struct(
    "cs" / Int8ul,
    "end_char" / Const(b"\x16")
)

time_cal = "time_cal" / Struct(
    "ss" / Int8ul,
    "mm" / Int8ul,
    "hh" / Int8ul,
    "DD" / Int8ul,
    "MM" / Int8ul,
    "YY" / Int8ul
)

data_read_req_format1 = "data_read_req_format1" / Struct(
    "DI0" / Int8ul,
    "DI1" / Int8ul,
    "DI2" / Int8ul,
    "DI3" / Int8ul,
)

data_read_req_format2 = "data_read_req_format2" / Struct(
    "DI0" / Int8ul,
    "DI1" / Int8ul,
    "DI2" / Int8ul,
    "DI3" / Int8ul,
    "N" / Int8ul,
)

data_read_req_format3 = "data_read_req_format3" / Struct(
    "DI0" / Int8ul,
    "DI1" / Int8ul,
    "DI2" / Int8ul,
    "DI3" / Int8ul,
    "N" / Int8ul,
    "mm" / Int8ul,
    "hh" / Int8ul,
    "DD" / Int8ul,
    "MM" / Int8ul,
    "YY" / Int8ul
)

data_read_normal_reply = "data_read_normal_reply" / Struct(
    "DI0" / Int8ul,
    "DI1" / Int8ul,
    "DI2" / Int8ul,
    "DI3" / Int8ul,
    "data" / Byte[this._.head.len-4],
)

data_read_error_reply = "data_read_error_reply" / Struct(
    "err" / Int8ul,
)

addr_read_req = "addr_read_req" / Struct(
)

addr_read_reply = "addr_read_reply" / Struct(
    "addr" / MtrAddress,
)

dlt645_07 = "dlt645_07" / Struct(
    "head" / dlt645_07_head,
    "body" / RawCopy(Switch(this.head.code,
        {
            "TIME_CAL" : time_cal,
            "DATA_READ": Switch(this.head.dir,
                {
                    "REQ_FRAME": Switch(this.head.len,
                        {
                            4: data_read_req_format1,
                            5: data_read_req_format2,
                            10: data_read_req_format3,
                        },
                        default = Pass,
                    ),
                    "REPLY_FRAME": Switch(this.head.reply_flag,
                        {
                            "NORMAL_REPLY": data_read_normal_reply,
                            "ABNORMAL_REPLY": data_read_error_reply
                        },
                    ),
                },
            ),
            "ADDR_READ": Switch(this.head.dir,
                {
                    "REQ_FRAME": addr_read_req,
                    "REPLY_FRAME": addr_read_reply
                },
            )
        },
    )),
    "tail" / dlt645_07_tail,
)