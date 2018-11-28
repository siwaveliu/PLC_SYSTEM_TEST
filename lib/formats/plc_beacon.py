"""
PLC Beacon Payload

"""

from construct import *
from construct.lib import *

beacon_item_type_enum = "beacon_item_type_enum" / Enum(Byte,
    STATION_CAPABILITY = 0,
    ROUTE_PARAM = 1,
    BAND_CHANGE = 2,
    SLOT_ALLOC = 0xC0,
    default = Pass
)

beacon_type_enum = "beacon_type_enum" / Enum(BitsInteger(3),
    DISCOVERY_BEACON = 0,
    PROXY_BEACON = 1,
    CENTRAL_BEACON = 2,
    default = Pass
)

sta_role_enum = "sta_role_enum" / Enum(BitsInteger(4),
    STA_ROLE_UNKNOWN = 0,
    STA_ROLE_STATION = 1,
    STA_ROLE_PCO = 2,
    STA_ROLE_CCO = 4,
    default = Pass
)


MacAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")],
    decoder = lambda obj,ctx: "-".join("%02X" % b for b in obj), )


station_capability_item = "station_capability_item" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "min_succ_rate" / BitsInteger(8),
        "proxy_tei" / BitsInteger(12),
        "sta_tei" / BitsInteger(12),
        )),
    "mac" / MacAddress,
    EmbeddedBitStruct(
        "level" / BitsInteger(4),
        "role" / sta_role_enum,
        ),
    "proxy_channel_quality" / Byte,
    EmbeddedBitStruct(
        Padding(6),
        "phase" / BitsInteger(2),
        )
)

route_param_item = "route_param_item" / Struct(
    "route_period" / Int16ul,
    "route_eva_remaining_time" / Int16ul,
    "pco_discovery_period" / Int16ul,
    "sta_discovery_period" / Int16ul,
)

band_change_item = "band_change_item" / Struct(
    "new_band" / Byte,
    "remaining_time" / Int32ul,
)

ncb_info_type = "ncb_info_type" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(3),
        "type" / BitsInteger(1),
        "tei" / BitsInteger(12),
        )),
)


csma_slot_info_type = "csma_slot_info_type" / Struct(
    "slot_len" / BytesInteger(3, swapped=True),
    EmbeddedBitStruct(
        Padding(6),
        "phase" / BitsInteger(2),
        ),
)

bind_csma_slot_info_type = "bind_csma_slot_info_type" / Struct(
    "slot_len" / BytesInteger(3, swapped=True),
    EmbeddedBitStruct(
        Padding(6),
        "phase" / BitsInteger(2),
        ),
)

slot_alloc_item = "slot_alloc_item" / Struct(
    "ncb_slot_num" / Byte,
    Embedded(BitStruct(
        Padding(2),
        "csma_phase_num" / BitsInteger(2),
        "cb_slot_num" / BitsInteger(4),
        )),
    Padding(1),
    "pb_slot_num" / Byte,
    "beacon_slot_len" / Byte,
    "csma_slot_slice_len" / Byte,
    "bind_csma_slot_phase_num" / Byte,
    "bind_csma_slot_lid" / Byte,
    "tdma_slot_len" / Byte,
    "tdma_slot_lid" / Byte,
    "beacon_period_start_time" / Int32ul,
    "beacon_period_len" / Int32ul,
    Padding(2),
    "ncb_info" / ncb_info_type[this.ncb_slot_num],
    "csma_slot_info" / csma_slot_info_type[this.csma_phase_num],
    "bind_csma_slot_info" / bind_csma_slot_info_type[this.bind_csma_slot_phase_num],
)

disc_beacon_slot_alloc_item = "disc_beacon_slot_alloc_item" / Struct(
    "ncb_slot_num" / Byte,
    Embedded(BitStruct(
        Padding(2),
        "csma_phase_num" / BitsInteger(2),
        "cb_slot_num" / BitsInteger(4),
        )),
    Padding(1),
    "pb_slot_num" / Byte,
    "beacon_slot_len" / Byte,
    "csma_slot_slice_len" / Byte,
    "bind_csma_slot_phase_num" / Byte,
    "bind_csma_slot_lid" / Byte,
    "tdma_slot_len" / Byte,
    "tdma_slot_lid" / Byte,
    "beacon_period_start_time" / Int32ul,
    "beacon_period_len" / Int32ul,
    Padding(2),
    "csma_slot_info" / csma_slot_info_type[this.csma_phase_num],
    "bind_csma_slot_info" / bind_csma_slot_info_type[this.bind_csma_slot_phase_num],
)

beacon_item_type = "beacon_item_type" / Struct(
    "head" / beacon_item_type_enum,
    "len" / Switch(this.head,
        {
            "STATION_CAPABILITY": Byte,
            "ROUTE_PARAM": Byte,
            "BAND_CHANGE": Byte,
            "SLOT_ALLOC": Int16ul,

        }
    ),
    "beacon_item" / Switch(this.head,
        {
            "STATION_CAPABILITY": station_capability_item,
            "ROUTE_PARAM": route_param_item,
            "BAND_CHANGE": band_change_item,
            "SLOT_ALLOC": slot_alloc_item,
        }
    )
)

disc_beacon_item_type = "disc_beacon_item_type" / Struct(
    "head" / beacon_item_type_enum,
    "len" / Switch(this.head,
        {
            "STATION_CAPABILITY": Byte,
            "ROUTE_PARAM": Byte,
            "BAND_CHANGE": Byte,
            "SLOT_ALLOC": Int16ul,

        }
    ),
    "beacon_item" / Switch(this.head,
        {
            "STATION_CAPABILITY": station_capability_item,
            "ROUTE_PARAM": route_param_item,
            "BAND_CHANGE": band_change_item,
            "SLOT_ALLOC": disc_beacon_slot_alloc_item,
        }
    )
)


beacon_info_type = "beacon_info_type" / Struct(
    "item_num" / Byte,
    "beacon_item_list" / beacon_item_type[this.item_num],
)

disc_beacon_info_type = "disc_beacon_info_type" / Struct(
    "item_num" / Byte,
    "beacon_item_list" / disc_beacon_item_type[this.item_num],
)


plc_beacon = "plc_beacon" / Struct(
    EmbeddedBitStruct(
        "beacon_use_flag" / BitsInteger(1),
        "association_start" / BitsInteger(1),
        Padding(2),
        "network_org_flag" / BitsInteger(1),
        "beacon_type" / beacon_type_enum
        ),
    "nw_sn" / Byte,
    "cco_mac_addr" / MacAddress,
    "beacon_period_counter" / Int32ul,
    Padding(8),
    "beacon_info" / IfThenElse(this.beacon_type != "DISCOVERY_BEACON", beacon_info_type, disc_beacon_info_type)
)

plc_beacon_crc = "plc_beacon_crc" / BytesInteger(4, swapped=True)

PLC_BEACON_CRC_SIZE = 4
