"""
PLC Network Management Message

"""

from construct import *
from construct.lib import *


#===============================================================================
# PLC MPDU FC
#===============================================================================

#########################################################################
# The followings are for some enum or sub structure definitions
#########################################################################
mm_type_enum_b16 = "mm_type_enum_b16" / Enum(Int16ul,
    MME_ASSOC_REQ                        = 0,
    MME_ASSOC_CNF                        = 1,
    MME_ASSOC_GATHER_IND                 = 2,
    MME_PROXY_CHANGE_REQ                 = 3,
    MME_PROXY_CHANGE_CNF                 = 4,
    MME_PROXY_CHANGE_BITMAP_CNF          = 5,
    MME_OFFLINE_IND                      = 6,
    MME_HEARTBEAT_REPORT                 = 7,
    MME_DISCOVER_NODE_LIST               = 8,
    MME_SUCC_RATE_REPORT                 = 9,
    MME_NW_CONFLICT_REPORT               = 0xA,
    MME_ZERO_CROSS_NTB_COLLECT_IND       = 0xB,
    MME_ZERO_CROSS_NTB_REPORT            = 0xC,
    MME_NW_DIAG_MSG                      = 0x4F,
    MME_ROUTE_REQ                        = 0x50,
    MME_ROUTE_REPLY                      = 0x51,
    MME_ROUTE_ERROR                      = 0x52,
    MME_ROUTE_ACK                        = 0x53,
    MME_LINK_CONFIRM_REQ                 = 0x54,
    MME_LINK_CONFIRM_RSP                 = 0x55,
#    default                              = Pass
)

nml_zero_cross_collect_type_enum_b8 = "nml_zero_cross_collect_type_enum_b8"     / Enum(Int8ul,
    ZERO_CROSS_COLLECT_TYPE_SINGLE       = 0,
    ZERO_CROSS_COLLECT_TYPE_ALL          = 1,
#    default                              = Pass
)

nml_zero_cross_collect_period_enum_b8 = "nml_zero_cross_collect_period_enum_b8" / Enum(Int8ul,
    ZERO_CROSS_COLLECT_PERIOD_HALF       = 0,
    ZERO_CROSS_COLLECT_PERIOD_ONE        = 1,
#    default                              = Pass
)

nml_phase_type_enum_b2 = "nml_phase_type_enum_b2"                               / Enum(BitsInteger(2),
    PHASE_ALL                            = 0,
    PHASE_UNKNOWN                        = 0,
    PHASE_A                              = 1,
    PHASE_B                              = 2,
    PHASE_C                              = 3,
#    default                              = Pass
)

nml_mac_addr_type_enum_b8 = "nml_mac_addr_type_enum_b8"                         / Enum(Int8ul,
    MAC_ADDR_TYPE_METER_ADDRESS          = 0,
    MAC_ADDR_TYPE_COMM_UNIT              = 1,
#    default                              = Pass
)

nml_device_type_enum_b8 = "nml_device_type_enum_b8"                              / Enum(Int8ul,
    DEV_TYPE_INVALID                     = 0,
    DEV_TYPE_HAND_READER                 = 1,
    DEV_TYPE_CCO                         = 2,
    DEV_TYPE_STA_SMART_METER             = 3,
    DEV_TYPE_REPEATER                    = 4,
    DEV_TYPE_STA_COLLECTOR_II            = 5,
    DEV_TYPE_STA_COLLECTOR_I             = 6,
#    default                              = Pass
)

nml_boot_cause_enum_b8 = "nml_boot_cause_enum_b8"                               / Enum(Int8ul,
    BC_NORMAL                            = 0,
    BC_HW_RESET                          = 1,
    BC_WATCH_DOG                         = 2,
    BC_EXCEPTION                         = 3,
#    default                              = Pass
)

nml_proxy_type_enum_b8 = "nml_proxy_type_enum_b8"                               / Enum(Int8ul,
    PROXY_TYPE_STATION_SELECTED          = 0,
#   default                              = Pass
)

nml_assoc_result_enum_b8 = "nml_assoc_result_enum_b8"                           / Enum(Int8ul,
    NML_ASSOCIATION_OK                   = 0,
    NML_ASSOCIATION_KO_NOT_IN_WL         = 1,
    NML_ASSOCIATION_KO_IN_BL             = 2,
    NML_ASSOCIATION_KO_TOO_MANY_STAS     = 3,
    NML_ASSOCIATION_KO_WL_IS_EMPTY       = 4,
    NML_ASSOCIATION_KO_TOO_MANY_PROXYS   = 5,
    NML_ASSOCIATION_KO_TOO_MANY_SUBSTAS  = 6,
    NML_ASSOCIATION_KO_RESERVED          = 7,
    NML_ASSOCIATION_KO_MAC_DUPLICATED    = 8,
    NML_ASSOCIATION_KO_LEVEL_OVERLIMIT   = 9,
    NML_ASSOCIATION_KO_RETRY_OK          = 10,
    NML_ASSOCIATION_KO_PROXY_IS_SUBSTAS  = 11,
    NML_ASSOCIATION_KO_RING_TOP_FOUND    = 12,
    NML_ASSOCIATION_KO_UNKNOW            = 13,
#    default                              = Pass
)

nml_assoc_gather_ind_result_enum_b8 = "nml_assoc_gather_ind_result_enum_b8"     / Enum(Int8ul,
    ASSOC_GATHER_IND_PERMIT              = 0,
#    default                              = Pass
)

nml_proxy_change_cnf_result_enum_b8 = "nml_proxy_change_cnf_result_enum_b8"     / Enum(Int8ul,
    PROXY_CHANGE_DONE                    = 0,
#    default                              = Pass
)

nml_proxy_change_reason_enum_b8 = "nml_proxy_change_reason_enum_b8"             / Enum(Int8ul,
    PROXY_CHANGE_UNKNOWN                 = 0,
    PROXY_CHANGE_PERIOD                  = 1,
#    default                              = Pass
)

nml_offline_reason_enum_b16 = "nml_offline_reason_enum_b16"                     / Enum(Int16ul,
    NML_NM_OFFLINE_REASON_CCO_REQUEST                 = 0,
    NML_NM_OFFLINE_REASON_LEVEL_OVERLIMIT             = 1,
    NML_NM_OFFLINE_REASON_NOT_IN_WHITELIST            = 2,
#    default                                           = Pass
)

nml_discover_role_type_enum_b4 = "nml_discover_role_type_enum_b4"               / Enum(BitsInteger(4),
    NML_ROLE_TYPE_UNKNOWN                = 0,
    NML_ROLE_TYPE_STATION                = 1,
    NML_ROLE_TYPE_PROXY                  = 2,
    NML_ROLE_TYPE_RESERVED               = 3,
    NML_ROLE_TYPE_CCO                    = 4,
#    default                              = Pass
)

nml_discover_route_type_enum_b4 = "nml_discover_route_type_enum_b4"             / Enum(BitsInteger(4),
    NML_INVALID_ROUTE_TYPE               = 0,
    NML_SAME_LEVEL_ROUTE_TYPE            = 1,
    NML_UPPER_LEVEL_ROUTE_TYPE           = 2,
    NML_PROXY_ROUTE_TYPE                 = 3,
    NML_UPPER_LEVEL2_ROUTE_TYPE          = 4,
#    default                              = Pass
)

nml_nw_diag_chip_vendor_id_enum_b16 = "nml_nw_diag_chip_vendor_id_enum_b16"     / Enum(Int16ul,
    VENDOR_RSVD                          = 0,
    VENDOR_HS                            = 1,
    VENDOR_ES                            = 2,
    VENDOR_TC                            = 3,
    VENDOR_LH                            = 4,
    VENDOR_HT                            = 5,
    VENDOR_RS                            = 6,
    VENDOR_SW                            = 7,
    VENDOR_SC                            = 8,
#    default                              = Pass
)

nml_preferred_route_flag_enum_b1 = "nml_preferred_route_flag_enum_b1"           / Enum(BitsInteger(1),
    NML_NOT_PREFERRED                    = 0,
    NML_PREFERRED                        = 1,
)

nml_payload_type_enum_b4 = "nml_payload_type_enum_b4"                           / Enum(BitsInteger(4),
    NML_NO_PAYLOAD                       = 0,
    NML_SPREAD_ROUTE_LIST                = 1,
#    default                              = Pass
)


MacAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")],
    decoder = lambda obj,ctx: "-".join("%02X" % b for b in obj), )

#########################################################################
# The followings are for frame header
#########################################################################

nmm_header = "nmm_header" / Struct(
    "mmtype"                       / mm_type_enum_b16,
    Padding(2)
)

#########################################################################
# The followings are for every single frame's construction
#########################################################################

# The followings are for MME_ASSOC_REQ
nmm_version_info = "nmm_version_info" / Struct(
    "boot_cause"                  / nml_boot_cause_enum_b8,
    "boot_ver"                    / Int8ul,
    "sw_ver"                      / Int16ul,
    ByteSwapped(EmbeddedBitStruct(
        "day"                     / BitsInteger(5),
        "month"                   / BitsInteger(4),
        "year"                    / BitsInteger(7),
    )),
    "vendor_id"                   / Int16ul,
    "chip_id"                     / Int16ul,
)

mme_assoc_req = "mme_assoc_req" / Struct(
    "mac"                         / MacAddress,
    "proxy_tei"                   / Int16ul[5],
    EmbeddedBitStruct(
        Padding(2),
        "phase_2"                 / nml_phase_type_enum_b2,
        "phase_1"                 / nml_phase_type_enum_b2,
        "phase_0"                 / nml_phase_type_enum_b2,
    ),
    "device_type"                 / nml_device_type_enum_b8,
    "mac_addr_type"               / nml_mac_addr_type_enum_b8,
    Padding(1),
    "rand_num"                    / Int32ul,
    "custom_ver_info"             / Byte[18],
    "version_info"                / nmm_version_info,
    "hw_reset_times"              / Int16ul,
    "sw_reset_times"              / Int16ul,
    "proxy_type"                  / nml_proxy_type_enum_b8,
    Padding(3),
    "p2p_sn"                      / Int32ul,
    "mng_id"                      / Byte[24],
)

# The followings are for MME_ASSOC_CNF
nmm_na_route_table_direct_proxy = "nmm_na_route_table_direct_proxy" / Struct(
    "tei"                         / Int16ul,
    "sub_sta_num"                 / Int16ul,
    "sub_sta_tei"                 / Int16ul[this.sub_sta_num],
)

nmm_na_route_table_info = "nmm_na_route_table_info" / Struct(
    "direct_station_num"          / Int16ul,
    "direct_proxy_num"            / Int16ul,
    "table_size"                  / Int16ul,
    Padding(2),
    "direct_sta_tei"              / Int16ul[this.direct_station_num],
    "direct_proxy_tei"            / nmm_na_route_table_direct_proxy[this.direct_proxy_num],
)

mme_assoc_cnf = "mme_assoc_cnf" / Struct(
    "mac_sta"                     / MacAddress,
    "mac_cco"                     / MacAddress,
    "result"                      / nml_assoc_result_enum_b8,
    "level"                       / Int8ul,
    "tei_sta"                     / Int16ul,
    "tei_proxy"                   / Int16ul,
    "frag_num"                    / Int8ul,
    "frag_sn"                     / Int8ul,
    "random_num"                  / Int32ul,
    "retry_times"                 / Int32ul,
    "p2p_sn"                      / Int32ul,
    "path_sn"                     / Int32ul,
    Padding(4),
    "info"                        / nmm_na_route_table_info
)

# The followings are for MME_ASSOC_GATHER_IND
nmm_gather_sta_info = "nmm_gather_sta_info" / Struct(
    "addr"                        / MacAddress,
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
)

mme_assoc_gather_ind = "mme_assoc_gather_ind" / Struct(
    "result"                      / nml_assoc_gather_ind_result_enum_b8,
    "level"                       / Int8ul,
    "mac_cco"                     / MacAddress,
    "proxy_tei"                   / Int16ul,        # tei:  in bit[0-11]
    Padding(1),
    "sta_num"                     / Int8ul,
    Padding(4),
    "sta_list"                    / nmm_gather_sta_info[this.sta_num],
)

# The followings are for MME_PROXY_CHANGE_REQ
mme_proxy_change_req = "mme_proxy_change_req" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "proxy_tei"                   / Int16ul[5],     # tei:  in bit[0-11] for every proxy
    "old_proxy"                   / Int16ul,        # tei:  in bit[0-11]
    "proxy_type"                  / nml_proxy_type_enum_b8,
    "reason"                      / nml_proxy_change_reason_enum_b8,
    "p2p_sn"                      / Int32ul,
    EmbeddedBitStruct(
        Padding(2),
        "phase_2"                 / nml_phase_type_enum_b2,
        "phase_1"                 / nml_phase_type_enum_b2,
        "phase_0"                 / nml_phase_type_enum_b2,
    ),
    Padding(3),
)

# The followings are for MME_PROXY_CHANGE_CNF
mme_proxy_change_cnf = "mme_proxy_change_cnf" / Struct(
    "result"                      / nml_proxy_change_cnf_result_enum_b8,
    "frag_num"                    / Int8ul,
    "frag_sn"                     / Int8ul,
    Padding(1),
    "sta_tei"                     / Int16ul,        # tei:  in bit[0-11]
    "proxy_tei"                   / Int16ul,        # tei:  in bit[0-11]
    "p2p_sn"                      / Int32ul,
    "path_sn"                     / Int32ul,
    "sta_num"                     / Int16ul,        # every STA's TEI ocupies 2 bytes in below sta list
    Padding(2),
    "sta_list"                    / Int16ul[this.sta_num],
)

# The followings are for MME_PROXY_CHANGE_BITMAP_CNF
mme_proxy_change_bitmap_cnf = "mme_proxy_change_bitmap_cnf" / Struct(
    "result"                      / nml_proxy_change_cnf_result_enum_b8,
    Padding(1),
    "bitmap_size"                 / Int16ul,        # unit: byte
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "proxy_tei"                   / Int16ul,        # tei:  in bit[0-11]
    "p2p_sn"                      / Int32ul,
    "path_sn"                     / Int32ul,
    Padding(4),
    "bitmap"                      / Byte[this.bitmap_size],
)

# The followings are for MME_OFFLINE_IND
mme_offline_ind = "mme_offline_ind" / Struct(
    "reason"                      / nml_offline_reason_enum_b16,
    "num"                         / Int16ul,
    "delay"                       / Int16ul,
    Padding(10),
    "mac"                         / MacAddress[this.num],
)

# The followings are for MME_HEARTBEAT_REPORT
mme_heartbeat_report = "mme_heartbeat_report" / Struct(
    "org_src_tei"                 / Int16ul,        # tei:  in bit[0-11]
    "good_ear_tei"                / Int16ul,        # tei:  in bit[0-11]
    "sta_num"                     / Int16ul,
    "bit_map_len"                 / Int16ul,        # unit: Byte
    "bitmap"                      / Byte[this.bit_map_len],
)

# The followings are for MME_DISCOVER_NODE_LIST
nmm_route_item =  "nmm_route_item" / Struct(
    EmbeddedBitStruct(
        "route_type"              / nml_discover_route_type_enum_b4, # route_type:  in bit[12-15]
        "next_hop_tei"            / BitsInteger(12),                 # tei:         in bit[0-11]
    ),
)

mme_discover_node_list = "mme_discover_node_list" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "level"                   / BitsInteger(4),                  # level:       in bit[28-32]
        "role"                    / nml_discover_role_type_enum_b4,  # role:        in bit[24-27]
        "proxy_tei"               / BitsInteger(12),                 # proxy_tei:   in bit[12-23]
        "tei"                     / BitsInteger(12),                 # tei:         in bit[0-11]
    )),
    "sta_mac_addr"                / MacAddress,
    "cco_mac_addr"                / MacAddress,
    EmbeddedBitStruct(
        Padding(2),
        "phase_3"                 / nml_phase_type_enum_b2, # phase 1~3:       in bit[0-5]
        "phase_2"                 / nml_phase_type_enum_b2,
        "phase_1"                 / nml_phase_type_enum_b2,
    ),
    "pco_chan_quality"            / Int8ul,
    "pco_succ_rate"               / Int8ul,
    "pco_dl_succ_rate"            / Int8ul,
    "station_num"                 / Int16ul,
    "sent_dnl_msg_num"            / Int8ul,
    "ul_route_item_num"           / Int8ul,         # every item with 16 bits
    "route_period_remaining_time" / Int16ul,
    "bitmap_size"                 / Int16ul,        # unit: Byte
    "min_succ_rate"               / Int8ul,
    Padding(3),
    "ul_route_item_list"          / nmm_route_item[this.ul_route_item_num],
    "bitmap"                      / Byte[this.bitmap_size],
    "recv_discover_node_list"     / Byte[this.station_num],
)

# The followings are for MME_SUCC_RATE_REPORT
nmm_comm_succ_rate =  "nmm_comm_succ_rate" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "dl_rate"                     / Int8ul,
    "ul_rate"                     / Int8ul,
)

mme_succ_rate_report = "mme_succ_rate_report" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "num"                         / Int16ul,
    "info"                        / nmm_comm_succ_rate[this.num],
)

# The followings are for MME_NW_CONFLICT_REPORT
mme_nw_conflict_report = "mme_nw_conflict_report" / Struct(
    "cco_mac"                     / MacAddress,
    "num"                         / Int8ul,
    "nid_size"                    / Int8ul,
    "nids"                        / BytesInteger(this.nid_size, swapped=True)[this.num],
)

# The followings are for MME_ZERO_CROSS_NTB_COLLECT_IND

mme_zero_cross_ntb_collect_ind = "mme_zero_cross_ntb_collect_ind" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "type"                        / nml_zero_cross_collect_type_enum_b8,
    "period"                      / nml_zero_cross_collect_period_enum_b8,
    "num"                         / Int8ul,
    Padding(3),
)

# The followings are for MME_ZERO_CROSS_NTB_REPORT
offset_pair = "offset_pair" / ByteSwapped(BitStruct(
    "even"                        / BitsInteger(12),
    "odd"                         / BitsInteger(12),
))

offset_tail = "offset_tail" / ByteSwapped(BitStruct(
    Padding(4),
    "odd"                         / BitsInteger(12),
))

mme_zero_cross_ntb_report = "mme_zero_cross_ntb_report" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "num"                         / Int8ul,
    "phase1_num"                  / Int8ul,
    "phase2_num"                  / Int8ul,
    "phase3_num"                  / Int8ul,
    "ntb"                         / Int32ul,
    "offset"                      / If ((this.phase1_num + this.phase2_num + this.phase3_num) > 1, offset_pair[(this.phase1_num + this.phase2_num + this.phase3_num) >> 1]),
    "offset_last"                 / If (((this.phase1_num + this.phase2_num + this.phase3_num) & 1) == 1, offset_tail),
)

# The followings are for MME_NW_DIAG_MSG
mme_nw_diag_msg = "mme_nw_diag_msg" / Struct(
    "chip_id"                     / nml_nw_diag_chip_vendor_id_enum_b16,
    "custom"                      / Byte[16],       # this is vendor customized field, no unified format, temporarily defined as 16 bytes.
)

# The followings are for MME_ROUTE_REQ
nmm_route_sta_info = "nmm_route_sta_info" / Struct(
    "tei"                         / Int16ul,        # tei:  in bit[0-11]
    "comm_succ_rate"              / Int8ul,
    "quality"                     / Int8ul,
)

mme_route_req = "mme_route_req" / Struct(
    "ver"                         / Int8ul,
    "sn"                          / Int32ul,
    EmbeddedBitStruct(
        "payload_type"            / nml_payload_type_enum_b4,           # payload type,      in bit[4-7]
        "route_prefer_flag"       / nml_preferred_route_flag_enum_b1,   # route prefer flag, in bit[3]
        Padding(3),
    ),
    "payload_len"                 / Int8ul,         # every sta information ocupies 4 bytes in below
    #it should be data length but not item number
    "data"                        / nmm_route_sta_info[this.payload_len/4],
)

# The followings are for MME_ROUTE_REPLY
mme_route_reply = "mme_route_reply" / Struct(
    "ver"                         / Int8ul,
    "sn"                          / Int32ul,
    EmbeddedBitStruct(
        "payload_type"            / nml_payload_type_enum_b4,           # payload type,      in bit[4-7]
        Padding(4),
    ),
    "payload_len"                 / Int8ul,         # every STA information ocupies 4 bytes in below
    "data"                        / nmm_route_sta_info[this.payload_len/4],
                                                    # <- the same structure with that in "MME_ROUTE_REQ"
)

# The followings are for MME_ROUTE_ERROR
mme_route_error = "mme_route_error" / Struct(
    "ver"                         / Int8ul,
    "sn"                          / Int32ul,
    Padding(1),
    "unreachable_sta_num"         / Int8ul,         # every STA's TEI ocupies 2 bytes in below list
    "unreachable_sta_list"        / Int16ul[this.unreachable_sta_num],
)

# The followings are for MME_ROUTE_ACK
mme_route_ack = "mme_route_ack" / Struct(
    "ver"                         / Int8ul,
    Padding(3),
    "sn"                          / Int32ul,
)

# The followings are for MME_LINK_CONFIRM_REQ
mme_link_confirm_req = "mme_link_confirm_req" / Struct(
    "ver"                         / Int8ul,
    "sn"                          / Int32ul,
    Padding(1),
    "confirm_sta_num"             / Int8ul,         # every STA's TEI ocupies 2 bytes in below list
    "confirm_sta_list"            / Int16ul[this.confirm_sta_num],
)

# The followings are for MME_LINK_CONFIRM_RSP
mme_link_confirm_rsp = "mme_link_confirm_rsp" / Struct(
    "ver"                         / Int8ul,
    "level"                       / Int8ul,
    "quality"                     / Int8ul,
    EmbeddedBitStruct(
        Padding(7),
        "route_prefer_flag"       / nml_preferred_route_flag_enum_b1, # route prefer flag,  in bit[0]
    ),
    "sn"                          / Int32ul,
)

#########################################################################
# The followings are for the whole PLC NMM frames construction
#########################################################################
plc_nmm = "plc_nmm" / Struct(
    "header" / nmm_header,
    "body" / Switch(this.header.mmtype,
        {
            "MME_ASSOC_REQ" : mme_assoc_req,
            "MME_ASSOC_CNF" : mme_assoc_cnf,

            "MME_ASSOC_GATHER_IND"           : mme_assoc_gather_ind,
            "MME_PROXY_CHANGE_REQ"           : mme_proxy_change_req,
            "MME_PROXY_CHANGE_CNF"           : mme_proxy_change_cnf,
            "MME_PROXY_CHANGE_BITMAP_CNF"    : mme_proxy_change_bitmap_cnf,
            "MME_OFFLINE_IND"                : mme_offline_ind,
            "MME_HEARTBEAT_REPORT"           : mme_heartbeat_report,
            "MME_DISCOVER_NODE_LIST"         : mme_discover_node_list,
            "MME_SUCC_RATE_REPORT"           : mme_succ_rate_report,
            "MME_NW_CONFLICT_REPORT"         : mme_nw_conflict_report,
            "MME_ZERO_CROSS_NTB_COLLECT_IND" : mme_zero_cross_ntb_collect_ind,
            "MME_ZERO_CROSS_NTB_REPORT"      : mme_zero_cross_ntb_report,

            "MME_NW_DIAG_MSG"         : mme_nw_diag_msg,
            "MME_ROUTE_REQ"           : mme_route_req,
            "MME_ROUTE_REPLY"         : mme_route_reply,
            "MME_ROUTE_ERROR"         : mme_route_error,
            "MME_ROUTE_ACK"           : mme_route_ack,
            "MME_LINK_CONFIRM_REQ"    : mme_link_confirm_req,
            "MME_LINK_CONFIRM_RSP"    : mme_link_confirm_rsp,
        },
        default = Pass
    ),
)
