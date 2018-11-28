"""
PLC MPDU

"""

from construct import *
from construct.lib import *


#===============================================================================
# PLC MPDU FC
#===============================================================================

plc_mpdu_type_enum = "plc_mpdu_type_enum" / Enum(BitsInteger(3),
    PLC_MPDU_BEACON = 0,
    PLC_MPDU_SOF = 1,
    PLC_MPDU_SACK = 2,
    PLC_MPDU_NCF = 3,
    default = Pass
)

plc_sof_var_region_ver = "plc_sof_var_region_ver" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "lid" / BitsInteger(8),
        "dst_tei" / BitsInteger(12),
        "src_tei" / BitsInteger(12),
        )),
    ByteSwapped(EmbeddedBitStruct(
        "pb_num" / BitsInteger(4),
        "frame_len" / BitsInteger(12),
        )),
    ByteSwapped(EmbeddedBitStruct(
        "tmi_b" / BitsInteger(4),
        "encrypt_flag" / BitsInteger(1),
        "retrans_flag" / BitsInteger(1),
        "broadcast_flag" / BitsInteger(1),
        "symbol_num" / BitsInteger(9),
        )),
    EmbeddedBitStruct(
        "ver" / BitsInteger(4),
        "tmi_e" / BitsInteger(4),
        ),
)

plc_beacon_var_region_ver = "plc_beacon_var_region_ver" / Struct(
    "timestamp" / Int32ul,
    ByteSwapped(EmbeddedBitStruct(
        "tmi" / BitsInteger(4),
        "src_tei" / BitsInteger(12),
    )),
    ByteSwapped(EmbeddedBitStruct(
        Padding(5),
        "phase" / BitsInteger(2),
        "sym_num" / BitsInteger(9),
    )),
    EmbeddedBitStruct(
        "ver" / BitsInteger(4),
        Padding(4),
    ),
)

plc_ncf_var_region_ver = "plc_ncf_var_region_ver" / Struct(
    "duration" / Int16ul,
    "offset" / Int16ul,
    ByteSwapped(EmbeddedBitStruct(
        Padding(8),
        "neigh_nid" / BitsInteger(24)
    )),
    EmbeddedBitStruct(
        "ver" / BitsInteger(4),
        Padding(4),
    ),
)

plc_sack_var_region_ver = "plc_sack_var_region_ver" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "dst_tei" / BitsInteger(12),
        "src_tei" / BitsInteger(12),
        "rx_status" / BitsInteger(4),
        "rx_result" / BitsInteger(4)
    )),
    EmbeddedBitStruct(
        Padding(5),
        "rx_pb_num" / BitsInteger(3),
    ),
    "chan_quality" / Byte,
    "load" / Byte,
    Padding(1),
    EmbeddedBitStruct(
        "ext_frame_type" / BitsInteger(4),
        "ver" / BitsInteger(4),
    ),
)


plc_mpdu_fc = "plc_mpdu_fc" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "nid" / BitsInteger(24),
        "network_type" / BitsInteger(5),
        "mpdu_type" / plc_mpdu_type_enum,
        )),
    "var_region_ver" / Switch(this.mpdu_type,
        {
            "PLC_MPDU_SOF" : plc_sof_var_region_ver,
            "PLC_MPDU_BEACON" : plc_beacon_var_region_ver,
            "PLC_MPDU_NCF" : plc_ncf_var_region_ver,
            "PLC_MPDU_SACK" : plc_sack_var_region_ver,
        },
        default = Pass
    ),
    "crc" / BytesInteger(3, swapped=True)
)

plc_sof_pb_head = "plc_sof_pb_head" / BitStruct(
        "end_flag" / BitsInteger(1),
        "start_flag" / BitsInteger(1),
        "sn" / BitsInteger(6),
)

plc_pb_crc = "plc_pb_crc" / BytesInteger(3, swapped=True)

plc_sof_pb520 = "plc_mpdu_pb520" / Struct(
    "head" / plc_sof_pb_head,
    "payload" / Byte[516],
    "crc" / plc_pb_crc
)

plc_sof_pb264 = "plc_sof_pb264" / Struct(
    "head" / plc_sof_pb_head,
    "payload" / Byte[260],
    "crc" / plc_pb_crc
)

plc_sof_pb136 = "plc_sof_pb136" / Struct(
    "head" / plc_sof_pb_head,
    "payload" / Byte[132],
    "crc" / plc_pb_crc
)

plc_sof_pb72 = "plc_sof_pb72" / Struct(
    "head" / plc_sof_pb_head,
    "payload" / Byte[68],
    "crc" / plc_pb_crc
)

PLC_SOF_PB_HEAD_SIZE = plc_sof_pb_head.sizeof()

PLC_PB_CRC_SIZE = 3