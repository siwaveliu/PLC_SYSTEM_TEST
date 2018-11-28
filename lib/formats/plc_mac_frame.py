"""
PLC MAC Frame

"""

from construct import *
from construct.lib import *
from plc_nmm import *
from plc_apl import *

MacAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")],
    decoder = lambda obj,ctx: "-".join("%02X" % b for b in obj), )


plc_msdu_type = "plc_msdu_type" / Enum(Byte,
    PLC_MSDU_TYPE_NMM = 0,
    PLC_MSDU_TYPE_APP = 48,
    PLC_MSDU_TYPE_IP = 49,
    default = Pass
)

plc_mac_frame_tx_type = "plc_mac_frame_tx_type" / Enum(BitsInteger(4),
    PLC_MAC_UNICAST = 0,
    PLC_MAC_ENTIRE_NW_BROADCAST = 1,
    PLC_LOCAL_BROADCAST = 2,
    PLC_MAC_PROXY_BROADCAST = 3,
    default = Pass
)

plc_mac_frame_head = "plc_mac_frame_head" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "org_src_tei" / BitsInteger(12),
        "ver" / BitsInteger(4),
    )),
    ByteSwapped(EmbeddedBitStruct(
        "tx_type" / plc_mac_frame_tx_type,
        "org_dst_tei" / BitsInteger(12),
    )),
    ByteSwapped(EmbeddedBitStruct(
        Padding(3),
        "tx_times_limit" / BitsInteger(5),  # tx_times_limit, in bit (0-4)
    )),
    "msdu_sn" / Int16ul,
    "msdu_type" / plc_msdu_type,
    ByteSwapped(EmbeddedBitStruct(
        "proxy_enabled" / BitsInteger(1),
        "reset_times" / BitsInteger(4),
        "msdu_len" / BitsInteger(11),
    )),
    ByteSwapped(EmbeddedBitStruct(
        "remaining_hop_count" / BitsInteger(4),
        "hop_limit" / BitsInteger(4),
    )),
    ByteSwapped(EmbeddedBitStruct(
        Padding(12),
        "mac_addr_flag" / BitsInteger(1),
        "route_fix_flag" / BitsInteger(1),
        "broadcast_dir" / BitsInteger(2),
    )),
    "nw_org_sn" / Int8ul,
    Padding(2),
    "src_mac_addr" / If(this.mac_addr_flag==1, MacAddress),
    "dst_mac_addr" / If(this.mac_addr_flag==1, MacAddress),
)

plc_mac_frame_crc = "plc_mac_frame_crc" / BytesInteger(4, swapped=True)

plc_mac_frame = "plc_mac_frame" / Struct(
    "head" / plc_mac_frame_head,
    "msdu" / RawCopy(Padded(this.head.msdu_len, Switch(this.head.msdu_type,
        {
            "PLC_MSDU_TYPE_NMM": plc_nmm,
            "PLC_MSDU_TYPE_APP": plc_apl,
        },
        default = Pass
    ))),
    "crc" / plc_mac_frame_crc
)

PLC_MAC_FRAME_CRC_SIZE = 4
PLC_SHORT_MAC_HEAD_SIZE = 16
PLC_LONG_MAC_HEAD_SIZE = 28