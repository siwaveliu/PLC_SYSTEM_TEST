# -- coding: utf-8 --

"""
GDW1376.2 frame

"""

from construct import *
from construct.lib import *

BcdAddress = ExprAdapter(Byte[6],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")][::-1],
    decoder = lambda obj,ctx: "-".join("%02x" % b for b in obj[::-1]),
)

BcdDate = ExprAdapter(Byte[3],
    encoder = lambda obj,ctx: [int(part, 16) for part in obj.split("-")][::-1],
    decoder = lambda obj,ctx: "".join("%02x" % b for b in obj[::-1]),
)

comm_mode_enum_b6 = "comm_mode_enum_b6" / Enum(BitsInteger(6),
                           BB_PLC=0x03, #
                          )

dir_enum_b1 = "dir_enum_b1" / Enum(BitsInteger(1),
                           DL=0,
                           UL=1
                          )

prm_enum_b1 = "prm_enum_b1" / Enum(BitsInteger(1),
                           SLAVE=0,
                           MASTER=1
                          )

comm_rate_type_enum_b1 = "comm_rate_type_enum_b1" / Enum(BitsInteger(1),
                           BPS=0,
                           KBPS=1
                          )


encoding_type_enum_b4 = "encoding_type_enum_b4" / Enum(BitsInteger(4),
                           NO_ENCODING=0,
                           RS_ENCODING=1,
                          )

proto_type_enum_u8 = "proto_type_enum_u8" / Enum(Int8ul,
                           PROTO_TRANSPARENT=0,
                           PROTO_DLT645_97=1,
                           PROTO_DLT645_07=2,
                           PROTO_DLT698_45=3,
                          )
gdw1376p2_afn05_flag_enum_b8 = "gdw1376p2_afn05_flag_enum_b8" / Enum(Int8ul,
                           AFN05F2_FLAG_FORBID       = 0,    # 禁止事件上报
                           AFN14F1_FLAG_PERMIT       = 1,    # 允许事件上报
)

time_cali_cwd_type_enum_b8 = "time_cali_cwd_type_enum_b8" / Enum (Int8ul,
                           CWD_TRANSPARENCE          = 0,
                           CWD_DLT645_1997           = 1,
                           CWD_DLT645_2007           = 2,
                           CWD_PHASE_IDENTIFY        = 3,
#                         default                     = Pass
)

delay_flag_type_enum_b8 = "delay_flag_type_enum_b8" / Enum (Int8ul,
                           NEED_NOT_CORRECT_DELAY    = 0,
                           NEED_CORRECT_DELAY        = 1,
#                         default                     = Pass
)

gdw1376p2_dev_type_enum_b8 = "gdw1376p2_dev_type_enum_b8" / Enum(Int8ul,
                           GDW1376P2_DEV_COLLECTOR   = 0,
                           GDW1376P2_DEV_METER       = 1,
)

gdw1376p2_file_id_enum_b8 = "gdw1376p2_file_id_enum_b8" / Enum(Int8ul,
                           AFN15F1_CLEAR_FILE           = 0,    # 清除下装文件
                           AFN15F1_LOCAL_MOD_UPG        = 3,    # 本地通信模块升级文件
                           AFN15F1_P_S_NODE_UPG         = 7,    # 主节点和子节点模块升级(控制全网升级)
                           AFN15F1_S_NODE_UPG           = 8,    # 子节点模块升级
)

gdw1376p2_file_att_enum_b8 = "gdw1376p2_file_att_enum_b8" / Enum(Int8ul,
                           AFN15F1_START_MIDDLE_FRAME   = 0,    # 起始帧，中间帧为00H
                           AFN15F1_END_FRAME            = 1,    # 起始帧，中间帧为00H
)

gdw1376p2_file_ind_enum_b8 = "gdw1376p2_file_ind_enum_b8" / Enum(Int8ul,
                           AFN15F1_PKT_DNLD             = 0,    # 报文方式下装
)

gdw1376p2_afn12_dt1_enum_b8 = "gdw1376p2_afn12_dt1_enum_b8" / Enum(Int8ul,
                           AFN12F1_RESET                = 1,    # 重启
                           AFN12F2_PAUSE                = 2,    # 暂停
                           AFN12F3_RESUME               = 4,    # 恢复
)

gdw1376p2_afn14_flag_enum_b8 = "gdw1376p2_afn14_flag_enum_b8" / Enum(Int8ul,
                           AFN14F1_FLAG_FAIL            = 0,    # 抄读失败
                           AFN14F1_FLAG_SUCCESS         = 1,    # 抄读成功
                           AFN14F1_FLAG_ALLOW           = 2,    # 允许抄读
)

gdw1376p2_afn14_delay_enum_b8 = "gdw1376p2_afn14_delay_enum_b8" / Enum(Int8ul,
                           AFN14F1_DELAY_NO_AMEND       = 0,    # 当前通信数据与本地信道延时无关。
                           AFN14F1_DELAY_NEED_AMEND     = 1,    # 当前通信数据与本地信道延时有关，后续需要CCT酌情修正
)

gdw1376p2_afn14_phase_enum_b8 = "gdw1376p2_afn14_phase_enum_b8"   / Enum(Int8ul,
                           AFN14F1_PHASE_UNKNOWN        = 0,
                           AFN14F1_PHASE_1              = 1,
                           AFN14F1_PHASE_2              = 2,
                           AFN14F1_PHASE_3              = 3,
#    default                              = Pass
)

role_enum_b4 = "role_enum_b4" / Enum(BitsInteger(4),
                           ROLE_INVALID=0x0, #
                           ROLE_STA=0x1, #
                           ROLE_PCO=0x2, #
                           ROLE_RESERVED=0x3, #
                           ROLE_CCO=0x4, #
                          )

afn06f3_change_type_u8 = "afn06f3_change_type_u8" / Enum(Int8ul,
                           METER_READ_TASK_COMPLETE=1,
                           METER_SEARCH_TASK_COMPLETE=2,
                          )

gdw1376p2_head = "gdw1376p2_head" / Struct(
    "start_char1" / Const(b"\x68"),
    "len"         / Int16ul,
)

gdw1376p2_cf = "gdw1376p2_cf" / BitStruct(
    "dir"       / dir_enum_b1,
    "prm"       / prm_enum_b1,
    "comm_mode" / comm_mode_enum_b6,
)

gdw1376p2_tail = "gdw1376p2_tail" / Struct(
    "cs"       / Int8ul,
    "end_char" / Const(b"\x16")
)

gdw1376p2_r_dl = "gdw1376p2_r_dl" / Struct(
    EmbeddedBitStruct(
        "relay_level"          / BitsInteger(4),
        "conflict_detect_flag" / BitsInteger(1),
        "comm_module_flag"     / BitsInteger(1),
        "subnode_flag"         / BitsInteger(1),
        "route_flag"           / BitsInteger(1),
    ),
    EmbeddedBitStruct(
        "coding_type"          / encoding_type_enum_b4,
        "channel_id"           / BitsInteger(4),
    ),
    "reply_len"                / Int8ul,
    ByteSwapped(EmbeddedBitStruct(
        "comm_rate_flag"       / comm_rate_type_enum_b1,
        "comm_rate"            / BitsInteger(15),
    )),
    "sn" / Int8ul,
)

gdw1376p2_r_ul = "gdw1376p2_r_dl" / Struct(
    EmbeddedBitStruct(
        "relay_level"      / BitsInteger(4),
        Padding(1),
        "comm_module_flag" / BitsInteger(1),
        Padding(1),
        "route_flag"       / BitsInteger(1),
    ),
    EmbeddedBitStruct(
        Padding(4),
        "channel_id"       / BitsInteger(4),
    ),
    EmbeddedBitStruct(
        "channel_type"     / BitsInteger(4),
        "phase_id"         / BitsInteger(4),
    ),
    EmbeddedBitStruct(
        "reply_sig_q"      / BitsInteger(4),
        "cmd_sig_q"        / BitsInteger(4),
    ),
    EmbeddedBitStruct(
        Padding(7),
        "event_flag"       / BitsInteger(1),
    ),
    "sn" / Int8ul,
)

afn00h_f1_data = "afn00h_f1_data" / Struct(
    EmbeddedBitStruct(
        "ch15" / BitsInteger(1),
        "ch14" / BitsInteger(1),
        "ch13" / BitsInteger(1),
        "ch12" / BitsInteger(1),
        "ch11" / BitsInteger(1),
        "ch10" / BitsInteger(1),
        "ch9"  / BitsInteger(1),
        "ch8"  / BitsInteger(1),
        "ch7"  / BitsInteger(1),
        "ch6"  / BitsInteger(1),
        "ch5"  / BitsInteger(1),
        "ch4"  / BitsInteger(1),
        "ch3"  / BitsInteger(1),
        "ch2"  / BitsInteger(1),
        "ch1"  / BitsInteger(1),
        "cmd_status" / BitsInteger(1),
    ),
    Padding(2),
    "wait_time" / Int16ul
)

afn00h_f2_data = "afn00h_f2_data" / Struct(
    "err_code"  / Int8ul
)

afn00h_data ="afn00h_data" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn00h_f1_data,  #F1
                    2: afn00h_f2_data,  #F2
                }
            ),
        },
        default=Pass,
    )
)

afn01h_data ="afn01h_data" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                },
                default=Pass,
            ),
        },
        default=Pass,
    )
)

afn03h_data_dl ="afn03h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
#                    1: afn03h_f1_data_dl,  #F1
                },
                default=Pass,
            ),
        },
        default=Pass,
    )
)

afn03h_f7_data_ul = "afn03h_f7_data_ul" / Struct(
    "max_exp_time" / Int8ul,
)


afn03f10_comm_rate = "afn03f10_comm_rate" / Struct(
    ByteSwapped(EmbeddedBitStruct(
        "comm_rate_flag"       / comm_rate_type_enum_b1,
        "comm_rate"            / BitsInteger(15),
    )),
)

afn03h_f10_data_ul = "afn03h_f10_data_ul" / Struct(
    EmbeddedBitStruct(
        "periodic_mr_mode" / BitsInteger(2),
        "sec_node_mode" / BitsInteger(1),
        "route_mng_mode" / BitsInteger(1),
        "comm_mode" / BitsInteger(4),
    ),

    EmbeddedBitStruct(
        "bc_cmd_ch_exec_mode" / BitsInteger(2),
        "bc_cmd_ack_mode" / BitsInteger(1),
        "fail_switch_mode" / BitsInteger(2),
        "delay_param_support" / BitsInteger(3),
    ),

    EmbeddedBitStruct(
        "pwr_loss" / BitsInteger(3),
        "ch_num" / BitsInteger(5),
    ),

    EmbeddedBitStruct(
        Padding(4),
        "rate_num" / BitsInteger(4),
    ),

    Padding(2),
    "sec_node_monitor_max_exp_time" / Int8ul,
    "bc_cmd_max_exp_time" / Int16ul,
    "max_frame_len" / Int16ul,
    "max_single_blk_len_for_file_transfer" / Int16ul,
    "upg_wait_time" / Int8ul,
    "master_addr" / BcdAddress,
    "max_sec_node_num" / Int16ul,
    "curr_sec_node_num" / Int16ul,
    "proto_pub_date" / BcdDate,
    "proto_record_date" / BcdDate,
    "vendor_code_version_info" / Byte[9],
    "comm_rate_list" / afn03f10_comm_rate[this.rate_num]
)

afn03h_f16_data_ul = "afn03h_f16_data_ul" / Struct(
    "band" / Int8ul,
)


afn03h_data_ul ="afn03h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
#                    1: afn03h_f1_data_ul,  #F1
                    64: afn03h_f7_data_ul,  #F7
                }
            ),
            1: Switch(this.dt1,
                {
                    2: afn03h_f10_data_ul,  #F10
                    128: afn03h_f16_data_ul,  #F16
                }
            ),
        },
        default=Pass,
    )
)

afn04h_f3_data_dl = "afn04h_f3_data_dl" / Struct(
    "comm_rate"   / Int8ul,
    "node_addr"   / BcdAddress,
    "proto_type"  / proto_type_enum_u8,
    "data_len"    / Int8ul,
    "data"        / Int8ul[this.data_len],
)

afn04h_data_dl ="afn04h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    4: afn04h_f3_data_dl,  #F3 本地通信模块报文通信测试
                }
            ),
        },
        default=Pass,
    )
)

afn05h_f1_data = "afn05h_f1_data" / Struct(
    "addr" / BcdAddress
)

afn05h_f2_data = "afn05h_f2_data" / Struct(
    "flag" / gdw1376p2_afn05_flag_enum_b8,
)

afn05h_f3_data = "afn05h_f3_data" / Struct(
    "cwd"  / time_cali_cwd_type_enum_b8,
    "len"  / Int8ul,
    "data" / Int8ul[this.len],
)

afn05h_f16_data = "afn05h_f16_data" / Struct(
    "band"  / Int8ul,
)

afn05h_data_dl ="afn05h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn05h_f1_data,  #F1 设置主节点地址
                    2: afn05h_f2_data,  #F2 允许/禁止从节点上报
                    4: afn05h_f3_data,  #F3 启动广播（校时）
                }
            ),
            1: Switch(this.dt1,
                {
                    128: afn05h_f16_data,  #F16 设置宽带载波通信参数
                }
            ),
        },
        default=Pass,
    )
)

afn06h_f2_data = "afn06h_f2_data" / Struct(
    "idx"                / Int16ul,
    "proto_type"         / proto_type_enum_u8,
    "latency"            / Int16ul,            # 当前报文本地通信上行时长
    "pkt_len"            / Int8ul,
    "pkt"                / Int8ul[this.pkt_len],
)

sub_node_info_st = "sub_node_info_st" / Struct(
    "addr"               / BcdAddress,
    "proto_type"         / proto_type_enum_u8,
)

node_info_st = "node_info_st" / Struct(
    "addr"               / BcdAddress,
    "proto_type"         / proto_type_enum_u8,
    "idx"                / Int16ul,
    "dev_type"           / gdw1376p2_dev_type_enum_b8,
    "sub_node_total_num" / Int8ul,
    "curr_sub_node_num"  / Int8ul,
    "sub_node"           / sub_node_info_st[this.curr_sub_node_num],
)

afn06h_f3_data = "afn06h_f3_data" / Struct(
    "type"   / afn06f3_change_type_u8
)


afn06h_f4_data = "afn06h_f4_data" / Struct(
    "node_num"   / Int8ul,
    "node"       / node_info_st[this.node_num],
)

afn06h_f5_data = "afn06h_f5_data" / Struct(
    "dev_type"           / gdw1376p2_dev_type_enum_b8,
    "proto_type"         / proto_type_enum_u8,
    "data_len"           / Int8ul,
    "data"               / Int8ul[this.data_len],
)

afn06h_data ="afn06h_data" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    2:  afn06h_f2_data,  #F2, 上报抄读数据
                    4:  afn06h_f3_data,  #F3, 上报路由工况变动信息
                    8:  afn06h_f4_data,  #F4, 上报从节点信息及设备类型
                    16: afn06h_f5_data,  #F5, 上报从节点事件
                }
            ),
        },
        default=Pass,
    )
)


afn10h_f21_data_dl = "afn10h_f21_data_dl" / Struct(
    "start_idx"  / Int16ul,
    "num"  / Int8ul,
)

afn10h_f112_data_dl = "afn10h_f112_data_dl" / Struct(
    "start_idx"  / Int16ul,
    "num"  / Int8ul,
)

afn10h_data_dl ="afn10h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            2: Switch(this.dt1,
                {
                    16: afn10h_f21_data_dl,  #F21 查询载波网络拓扑
                }
            ),
            13: Switch(this.dt1,
                {
                    128: afn10h_f112_data_dl,  #F27 查询宽带载波芯片信息
                }
            ),
        },
        default=Pass,
    )
)

afn10f21_node_info = "afn10f21_node_info" / Struct(
    "addr"  / BcdAddress,
    "sta_tei"  / Int16ul,
    "proxy_tei"  / Int16ul,
    EmbeddedBitStruct(
        "role"         / role_enum_b4,
        "level" / BitsInteger(4),
    ),
)


afn10h_f21_data_ul = "afn10h_f21_data_ul" / Struct(
    "total_num"  / Int16ul,
    "start_idx"  / Int16ul,
    "curr_num"  / Int8ul,
    "node_list" / afn10f21_node_info[this.curr_num]
)

afn10f112_chip_id = "afn10f112_chip_id" / Struct(
    "c1" / Const(0x1, Int8ul),
    "c2" / Const(0x2, Int8ul),
    "c3" / Const(0x9C, Int8ul),
    "c4" / Const(0x01C1FB, Int24ul),
    "dev_categoy" / Int8ul,
    "vendor_code" / Int16ul,
    "chip_id" / Int16ul,
    "dev_sn" / BytesInteger(5, swapped=True),
    "checksum" / BytesInteger(8, swapped=True),
)

afn10f112_node_info = "afn10f112_node_info" / Struct(
    "addr"  / BcdAddress,
    "dev_type"  / Int8ul,
    "chip_id"  / afn10f112_chip_id,
    "sw_ver" / Byte[2]
)

afn10h_f112_data_ul = "afn10h_f112_data_ul" / Struct(
    "total_num"  / Int16ul,
    "start_idx"  / Int16ul,
    "curr_num"  / Int8ul,
    "node_list" / afn10f112_node_info[this.curr_num]
)

afn10h_data_ul ="afn10h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            2: Switch(this.dt1,
                {
                    16: afn10h_f21_data_ul,  #F21 查询载波网络拓扑
                }
            ),
            13: Switch(this.dt1,
                {
                    128: afn10h_f112_data_ul,  #F27 查询宽带载波芯片信息
                }
            ),
        },
        default=Pass,
    )
)


afn11h_f1_sec_node = "afn11h_f1_sec_node" / Struct(
    "addr"       / BcdAddress,
    "proto_type" / proto_type_enum_u8
)

afn11h_f1_data = "afn11h_f1_data" / Struct(
    "num"  / Int8ul,
    "list" / afn11h_f1_sec_node[this.num]
)

afn11h_f2_data = "afn11h_f2_data" / Struct(
    "num"  / Int8ul,
    "list" / BcdAddress[this.num]
)

afn11h_f5_data = "afn11h_f5_data" / Struct(
    "start_time"               / Int8ul[6],  # BCD
    "duration"                 / Int16ul,    # minutes
    "re_send_times"            / Int8ul,
    "rand_wait_time_slice_num" / Int8ul,     # 150ms / time-slice
)

afn11h_data ="afn11h_data" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1:  afn11h_f1_data,  #F1 添加从节点
                    2:  afn11h_f2_data,  #F2 删除从节点
                    16: afn11h_f5_data,  #F5 激活从节点主动注册
                    32: Byte[0],         #F6 中止从节点主动注册, 无数据单元内容
                },
                #default=Pass,
            ),
        },
        default=Pass,
    )
)

#afn12h_f1_data = "afn12h_f1_data" / Struct( # 无数据单元内容
#)
#afn12h_f2_data = "afn12h_f2_data" / Struct( # 无数据单元内容
#)
#afn12h_f3_data = "afn12h_f3_data" / Struct( # 无数据单元内容
#)

afn12h_data ="afn12h_data" / Struct(    # 路由控制类
    "dt1" / gdw1376p2_afn12_dt1_enum_b8,
    "dt2" / Const(0,Int8ul),
#    "data" / Switch(this.dt2,
#        {
#            0: Switch(this.dt1,
#                {
#                    1:  afn12h_f1_data,  #F1 重启
#                    2:  afn12h_f2_data,  #F2 暂停
#                    4:  afn12h_f3_data,  #F5 恢复
#                }
#            ),
#        },
#        default=Pass,
#    )
)

afn13h_f1_data_dl = "afn13h_f1_data_dl" / Struct(
    "proto_type"   / proto_type_enum_u8,
    "delay_flag"   / delay_flag_type_enum_b8,
    "subnode_num"  / Int8ul,
    "addr"         / BcdAddress[this.subnode_num],
    "packet_len"   / Int8ul,
    "packet"       / Int8ul[this.packet_len]
)

afn13h_data_dl ="afn13h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn13h_f1_data_dl,  #F1
                }
            ),
        },
        default=Pass,
    )
)

afn13h_f1_data_ul = "afn13h_f1_data_ul" / Struct(
    "ul_delay"   / Int16ul,
    "proto_type" / proto_type_enum_u8,
    "packet_len" / Int8ul,
    "packet"     / Int8ul[this.packet_len]
)

afn13h_data_ul ="afn13h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn13h_f1_data_ul,  #F1
                }
            ),
        },
        default=Pass,
    )
)

afn14h_f1_data_ul = "afn14h_f1_data_ul" / Struct(
    "phase"  / gdw1376p2_afn14_phase_enum_b8,
    "addr"   / BcdAddress,
    "idx"    / Int16ul,
)

afn14h_data_ul ="afn14h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn14h_f1_data_ul,  #F1 路由请求抄读内容
                }
            ),
        },
        default=Pass,
    )
)

afn14h_f1_data_dl = "afn14h_f1_data_dl" / Struct(
    "flag"          / gdw1376p2_afn14_flag_enum_b8,
    "delay"         / gdw1376p2_afn14_delay_enum_b8,
    "data_len"      / Int8ul,
    "data"          / Int8ul[this.data_len],
    "sub_node_num"  / Int8ul,
    "sub_node_addr" / BcdAddress[this.sub_node_num],
)

afn14h_data_dl ="afn14h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn14h_f1_data_dl,  #F1 路由请求抄读内容
                }
            ),
        },
        default=Pass,
    )
)

afn15h_f1_data_dl = "afn15h_f1_data_dl" / Struct(
    "file_id"      / gdw1376p2_file_id_enum_b8,
    "file_att"     / gdw1376p2_file_att_enum_b8,
    "file_ind"     / gdw1376p2_file_ind_enum_b8,
    "block_num"    / Int16ul,
    "block_id"     / Int32ul,
    "block_len"    / Int16ul,
    "data"         / Int8ul[this.block_len],
)

afn15h_data_dl ="afn15h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn15h_f1_data_dl,  #F1
                }
            ),
        },
        default=Pass,
    )
)

afn15h_f1_data_ul = "afn15h_f1_data_ul" / Struct(
    "block_id"     / Int32ul,
)

afn15h_data_ul ="afn15h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afn15h_f1_data_ul,  #F1
                }
            ),
        },
        default=Pass,
    )
)

afnf1h_f1_data_dl = "afnf1h_f1_data_dl" / Struct(
    "proto_type"     / proto_type_enum_u8,
#    "sub_node_num"   / Int8ul,
#    "sub_node_addr"  / BcdAddress[this.sub_node_num],
    Padding(1),
    "data_len"       / Int16ul,
    "data"           / Int8ul[this.data_len],
)

afnf1h_data_dl ="afnf1h_data_dl" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afnf1h_f1_data_dl,  #F1 - 并发抄表下行报文
                }
            ),
        },
        default=Pass,
    )
)

afnf1h_f1_data_ul = "afnf1h_f1_data_ul" / Struct(
    "proto_type"     / proto_type_enum_u8,
    "data_len"       / Int16ul,
    "data"           / Int8ul[this.data_len],
)

afnf1h_data_ul ="afnf1h_data_ul" / Struct(
    "dt1"  / Int8ul,
    "dt2"  / Int8ul,
    "data" / Switch(this.dt2,
        {
            0: Switch(this.dt1,
                {
                    1: afnf1h_f1_data_ul,  #F1 - 并发抄表上行报文
                }
            ),
        },
        default=Pass,
    )
)

gdw1376p2_user_data_dl = "gdw1376p2_user_data_dl" / Struct(
    "r" / gdw1376p2_r_dl,
    "a" / If(this.r.comm_module_flag == 1, Struct(
        "src"        / BcdAddress,
        "relay_addr" / If(this._.r.relay_level > 0, BcdAddress[this._.r.relay_level]),
        "dst"        / BcdAddress,
    )),
    "afn"  / Int8ul,
    "data" / Switch(this.afn,
        {
            0x00: afn00h_data,
            0x01: afn01h_data,
            0x03: afn03h_data_dl,
            0x04: afn04h_data_dl,
            0x05: afn05h_data_dl,
            0x10: afn10h_data_dl,
            0x11: afn11h_data,
            0x12: afn12h_data,
            0x13: afn13h_data_dl,
            0x14: afn14h_data_dl,
            0x15: afn15h_data_dl,
            0xF1: afnf1h_data_dl,
        },
        default=Pass
    )
)


gdw1376p2_user_data_ul = "gdw1376p2_user_data_ul" / Struct(
    "r" / gdw1376p2_r_ul,
    "a" / If(this.r.comm_module_flag == 1, Struct(
        "src" / BcdAddress,
        "dst" / BcdAddress,
    )),
    "afn"  / Int8ul,
    "data" / Switch(this.afn,
        {
            0x00: afn00h_data,
            0x03: afn03h_data_ul,
            0x06: afn06h_data,
            0x10: afn10h_data_ul,
            0x13: afn13h_data_ul,
            0x14: afn14h_data_ul,
            0x15: afn15h_data_ul,
            0xF1: afnf1h_data_ul,
        },
        default=Pass
    )
)


gdw1376p2 = "gdw1376p2" / Struct(
    "head" / gdw1376p2_head,
    "cf"   / gdw1376p2_cf,
    "user_data" / RawCopy(Switch(this.cf.dir,
        {
            "DL": gdw1376p2_user_data_dl,
            "UL": gdw1376p2_user_data_ul
        },
        default=Pass,
    )),
    "tail" / gdw1376p2_tail,
)
