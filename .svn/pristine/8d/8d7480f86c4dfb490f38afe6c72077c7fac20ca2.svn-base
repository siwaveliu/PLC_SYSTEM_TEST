"""
PLC Test Frame

"""

from construct import *
from construct.lib import *
from plc_mpdu import *
from plc_beacon import *


#===============================================================================
# Frame Header
#===============================================================================

cf_enum = "cf_enum" / Enum(Int16ub,
                           FC_DATA=0x0001,
                           FC_PL_DATA=0x0002,
                           PL_DATA=0x0003,
                           TX_COMPLETE_IND=0x0004,
                           SACK_TX_COMPLETE_IND=0x0005,
                           BEACON_DATA=0x0006,
                           PERIODIC_FC_PL_DATA=0x0007,
                           RESET_CMD=0x0100,
                           COMM_TEST_REQ_CMD=0x0101,
                           COMM_TEST_CNF_CMD=0x0102,
                           TIME_READ_REQ_CMD=0x0103,
                           TIME_READ_CNF_CMD=0x0104,
                           TIME_CONFIG_REQ_CMD=0x0105,
                           TIME_CONFIG_CNF_CMD=0x0106,
                           SACK_TEI_CONFIG_REQ_CMD=0x0107,
                           SACK_TEI_CONFIG_CNF_CMD=0x0108,
                           BAND_CONFIG_REQ_CMD=0x0109,
                           BAND_CONFIG_CNF_CMD=0x010A,
                           PHASE_CONFIG_REQ_CMD=0x010B,
                           PHASE_CONFIG_CNF_CMD=0x010C,
                           NACK_TEI_CONFIG_REQ_CMD=0x010D,
                           NACK_TEI_CONFIG_CNF_CMD=0x010E,
                           SACK_CONFIG_REQ_CMD=0x010F,
                           SACK_CONFIG_CNF_CMD=0x0110,
                           COMM_RATE_TEST_REQ_CMD=0x0111,
                           COMM_RATE_TEST_CNF_CMD=0x0112,
                           ACTIVATE_REQ_CMD=0x0113,
                           ACTIVATE_CNF_CMD=0x0114,
                           DEACTIVATE_REQ_CMD=0x0115,
                           DEACTIVATE_CNF_CMD=0x0116,
                           STA_CONFIG_REQ_CMD=0x0117,
                           STA_CONFIG_CNF_CMD=0x0118,
                           EVT_TRIG_REQ_CMD=0x0119,
                           EVT_TRIG_CNF_CMD=0x011A,
                           SACK_CONFIG_EX_REQ_CMD=0x011B,
                           SACK_CONFIG_EX_CNF_CMD=0x011C,                           
                           FREQ_OFFSET_CONFIG_REQ_CMD=0x011D,
                           FREQ_OFFSET_CONFIG_CNF_CMD=0x011E,
                          )

plc_phase_enum_u8 = "phase_enum_u8" / Enum(Int8ul,
                           PLC_PHASE_ALL=0,
                           PLC_PHASE_A=1,
                           PLC_PHASE_B=2,
                           PLC_PHASE_C=3,
)

plc_test_frame_head = "plc_test_frame_head" / Struct(
    "start_char" / Const(b"\xED"),
    "len" / Int16ub,
    "cf" / cf_enum,
    "sn" / Int16ul,
    Padding(1),
)

plc_test_frame_tail = "plc_test_frame_tail" / Struct(
    "cs" / Int8ul,
    "end_char" / Const(b"\xEE"),
)

#===============================================================================
# Frame Body
#===============================================================================

fc_pl_data = "fc_pl_data" / Struct(
    "timestamp" / Int32ul,
    "pb_size" / Int16ul,
    "pb_num" / Int8ul,
    "phase" / Int8ul,
    "payload" / RawCopy(Byte[16 + this.pb_size * this.pb_num])
)

pl_data = "pl_data" / Struct(
    "timestamp" / Int32ul,
    "pb_size" / Int16ul,
    "pb_num" / Int8ul,
    Padding(1),
    "payload" / Byte[this.pb_num * this.pb_size]
)

tx_complete_ind = "tx_complete_ind" / Struct(
    "timestamp" / Int32ul,
)

sack_tx_complete_ind = "tx_complete_ind" / Struct(
    "timestamp" / Int32ul,
    "fc" / plc_mpdu_fc,
)

beacon_data = "beacon_data" / Struct(
    "tx_time" / Int32ul,
    "period" / Int16ul,
    "num" / Int16ul,
    "pb_size" / Int16ul,
    "cfg_csma_flag" /Int8ul,
    Padding(1),
    "fc" / plc_mpdu_fc,
    "payload" / RawCopy(plc_beacon)
)

periodic_fc_pl_data = "fc_pl_data" / Struct(
    "timestamp" / Int32ul,
    "tx_num" / Int32ul,
    "tx_interval" / Int16ul,
    "pb_size" / Int16ul,
    "beacon_period" / Int16ul,
    "beacon_interval" / Int16ul,
    "beacon_num" / Int8ul,
    "pb_num" / Int8ul,
    "phase" / Int8ul,
    Padding(1),
    "payload" / RawCopy(Byte[16 + this.pb_size * this.pb_num])
)



time_read_cnf = "time_read_cnf" / Struct(
    "timestamp" / Int32ul,
)

time_config_req = "time_config_req" / Struct(
    "offset" / Int32sl,
    "proxy_tei" / Int16ul,
    "proxy_phase" / plc_phase_enum_u8,
    Padding(1)
)

time_config_cnf = "time_config_cnf" / Struct(
    "timestamp" / Int32ul,
)

band_config_req = "band_config_req" / Struct(
    "band" / Int8ul,
    "tonemask" / Int8ul,
)

phase_config_req = "phase_config_req" / Struct(
    "phase" / Int8ul,
)

sack_config_req = "sack_config_req" / Struct(
    "src_tei" / Int16ul,
    Padding(2),
    "fc" / plc_mpdu_fc,
)

sack_config_ex_req = "sack_config_ex_req" / Struct(
    "src_tei" / Int16ul,
    "num" / Int8ul,
    Padding(1),
    "fc" / plc_mpdu_fc[this.num],
)

activate_req = "activate_req" / Struct(
    "role" / Int8ul,
    "band" / Int8ul,
    "phase" / Int8ul,
    "tonemask" /Int8ul
)

activate_cnf_err_code_enum = "activate_cnf_err_code_enum" / Enum(Int8ub,
    ACT_NO_ERROR=0x00,
    ACT_ERROR=0x01,
    default=Pass
)

activate_cnf = "activate_cnf" / Struct(
    "error_code" / activate_cnf_err_code_enum,
)

deactivate_cnf_err_code_enum = "deactivate_cnf_err_code_enum" / Enum(Int8ub,
    DEACT_NO_ERROR=0x00,
    DEACT_ERROR=0x01,
    default=Pass
)

deactivate_cnf = "deactivate_cnf" / Struct(
    "error_code" / deactivate_cnf_err_code_enum,
)

sta_info = "sta_info" / Struct(
    "sta_tei" / Int16ul,
    "proxy_tei" / Int16ul,
    "min_succ_rate" / Int8ul,
    "level" / Int8ul,
    "proxy_channel_quality" / Int8ul,
    "phase" / plc_phase_enum_u8,
    "mac" / MacAddress,
)

sta_config_req = "sta_config_req" / Struct(
    "num" / Int16ul,
    "info" / sta_info[this.num],
)

freq_offset_config_req = "freq_offset_config_req" / Struct(
    "freq_offset" / Int32sl,
)

#===============================================================================
# entire trace
#===============================================================================

plc_test_frame = "plc_test_frame" / Struct(
    "head" / plc_test_frame_head,
    "payload" / Switch(this.head.cf,
        {
            "FC_DATA" : fc_pl_data,
            "FC_PL_DATA" : fc_pl_data,
            "PL_DATA" : pl_data,
            "TX_COMPLETE_IND": tx_complete_ind,
            "SACK_TX_COMPLETE_IND": sack_tx_complete_ind,
            "BEACON_DATA": beacon_data,
            "PERIODIC_FC_PL_DATA": periodic_fc_pl_data,

            "TIME_READ_CNF_CMD": time_read_cnf,
            "TIME_CONFIG_REQ_CMD": time_config_req,
            "TIME_CONFIG_CNF_CMD": time_config_cnf,
            "BAND_CONFIG_REQ_CMD": band_config_req,
            "PHASE_CONFIG_REQ_CMD": phase_config_req,
            "SACK_CONFIG_REQ_CMD": sack_config_req,
            "ACTIVATE_REQ_CMD": activate_req,
            "ACTIVATE_CNF_CMD": activate_cnf,
            "DEACTIVATE_CNF_CMD": deactivate_cnf,
            "STA_CONFIG_REQ_CMD": sta_config_req,
            "FREQ_OFFSET_CONFIG_REQ_CMD": freq_offset_config_req,
        },
        default = Pass,
    ),
    "tail" / plc_test_frame_tail,
)
