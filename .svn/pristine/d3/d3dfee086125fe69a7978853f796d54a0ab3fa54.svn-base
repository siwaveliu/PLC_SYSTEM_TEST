# -*- coding: UTF-8 -*-

"""
PLC Application Layer Message

"""

from construct import *
from construct.lib import *

#===============================================================================
# PLC MPDU FC
#===============================================================================

#########################################################################
# The followings are for some enum or sub structure definitions
#########################################################################

apl_packet_id_enum_b12 = "apl_packet_id_enum_b12"           / Enum(BitsInteger(12),
    APL_CCT_METER_READ      = 0x0001,
    APL_ROUTE_METER_READ    = 0x0002,
    APL_CCT_SIMU_METER_READ = 0x0003,
    APL_TIME_CALI           = 0x0004,
    APL_COMM_TEST           = 0x0006,
    APL_EVENT_REPORT        = 0x0008,
    APL_NODE_REG_QUERY      = 0x0011,
    APL_NODE_REG_START      = 0x0012,
    APL_NODE_REG_STOP       = 0x0013,
    APL_ACK_NACK            = 0x0020,
    APL_DATA_COLLECT        = 0x0021,
    APL_UPGRADE_START       = 0x0030,
    APL_UPGRADE_STOP        = 0x0031,
    APL_DATA_TRANSFER       = 0x0032,
    APL_DATA_TRANSFER_BC    = 0x0033,
    APL_UPGRADE_STATE_QUERY = 0x0034,
    APL_UPGRADE_EXEC        = 0x0035,
    APL_STATE_INFO_QUERY    = 0x0036,
    APL_SECURITY            = 0x00A0,

#    default                 = Pass
)

apl_proto_ver_enum_b6 = "apl_proto_ver_enum_b6"             / Enum (BitsInteger(6),
    PROTO_VER1                  = 1,
#    default                     = Pass
)

apl_dir_bit_enum_b1 = "apl_dir_bit_enum_b1"                 / Enum (BitsInteger(1),
    DL                          = 0,
    UL                          = 1,
)

apl_data_proto_type_enum_b4 = "apl_data_proto_type_enum_b4" / Enum (BitsInteger(4),  # 4 bits, used in METER READ
    PROTO_TRANSPARENCE          = 0,
    PROTO_DLT645_1997           = 1,
    PROTO_DLT645_2007           = 2,
    PROTO_DLT698_45             = 3,
#    default                     = Pass
)

apl_data_proto_type_enum_b8 = "apl_data_proto_type_enum_b8" / Enum (Int8ul,          # 8 bits, used in APL_NODE_REG_QUERY ul
    PROTO_TRANSPARENCE          = 0,
    PROTO_DLT645_1997           = 1,
    PROTO_DLT645_2007           = 2,
    PROTO_DLT698_45             = 3,
#    default                     = Pass
)

apl_retry_enum_b1 = "apl_retry_enum_b1"                     / Enum (BitsInteger(1),
    NO_RETRY                    = 0,
    RETRY                       = 1,
)

apl_rsp_status_enum_b4 = "apl_rsp_status_enum_b4"           / Enum (BitsInteger(4),
    NORMAL_ACK                  = 0,
#    default                     = Pass
)

apl_reg_para_enum_b3 = "apl_reg_para_enum_b3"               / Enum (BitsInteger(3),
    QUERY_REG_RESULT            = 0,
    START_REG                   = 1,
#    default                     = Pass
)


apl_must_answer_enum_b1 = "apl_must_answer_enum_b1"         / Enum (BitsInteger(1),
    NOT_MUST_ANSWER             = 0,
    MUST_ANSWER                 = 1,
)

apl_dev_type_enum_b8 = "apl_dev_type_enum_b8"               / Enum (Int8ul,           # 8 bits, used for DEV TYPE, in APL_NODE_REG_QUERY ul
    PRODUCT_TYPE_METER          = 0,
    PRODUCT_TYPE_COLLECTOR_I    = 1,
    PRODUCT_TYPE_COLLECTOR_II   = 2,
#    default                     = Pass
)

apl_module_type_enum_b4 = "apl_module_type_enum_b4"         / Enum (BitsInteger(4),   # 4 bits, used for MODULE TYPE, in APL_NODE_REG_QUERY ul
    PRODUCT_TYPE_METER          = 0,
    PRODUCT_TYPE_COLLECTOR_I    = 1,
    PRODUCT_TYPE_COLLECTOR_II   = 2,
#    default                     = Pass
)

apl_prm_enum_b1 = "apl_prm_enum_b1"                         / Enum (BitsInteger(1),
    SLAVE                       = 0,             # 从动站
    MASTER                      = 1,             # 启动站
)

apl_event_report_enum_b6 = "apl_event_report_enum_b6"       / Enum (BitsInteger(6),
    EVENT_CODE_ACK              = 1,
    EVENT_CODE_REPORT           = 1,
    EVENT_CODE_ENABLE_REPORT    = 2,
    EVENT_CODE_DISABLE_REPORT   = 3,
    EVENT_CODE_EVENT_BUFF_FULL  = 4,
#    default                     = Pass
)

apl_ack_enum_b1 = "apl_ack_enum_b1"                         / Enum (BitsInteger(1),
    DENY                        = 0,              # 否认
    ACCEPT                      = 1,              # 确认
)

apl_upg_block_size_enum_b16 = "apl_upg_block_size_enum_b16" / Enum (Int16ul,
    UPG_BLK_SZ_1                = 100,
    UPG_BLK_SZ_2                = 200,
    UPG_BLK_SZ_3                = 300,
    UPG_BLK_SZ_4                = 400,
#    default                     = Pass
)

apl_upg_dev_type_enum_b8 = "apl_upg_dev_type_enum_b8"       / Enum (Int8ul,
    UPG_VENDOR_ID               = 0,
    UPG_VERSION_INFO            = 1,
    UPG_BOOT_INFO               = 2,
    UPG_CRC32                   = 3,
    UPG_FILE_SIZE               = 4,
    UPG_DEV_TYPE                = 5,
#    default                     = Pass
)

apl_upg_state_enum_b4 = "apl_upg_state_enum_b4"             / Enum (BitsInteger(4),
    UPG_STATE_IDLE              = 0,
    UPG_STATE_RECEIVING         = 1,
    UPG_STATE_RX_COMPLETE       = 2,
    UPG_STATE_UPGRADING         = 3,
    UPG_STATE_TRY_RUNNING       = 4,
#    default                     = Pass
)

apl_test_mode_cmd_enum_b4 = "apl_test_mode_enum_b4" / Enum (BitsInteger(4),  # 4 bits, used in METER READ
    ENTER_NON_TEST_MODE          = 0,
    ENTER_APL_UART_FWD_MODE      = 1,
    ENTER_APL_PLC_FWD_MODE       = 2,
    ENTER_PHY_TRANS_MODE         = 3,
    ENTER_PHY_LOOPBACK_MODE      = 4,
    ENTER_MAC_TRANS_MODE         = 5,
    CONFIG_BAND                  = 6,
    CONFIG_TONEMASK              = 7,
#    default                     = Pass
)

# big-endian
MacAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")],
    decoder = lambda obj,ctx: "-".join("%02X" % b for b in obj), )

# little-endian
BcdAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")][::-1],
    decoder = lambda obj,ctx: "-".join("%02x" % b for b in obj[::-1]),
)


#########################################################################
# The followings are for frame header
#########################################################################
apl_header = "apl_header" / Struct(
    "port"                / Int8ul,
    ByteSwapped(EmbeddedBitStruct(
        "sec_mode"        / BitsInteger(4),
        "id"              / apl_packet_id_enum_b12,
    )),
    "ctrl_word"           / Int8ul
)

#########################################################################
# The followings are for every single frame's construction
#########################################################################


# The followings are for APL_CCT_METER_READ and APL_DATA_COLLECT
meter_read_dl = "meter_read_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "data_len"        / BitsInteger(12),
        "data_proto_type" / apl_data_proto_type_enum_b4,
        "cfg_word"        / BitsInteger(4),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    "exp_time"            / Int8ul,
    EmbeddedBitStruct(                         # "option_word" / Int8ul,
        Padding(7),
        "dir_bit"         / apl_dir_bit_enum_b1,# dir_bit, in bit 0
    ),
    "data"                / Byte[this.data_len]
)

meter_read_ul = "meter_read_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "data_len"        / BitsInteger(12),
        "data_proto_type" / apl_data_proto_type_enum_b4,
        "rsp_status"      / apl_rsp_status_enum_b4,
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    ByteSwapped(EmbeddedBitStruct(                         # "option_word" / Int16ul,
        Padding(7),
        "dir_bit"         / apl_dir_bit_enum_b1,# dir_bit, in BYTE1, bit 0. Value 0=dl, 1=ul
        Padding(8),
    )),
    "data"                / Byte[this.data_len]
)

# The followings are for APL_CCT_SIMU_METER_READ and APL_ROUTE_METER_READ
meter_simu_read_dl = "meter_simu_read_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "data_len"        / BitsInteger(12),
        "data_proto_type" / apl_data_proto_type_enum_b4,
        "retry_num"       / BitsInteger(2),    #   "cfg_word" / BitsInteger(4),
        "nack_retry"      / apl_retry_enum_b1,  #   "cfg_word"
        "no_rsp_retry"    / apl_retry_enum_b1,  #   "cfg_word"
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    "exp_time"            / Int8ul,            #   unit: 100ms
    "pkt_interval"        / Int8ul,
    "data"                / Byte[this.data_len]
)

# The followings are for APL_CCT_SIMU_METER_READ only
meter_simu_read_ul = "meter_simu_read_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "data_len"        / BitsInteger(12),
        "data_proto_type" / apl_data_proto_type_enum_b4,
        "rsp_status"      / apl_rsp_status_enum_b4,
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    "pkt_rsp_status"      / Int16ul,           # "option_word" / Int16ul,
    "data"                / Byte[this.data_len]
)

# The followings are for APL_DATA_COLLECT only
meter_data_collect_ul = "meter_data_collect_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "data_len"        / BitsInteger(12),
        "data_proto_type" / apl_data_proto_type_enum_b4,
        "rsp_status"      / apl_rsp_status_enum_b4,
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    ByteSwapped(EmbeddedBitStruct(             # "option_word" / Int16ul,
        Padding(8),
        "ul_id"           / BitsInteger(8),    # upload id, in bit 0-7
    )),
    "data"                / Byte[this.data_len]
)

# The followings are for APL_NODE_REG_START (downstream only, no upstream)
node_reg_start_dl = "node_reg_start_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "reg_para"        / Const('START_REG',apl_reg_para_enum_b3),
        "must_answer"     / Const('NOT_MUST_ANSWER',apl_must_answer_enum_b1),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    Padding(2),
    "sn"                  / Int32ul,
)

# The followings are for APL_NODE_REG_QUERY
node_reg_query_dl = "node_reg_query_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "reg_para"        / Const('QUERY_REG_RESULT',apl_reg_para_enum_b3),
        "must_answer"     / apl_must_answer_enum_b1,
        "hdr_len"         / Const(20,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    Padding(2),
    "sn"                  / Int32ul,
    "src_mac"             / MacAddress,
    "dst_mac"             / MacAddress,
)

sub_node_info = "sub_node_info" / Struct(
    "addr"                / BcdAddress,
    "prot_type"           / apl_data_proto_type_enum_b8,
    EmbeddedBitStruct(
        Padding(4),
        "module_type"     / apl_module_type_enum_b4,  # module_type, in bit 0-3
    ),
)

node_reg_query_ul = "node_reg_query_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "reg_para"        / apl_reg_para_enum_b3,
        "status"          / BitsInteger(1),
        "hdr_len"         / Const(36,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "meter_num"           / Int8ul,
    "dev_type"            / apl_dev_type_enum_b8,
    "dev_addr"            / BcdAddress,
    "dev_id"              / MacAddress,
    "sn"                  / Int32ul,
    Padding(4),
    "src_mac"             / MacAddress,
    "dst_mac"             / MacAddress,
    "info"                / sub_node_info[this.meter_num],
)

# The followings are for APL_NODE_REG_STOP (downstream only, no upstream)
node_reg_stop_dl = "node_reg_stop_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(4),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    Padding(2),
    "sn"                  / Int32ul,
)

# The followings are for APL_TIME_CALI (downstream only, no upstream)
time_cali_dl = "time_cali_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "length"          / BitsInteger(12),
        Padding(4),
        Padding(4),
        "hdr_len"         / Const(4,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "data"                / Byte[this.length],
)

# The followings are for APL_EVENT_REPORT (downstream and upstream are the same)
event_report_dl = "event_report_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "length"          / BitsInteger(12),
        "op_code"         / apl_event_report_enum_b6,
        "prm"             / apl_prm_enum_b1,
        "direction"       / apl_dir_bit_enum_b1,
        "hdr_len"         / Const(12,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    "addr"                / MacAddress,
    "data"                / Byte[this.length],
)

event_report_ul = event_report_dl

# The followings are for APL_COMM_TEST (downstream only, no upstream)
comm_test_dl = "comm_test_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "length"          / BitsInteger(12),
        "prot_type"       / apl_data_proto_type_enum_b4,
        "test_mode_cmd"   / apl_test_mode_cmd_enum_b4,
        "hdr_len"         / Const(4,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "data"                / If(this.test_mode_cmd == 'ENTER_NON_TEST_MODE', Byte[this.length])
)

# The followings are for APL_ACK_NACK (downstream and upstream are the same)
ack_nack_dl = "ack_nack_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(2),
        "ack"             / apl_ack_enum_b1,
        "direction"       / apl_dir_bit_enum_b1,
        "hdr_len"         / Const(6,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "sn"                  / Int16ul,
    "option"              / Struct(            # "option_word" / Int16ul,
        ByteSwapped(EmbeddedBitStruct(
            Padding(8),
            "ul_id"       / BitsInteger(8),    # upload id, in bit 0-7
        )),
    ),
)

ack_nack_ul = ack_nack_dl

# The followings are for APL_UPGRADE_START
upgrade_start_dl = "upgrade_start_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(20),
        "hdr_len"         / Const(20,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "upg_id"              / Int32ul,
    "upg_time_slot"       / Int16ul,
    "upg_block_size"      / apl_upg_block_size_enum_b16,
    "upg_file_size"       / Int32ul,
    "upg_file_crc"        / Int32ul,
)
upgrade_start_ul = "upgrade_start_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(12),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "upg_start_result"    / Int8ul,
    "upg_id"              / Int32ul,
)

# The followings are for APL_UPGRADE_STOP (downstream only, no upstream)
upgrade_stop_dl = "upgrade_stop_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(20),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "upg_id"              / Int32ul,
)

# The followings are for APL_DATA_TRANSFER (downstream only, no upstream)
data_transfer_dl = "data_transfer_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(4),
        "hdr_len"         / Const(12,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "data_blk_size"       / Int16ul,
    "upg_id"              / Int32ul,
    "data_blk_id"         / Int32ul,
    "data"                / Byte[this.data_blk_size]
)


# The followings are for APL_UPGRADE_STATE_QUERY
upgrade_state_query_dl = "upgrade_state_query_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(4),
        "hdr_len"         / Const(12,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "blk_num"             / Int16ul,
    "start_blk_id"        / Int32ul,
    "upg_id"              / Int32ul,
)

upgrade_state_query_ul = "upgrade_state_query_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "upg_st"          / apl_upg_state_enum_b4,
        "hdr_len"         / Const(12,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "valid_data_blk"      / Int16ul,
    "start_blk_id"        / Int32ul,
    "upg_id"              / Int32ul,
    "bit_map"             / Byte[(this.valid_data_blk + 7) >> 3]
)

# The followings are for APL_UPGRADE_EXEC (downstream only, no upstream)
upgrade_exec_dl = "upgrade_exec_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(4),
        "hdr_len"         / Const(12,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "time_2_rst"          / Int16ul,
    "upg_id"              / Int32ul,
    "try_running_time"    / Int32ul,
)

# The followings are for APL_STATE_INFO_QUERY
state_info_query_dl = "state_info_query_dl" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(4),
        "hdr_len"         / Const(4,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "info_num"            / Int16ul,
    "info_list"           / apl_upg_dev_type_enum_b8[this.info_num],  # 每个信息元素ID占1个Byte
)

dev_info = "dev_info" / Struct(
    "type"                / apl_upg_dev_type_enum_b8,
    "length"              / Int8ul,
    "value"               / Byte[this.length],
)

state_info_query_ul = "state_info_query_ul" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        Padding(12),
        "hdr_len"         / Const(8,BitsInteger(6)),
        "proto_ver"       / apl_proto_ver_enum_b6,
    )),
    "info_num"            / Int8ul,
    "upg_id"              / Int32ul,
    "info_list"           / dev_info[this.info_num]
)

#########################################################################
# The followings are for every protocol interaction frames' construction
#########################################################################

meter_read = "meter_read" / Union(0,
    "dl" / Optional(meter_read_dl),
    "ul" / Optional(meter_read_ul),
)

meter_simu_read = "meter_simu_read" / Union(0,
    "dl" / Optional(meter_simu_read_dl),
    "ul" / Optional(meter_simu_read_ul),
)

meter_data_collect = "meter_data_collect" / Union(0,
    "dl" / Optional(meter_simu_read_dl),
    "ul" / Optional(meter_data_collect_ul),
)

node_reg_start = "node_reg_start" / Union(0,        # downstream only, no upstream
    "dl" / Optional(node_reg_start_dl),
)

node_reg_query = "node_reg_query" / Union(0,
    "dl" / Optional(node_reg_query_dl),
    "ul" / Optional(node_reg_query_ul),
)

node_reg_stop = "node_reg_stop" / Union(0,          # downstream only, no upstream
    "dl" / Optional(node_reg_stop_dl),
)

time_cali = "time_cali" / Union(0,                  # downstream only, no upstream
    "dl" / Optional(time_cali_dl),
)

event_report = "event_report" / Union(0,            # downstream and upstream are the same
    "dl" / Optional(event_report_dl),
    "ul" / Optional(event_report_ul),
)

comm_test = "comm_test" / Union(0,                  # downstream only, no upstream
    "dl" / Optional(comm_test_dl),
)

ack_nack = "ack_nack" / Union(0,                    # downstream and upstream are the same
    "dl" / Optional(ack_nack_dl),
    "ul" / Optional(ack_nack_ul),
)

upgrade_start = "upgrade_start" / Union(0,
    "dl" / Optional(upgrade_start_dl),
    "ul" / Optional(upgrade_start_ul),
)

upgrade_stop = "upgrade_stop" / Union(0,            # downstream only, no upstream
    "dl" / Optional(upgrade_stop_dl),
)

data_transfer = "data_transfer" / Union(0,          # downstream only, no upstream
    "dl" / Optional(data_transfer_dl),
)

data_transfer_bc = "data_transfer_bc" / Union(0,    # downstream only, no upstream, ths same as "data_transfer"
    "dl" / Optional(data_transfer_dl),
)

upgrade_state_query = "upgrade_state_query" / Union(0,
    "dl" / Optional(upgrade_state_query_dl),
    "ul" / Optional(upgrade_state_query_ul),
)

upgrade_exec = "upgrade_exec" / Union(0,            # downstream only, no upstream
    "dl" / Optional(upgrade_exec_dl),
)

state_info_query = "state_info_query" / Union(0,
    "dl" / Optional(state_info_query_dl),
    "ul" / Optional(state_info_query_ul),
)

#########################################################################
# The followings are for the whole PLC APL frames construction
#########################################################################

plc_apl = "plc_apl" / Struct(
    "header" / apl_header,
    "body" / Switch(this.header.id,
        {
            "APL_CCT_METER_READ"      : meter_read,
            "APL_ROUTE_METER_READ"    : meter_read,
            "APL_CCT_SIMU_METER_READ" : meter_simu_read,
            "APL_TIME_CALI"           : time_cali,
            "APL_COMM_TEST"           : comm_test,
            "APL_EVENT_REPORT"        : event_report,
            "APL_NODE_REG_QUERY"      : node_reg_query,
            "APL_NODE_REG_START"      : node_reg_start,
            "APL_NODE_REG_STOP"       : node_reg_stop,
            "APL_ACK_NACK"            : ack_nack,
            "APL_DATA_COLLECT"        : meter_data_collect,
            "APL_UPGRADE_START"       : upgrade_start,
            "APL_UPGRADE_STOP"        : upgrade_stop,
            "APL_DATA_TRANSFER"       : data_transfer,
            "APL_DATA_TRANSFER_BC"    : data_transfer_bc,
            "APL_UPGRADE_STATE_QUERY" : upgrade_state_query,
            "APL_UPGRADE_EXEC"        : upgrade_exec,
            "APL_STATE_INFO_QUERY"    : state_info_query,
#            "APL_SECURITY"            : meter_read,        # not find the definitions in the standard doc

        },
        default = Pass
    ),
)


plc_apl_dl = "plc_apl_dl" / Struct(
    "header" / apl_header,
    "body" / Switch(this.header.id,
        {
            "APL_CCT_METER_READ"      : meter_read_dl,
            "APL_ROUTE_METER_READ"    : meter_read_dl,
            "APL_CCT_SIMU_METER_READ" : meter_simu_read_dl,
            "APL_TIME_CALI"           : time_cali_dl,
            "APL_COMM_TEST"           : comm_test_dl,
            "APL_EVENT_REPORT"        : event_report_dl,
            "APL_NODE_REG_QUERY"      : node_reg_query_dl,
            "APL_NODE_REG_START"      : node_reg_start_dl,
            "APL_NODE_REG_STOP"       : node_reg_stop_dl,
            "APL_ACK_NACK"            : ack_nack_dl,
            "APL_DATA_COLLECT"        : meter_simu_read_dl,
            "APL_UPGRADE_START"       : upgrade_start_dl,
            "APL_UPGRADE_STOP"        : upgrade_stop_dl,
            "APL_DATA_TRANSFER"       : data_transfer_dl,
            "APL_DATA_TRANSFER_BC"    : data_transfer_dl,
            "APL_UPGRADE_STATE_QUERY" : upgrade_state_query_dl,
            "APL_UPGRADE_EXEC"        : upgrade_exec_dl,
            "APL_STATE_INFO_QUERY"    : state_info_query_dl,
#            "APL_SECURITY"            : meter_read,        # not find the definitions in the standard doc

        },
    ),
)

plc_apl_ul = "plc_apl_ul" / Struct(
    "header" / apl_header,
    "body" / Switch(this.header.id,
        {
            "APL_CCT_METER_READ"      : meter_read_ul,
            "APL_ROUTE_METER_READ"    : meter_read_ul,
            "APL_CCT_SIMU_METER_READ" : meter_simu_read_ul,
            "APL_EVENT_REPORT"        : event_report_ul,
            "APL_NODE_REG_QUERY"      : node_reg_query_ul,
            "APL_ACK_NACK"            : ack_nack_ul,
            "APL_DATA_COLLECT"        : meter_data_collect_ul,
            "APL_UPGRADE_START"       : upgrade_start_ul,
            "APL_UPGRADE_STATE_QUERY" : upgrade_state_query_ul,
            "APL_STATE_INFO_QUERY"    : state_info_query_ul,
#            "APL_SECURITY"            : meter_read,        # not find the definitions in the standard doc

        },
    ),
)
