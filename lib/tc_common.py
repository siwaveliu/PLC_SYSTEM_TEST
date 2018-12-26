# -- coding: utf-8 --
from robot.api import logger
from robot.libraries import Dialogs
import plc_packet_helper
import concentrator
import test_frame_helper
import plc_tb_ctrl
import meter
import config
import time



#设置主节点地址函数
def set_cco_mac_addr(cct, mac_addr):
    assert isinstance(cct, concentrator.Concentrator)
    cct.clear_port_rx_buf()
    frame = concentrator.build_gdw1376p2_frame(dict_content= {
        'head':{'len':0},
        'cf':{'dir':'DL','prm':'MASTER','comm_mode':'BB_PLC'},
        'user_data':{
            'value':
                         {'r':{
                             'relay_level':0,
                             'conflict_detect_flag':0,
                             'comm_module_flag':0,
                             'subnode_flag':0,
                             'route_flag':0,
                             'coding_type':'NO_ENCODING',
                             'channel_id': 0,
                             'reply_len':0,
                             'comm_rate_flag':'BPS',
                             'comm_rate': 0,
                             'sn': 0
                             },
                          'a':'null',
                          'afn': 0x05,
                          'data':{
                              'dt1': 1,
                              'dt2': 0,
                              'data':{'addr': mac_addr}
                                }

                        }
                         },

        'tail':{'cs':0}
        })
    assert frame is not None
    cct.send_frame(frame)
    # 等待确认
    cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)

#添加从节点地址
def add_sub_node_addr(cct, mac_addr_list, wait_ack=True):
    """
    :type cct: concentrator.Concentrator
    """
    assert isinstance(cct, concentrator.Concentrator)
    cct.clear_port_rx_buf()
    '''
          num: 1
          list:
          addr: 00-00-00-00-00-01
          proto_type: PROTO_DLT645_07
    '''
    mac_dict_list =[]
    couter = 0 # type: int
    dl_afn11f1_pkt = plc_tb_ctrl.PlcSystemTestbench._load_data_file(data_file='afn11f1_dl.yaml')
    for addr in mac_addr_list:
        mac_dict_list.append({'addr':addr,'proto_type':'PROTO_DLT645_07'})
        couter += 1
        if couter % 15 == 0 or couter == len(mac_addr_list):
            dl_afn11f1_pkt['user_data']['value']['data']['data']['num'] = len(mac_dict_list)
            dl_afn11f1_pkt['user_data']['value']['data']['data']['list'] = mac_dict_list
            frame = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f1_pkt)
            assert frame is not None
            cct.send_frame(frame)
            # 等待确认
            if wait_ack:
                cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)
            else:
                cct.wait_for_gdw1376p2_frame(afn=0x00)
            mac_dict_list = []

#删除从节点地址
def del_sub_node_addr(cct,mac_addr_list):
    assert isinstance(cct, concentrator.Concentrator)

    cct.clear_port_rx_buf()

    '''
              num: 1
          list:
          - addr: 00-00-00-00-00-01
    '''
    mac_dict_list = []
    dl_afn11f2_pkt = plc_tb_ctrl.PlcSystemTestbench._load_data_file(data_file='afn11f2_dl.yaml')
    total = len(mac_addr_list)
    for couter in range(total):
        mac_dict_list.append(mac_addr_list[couter])
        if (couter !=0 and couter % 15 == 0) or couter == total - 1:
            plc_tb_ctrl._debug(mac_dict_list)
            dl_afn11f2_pkt['user_data']['value']['data']["data"]['num'] = len(mac_dict_list)
            dl_afn11f2_pkt['user_data']['value']['data']["data"]['list'] = mac_dict_list
            frame = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f2_pkt)
            assert frame is not None
            cct.send_frame(frame)
            # 等待确认
            cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0, tm_assert=False)
            mac_dict_list = []


#发送AFN10F21查询网络拓扑
def query_nw_top(cct, start_idx, num):
    assert isinstance(cct, concentrator.Concentrator)

    cct.clear_port_rx_buf()
    frame = concentrator.build_gdw1376p2_frame(dict_content= {
        'head':{'len':0},
        'cf':{'dir':'DL','prm':'MASTER','comm_mode':'BB_PLC'},
        'user_data':{
            'value':
                         {'r':{
                             'relay_level':0,
                             'conflict_detect_flag':0,
                             'comm_module_flag':0,
                             'subnode_flag':0,
                             'route_flag':0,
                             'coding_type':'NO_ENCODING',
                             'channel_id': 0,
                             'reply_len':0,
                             'comm_rate_flag':'BPS',
                             'comm_rate': 0,
                             'sn': 0
                             },
                          'a':'null',
                          'afn': 0x10,
                          'data':{
                                  'dt1': 16,
                                  'dt2': 2,
                                  'data':{'start_idx': start_idx,
                                          'num': num},
                                 }

                        }
                    },
        'tail':{'cs':0}
        })
    assert frame is not None
    cct.send_frame(frame)
    # wait 10F21
    afn10f21_ul_frame = cct.wait_for_gdw1376p2_frame(afn=0x10, dt1=16, dt2=2, tm_assert=False)
    return afn10f21_ul_frame

# send afn01f2, 初始化CCO参数区（清除所有从节点档案信息）
def reset_cco_param_area(cct):
    assert isinstance(cct, concentrator.Concentrator)

    cct.clear_port_rx_buf()
    frame = concentrator.build_gdw1376p2_frame(dict_content= {
    'head':
      {'len': 0},
    'cf':
      {'dir': 'DL',
      'prm': 'MASTER',
      'comm_mode': 'BB_PLC'
        },
    'user_data':{
      'value':{
        'r':{
          'relay_level': 0,
          'conflict_detect_flag': 0,
          'comm_module_flag': 0,
          'subnode_flag': 0,
          'route_flag': 0,
          'coding_type': 'NO_ENCODING',
          'channel_id': 0,
          'reply_len': 0,
          'comm_rate_flag': 'BPS',
          'comm_rate': 0,
          'sn': 0
          }, #end of r
        'a': 'null',
        'afn': 0x01,
        'data':{
          'dt1': 2,
          'dt2': 0,
          } #end of data
        }#end of value
      },#end of user_data
    'tail':{'cs': 0}
    }) #end of dict_content

    assert frame is not None
    cct.send_frame(frame)
    # 等待确认
    cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)

# uses 03F7 to read max expiratin time
def read_mr_max_exp_time(cct):
    assert isinstance(cct, concentrator.Concentrator)

    cct.clear_port_rx_buf()
    frame = concentrator.build_gdw1376p2_frame(dict_content= {
    'head':
      {'len': 0},
    'cf':
      {'dir': 'DL',
      'prm': 'MASTER',
      'comm_mode': 'BB_PLC'
        },
    'user_data':{
      'value':{
        'r':{
          'relay_level': 0,
          'conflict_detect_flag': 0,
          'comm_module_flag': 0,
          'subnode_flag': 0,
          'route_flag': 0,
          'coding_type': 'NO_ENCODING',
          'channel_id': 0,
          'reply_len': 0,
          'comm_rate_flag': 'BPS',
          'comm_rate': 0,
          'sn': 0
          }, #end of r
        'a': 'null',
        'afn': 0x03,
        'data':{
          'dt1': 64,
          'dt2': 0,
          } #end of data
        }#end of value
      },#end of user_data
    'tail':{'cs': 0}
    }) #end of dict_content

    assert frame is not None
    cct.send_frame(frame)
    # 等待03F7
    afn03f7_ul_frame = cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=64, dt2=0)

    return afn03f7_ul_frame.user_data.value.data.data.max_exp_time

def send_gdw1376p2_ack(cct, sn):
    assert isinstance(cct, concentrator.Concentrator)
    frame = concentrator.build_gdw1376p2_frame(dict_content= {
        'head':
        {'len': 0},
        'cf':
        {'dir': 'DL',
        'prm': 'SLAVE',
        'comm_mode': 'BB_PLC'
            },
        'user_data':{
        'value':{
            'r':{
            'relay_level': 0,
            'conflict_detect_flag': 0,
            'comm_module_flag': 0,
            'subnode_flag': 0,
            'route_flag': 0,
            'coding_type': 'NO_ENCODING',
            'channel_id': 0,
            'reply_len': 0,
            'comm_rate_flag': 'BPS',
            'comm_rate': 0,
            'sn': sn
            }, #end of r
            'a': 'null',
            'afn': 0x00,
            'data':{
            'dt1': 1,
            'dt2': 0,
            'data':{
                'cmd_status': 0,
                'ch1': 1,
                'ch2': 1,
                'ch3': 1,
                'ch4': 1,
                'ch5': 1,
                'ch6': 1,
                'ch7': 1,
                'ch8': 1,
                'ch9': 1,
                'ch10': 1,
                'ch11': 1,
                'ch12': 1,
                'ch13': 1,
                'ch14': 1,
                'ch15': 1,
                'wait_time': 0,
            }

            } #end of data
          }#end of value
        },#end of user_data
        'tail':{'cs': 0}
    }) #end of dict_content

    assert frame is not None
    cct.send_frame(frame)



# sync tb parameter after received beacon from DUT(must be CCO)
# it must be called after beacon received
def sync_tb_configurations(tb,nid,sn):
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "not PlcSystemTestBench instance"

    result = test_frame_helper.build_time_config_req(dict_content={
        'offset': 0,
        'proxy_tei': 1,
        'proxy_phase': 'PLC_PHASE_A'
        })
    cf = result['cf']
    frame_body = result['body']
    tb.tb_uart.send_test_frame(frame_body, cf)
    test_frame = tb.tb_uart.wait_for_test_frame("TIME_CONFIG_CNF_CMD", timeout=30)
    assert test_frame is not None

    tb._configure_nw_static_para(nid, sn)
    return test_frame.payload.timestamp

#role parameter has not been used up to now.
def activate_tb(tb,work_band,role=0, phase=1, tonemask=plc_packet_helper.TONEMASK_INVALID):
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "not PlcSystemTestbench"
    tb._init_band_param(work_band, tonemask)
    result = test_frame_helper.build_activate_req(dict_content = {
        'role': role,
        'band': work_band,
        'phase': phase,
        'tonemask': tonemask,
        })
    cf = result['cf']
    frame_body = result['body']
    tb.tb_uart.send_test_frame(frame_body, cf)
    test_frame = tb.tb_uart.wait_for_test_frame("ACTIVATE_CNF_CMD")
    assert test_frame is not None, 'ACTIVATE_CNF Timeout'
    assert test_frame.payload.error_code == "ACT_NO_ERROR", 'Wrong error_code {}'.format(test_frame.payload.error_code)

def trig_event_report(tb):
    tb.set_event_high()

    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "not PlcSystemTestbench"
    result = test_frame_helper.build_evt_trig_req()
    cf = result['cf']
    frame_body = result['body']
    tb.tb_uart.send_test_frame(frame_body, cf)
    test_frame = tb.tb_uart.wait_for_test_frame("EVT_TRIG_CNF_CMD")
    assert test_frame is not None, 'EVT_TRIG_CNF_CMD Timeout'
    """

def untrig_event_report(tb):
    tb.set_event_low()


#645 meter read reply frame produce
def send_dlt645_reply_frame(m,addr,di,data,data_len):
    assert isinstance(m, meter.Meter),"m type is not meter.Meter"

    frame = meter.build_dlt645_07_frame(dict_content={
        'head':{
                  'addr': addr,
                  'dir': 'REPLY_FRAME',
                  'reply_flag': 'NORMAL_REPLY',
                  'more_flag': 'NO_MORE_DATA',
                  'code': 'DATA_READ',
                  'len': 4 + data_len
                  },
                'body':{
                    #there is a RawCopy, so 'value' is a must
                    'value':{
                          'DI0':di[0],
                          'DI1':di[1],
                          'DI2':di[2],
                          'DI3':di[3],
                          'data': data
                  }
                },

                'tail':
                  {'cs':0}
                  })

    assert frame is not None
    m.send_frame(frame)
    return frame


#645 meter addr read reply
# addr: meter address string, e.g. "00-00-00-00-00-01", 未加过0x33
def send_dlt645_addr_read_reply_frame(m,addr):
    assert isinstance(m, meter.Meter),"m type is not meter.Meter"

    # 加0x33
    addr_new = addr.split('-')
    addr_new=["{:X}".format(int(d,16)+0x33) for d in addr_new]
    addr_new = "-".join(addr_new)
    frame = meter.build_dlt645_07_frame(dict_content={
        'head':{
                  'addr': addr,
                  'dir': 'REPLY_FRAME',
                  'reply_flag': 'NORMAL_REPLY',
                  'more_flag': 'NO_MORE_DATA',
                  'code': 'ADDR_READ',
                  'len': 6
                  },
                'body':{
                    #there is a RawCopy, so 'value' is a must
                    'value':{
                          'addr':addr_new
                  }
                },

                'tail':
                  {'cs':0}
                  })

    assert frame is not None
    m.send_frame(frame)
    return frame

# di: 数据标识，未+0x33
def create_dlt645_data_read_req_frame(addr, di):
    ditmp = [d+0x33 for d in di]
    frame = meter.build_dlt645_07_frame(dict_content={
        'head':{
                'addr': addr,
                'dir': 'REQ_FRAME',
                'reply_flag': None,
                'more_flag': None,
                'code': 'DATA_READ',
                'len': 4
               },
        'body':{
                #there is a RawCopy, so 'value' is a must
                'value':{
                        'DI0':ditmp[0],
                        'DI1':ditmp[1],
                        'DI2':ditmp[2],
                        'DI3':ditmp[3],
                        }
                },

        'tail':
            {'cs':0}
    })

    return frame



def send_comm_test_command(test_mode_cmd, param, tmi_b=4, tmi_e=0):
    tb = plc_tb_ctrl.TB_INSTANCE
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "not plc_tb_ctrl.PlcSystemTestbench"

    comm_test_dl_packet = dict(header=dict(port=0x11, sec_mode=0, id='APL_COMM_TEST', ctrl_word=0),
                               body=dict(proto_ver='PROTO_VER1', test_mode_cmd=test_mode_cmd,
                                         prot_type='PROTO_DLT645_2007', length=param,
                                         data=None))

    msdu = plc_packet_helper.build_apm(dict_content=comm_test_dl_packet, is_dl=True)
    plc_tb_ctrl._trace_byte_stream("msdu", msdu)

    tb.mac_head.org_dst_tei = 0xFFF
    tb.mac_head.org_src_tei = 0
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb.fc.nid = 0
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, broadcast_flag=1,
                  tmi_b=tmi_b, pb_num=1, src_tei=0, dst_tei=0xFFF, tx_time=0, auto_retrans=False)

    plc_tb_ctrl._debug('wait for TX_COMPLETE_IND')
    test_frame = tb.tb_uart.wait_for_test_frame("TX_COMPLETE_IND")
    assert test_frame is not None, 'TX_COMPLETE_IND Timeout'

'''
发送指定TMI的SOF帧，返回fc_pl_data对象
'''
def send_sof_fc_pl_data(tmi_b=0, tmi_e=0, pb_num=1, ack_needed=False):
    tb = plc_tb_ctrl.TB_INSTANCE

    # 生成FC
    sym_num = tb.tonemask_param.calc_payload_sym_num(tmi_b, tmi_e, pb_num)
    frame_len = plc_packet_helper.calc_frame_len(sym_num, ack_needed)
    fc = dict(mpdu_type='PLC_MPDU_SOF', network_type=0, nid=1, crc=0)
    sof_var_region_ver = dict(lid=1, dst_tei=0xFFF, src_tei=1, pb_num=pb_num,
                              frame_len=frame_len, tmi_b=tmi_b,
                              encrypt_flag=0, retrans_flag=0, broadcast_flag=1,
                              symbol_num=sym_num, ver=0, tmi_e=tmi_e)
    fc['var_region_ver'] = sof_var_region_ver
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sof_fc[0:13])
    fc['crc'] = fc_crc
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sof_fc is not None, "sof_fc is none"

    # 生成sof payload
    pb_size = plc_packet_helper.query_pb_size_by_tmi(tmi_b, tmi_e)
    sof_payload = plc_packet_helper.gen_sof_pb(pb_size, pb_num)

    # 生成fc_pl_data的payload
    payload = sof_fc + sof_payload

    fc_pl_data = dict(timestamp=0, pb_size=pb_size, pb_num=pb_num, phase=1, payload=dict(data=payload))
    tb._send_fc_pl_data(fc_pl_data)

    return fc_pl_data

'''
发送SACK帧，返回fc_pl_data对象
'''
def send_sack_fc_pl_data():
    tb = plc_tb_ctrl.TB_INSTANCE

    # 生成FC
    fc = dict(mpdu_type='PLC_MPDU_SACK', network_type=0, nid=1, crc=0)
    sack_var_region_ver = dict(rx_result=0, rx_status=1, dst_tei=0xFFF,
                               src_tei=1, rx_pb_num=1, chan_quality=0xFF,
                               load=0, ext_frame_type=0, ver=0)
    fc['var_region_ver'] = sack_var_region_ver
    sack_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sack_fc[0:13])
    fc['crc'] = fc_crc
    sack_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sack_fc is not None, "sack_fc is none"

    # 生成fc_pl_data的payload
    payload = sack_fc

    fc_pl_data = dict(timestamp=0, pb_size=0, pb_num=0, phase=1, payload=dict(data=payload))
    tb._send_fc_pl_data(fc_pl_data)

    return fc_pl_data

'''
发送指定TMI的SOF帧，返回fc_pl_data对象
'''
def send_periodic_sof_fc_pl_data(tmi_b=0, tmi_e=0, pb_num=1,
                                 ack_needed=False, tx_interval=100,
                                 tx_num=500, beacon_period=100, beacon_num=5,
                                 beacon_interval=1000):
    tb = plc_tb_ctrl.TB_INSTANCE

    # 生成FC
    sym_num = tb.tonemask_param.calc_payload_sym_num(tmi_b, tmi_e, pb_num)
    frame_len = plc_packet_helper.calc_frame_len(sym_num, ack_needed)
    fc = dict(mpdu_type='PLC_MPDU_SOF', network_type=0, nid=1, crc=0)
    sof_var_region_ver = dict(lid=1, dst_tei=0xFFF, src_tei=1, pb_num=pb_num,
                              frame_len=frame_len, tmi_b=tmi_b,
                              encrypt_flag=0, retrans_flag=0, broadcast_flag=1,
                              symbol_num=sym_num, ver=0, tmi_e=tmi_e)
    fc['var_region_ver'] = sof_var_region_ver
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sof_fc[0:13])
    fc['crc'] = fc_crc
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sof_fc is not None, "sof_fc is none"

    # 生成sof payload
    pb_size = plc_packet_helper.query_pb_size_by_tmi(tmi_b, tmi_e)
    sof_payload = plc_packet_helper.gen_sof_pb(pb_size, pb_num)

    # 生成fc_pl_data的payload
    payload = sof_fc + sof_payload

    fc_pl_data = dict(timestamp=0, tx_num=tx_num, tx_interval=tx_interval,
                      pb_size=pb_size, beacon_period=beacon_period,
                      beacon_interval=beacon_interval, beacon_num=beacon_num,
                      pb_num=pb_num, phase=1, payload=dict(data=payload))
    tb._send_periodic_fc_pl_data(fc_pl_data)

    return fc_pl_data


'''
发送SACK帧，返回fc_pl_data对象
'''
def send_periodic_sack_fc_pl_data():
    tb = plc_tb_ctrl.TB_INSTANCE

    # 生成FC
    fc = dict(mpdu_type='PLC_MPDU_SACK', network_type=0, nid=1, crc=0)
    sack_var_region_ver = dict(rx_result=0, rx_status=1, dst_tei=0xFFF,
                               src_tei=1, rx_pb_num=1, chan_quality=0xFF,
                               load=0, ext_frame_type=0, ver=0)
    fc['var_region_ver'] = sack_var_region_ver
    sack_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sack_fc[0:13])
    fc['crc'] = fc_crc
    sack_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sack_fc is not None, "sack_fc is none"

    # 生成fc_pl_data的payload
    payload = sack_fc

    fc_pl_data = dict(timestamp=0, tx_num=tx_num, tx_interval=tx_interval,
                      pb_size=0, beacon_period=beacon_period,
                      beacon_interval=beacon_interval, beacon_num=beacon_num,
                      pb_num=0, phase=1, payload=dict(data=payload))
    tb._send_periodic_fc_pl_data(fc_pl_data)

    return fc_pl_data

'''
使用mac_frame构造fc_pl_data对象, mac_frame为str对象的字节流
'''
def build_sof_fc_pl_data(mac_frame, pb_size, pb_num, pb_start_sn, total_pb_num):
    tb = plc_tb_ctrl.TB_INSTANCE

    if 72 == pb_size:
        tmi_b = 14
        tmi_e = 0
    elif 136 == pb_size:
        tmi_b = 4
        tmi_e = 0
    elif 264 == pb_size:
        tmi_b = 12
        tmi_e = 0
    elif 520 == pb_size:
        tmi_b = 9
        tmi_e = 0
    else:
        AssertionError("wrong pb_size {}".format(pb_size))

    # 生成FC
    sym_num = tb.tonemask_param.calc_payload_sym_num(tmi_b, tmi_e, pb_num)
    frame_len = plc_packet_helper.calc_frame_len(sym_num, False)
    fc = dict(mpdu_type='PLC_MPDU_SOF', network_type=0, nid=1, crc=0)
    sof_var_region_ver = dict(lid=1, dst_tei=0xFFF, src_tei=1, pb_num=pb_num,
                              frame_len=frame_len, tmi_b=tmi_b,
                              encrypt_flag=0, retrans_flag=0, broadcast_flag=1,
                              symbol_num=sym_num, ver=0, tmi_e=tmi_e)
    fc['var_region_ver'] = sof_var_region_ver
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sof_fc[0:13])
    fc['crc'] = fc_crc
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sof_fc is not None, "sof_fc is none"

    sof_payload = ''
    for i in range(pb_num):
        sof_payload += plc_packet_helper.build_sof_one_pb(mac_frame, pb_size, pb_start_sn+i, total_pb_num)

    # 生成fc_pl_data的payload
    payload = sof_fc + sof_payload

    fc_pl_data = dict(timestamp=0, pb_size=pb_size, pb_num=pb_num, phase=1, payload=dict(data=payload))

    return fc_pl_data

'''
使用mac_frame构造fc_pl_data对象, mac_frame为str对象的字节流, FC参数可以自定义
'''
def build_sof_fc_pl_data_ex(mac_frame, nid, src_tei, dst_tei, tmi_b=None, tmi_e=None, pb_num=None, ack_needed=True, encrypt_flag=0,
                            lid=0, retrans_flag=0, broadcast_flag=0, pb_start_sn=0, total_pb_num=None, timestamp=0xFFFFFFFF):

    tb = plc_tb_ctrl.TB_INSTANCE

    fc = dict(mpdu_type='PLC_MPDU_SOF', network_type=0, nid=nid, crc=0)

    if (tmi_b is None) and (tmi_e is None):
        pb_format = plc_packet_helper.calc_pb_format(tb.tonemask_param, plc_packet_helper.MAC_MPDU_SOF, data_size)
        frame_len = plc_packet_helper.calc_frame_len(pb_format['sym_num'], ack_needed)

        sof_var_region_ver = dict(lid=lid, dst_tei=dst_tei, src_tei=src_tei,
                                  pb_num=pb_format['pb_num'], frame_len=frame_len, tmi_b=pb_format['tmi_basic_mode'], encrypt_flag=encrypt_flag,
                                  retrans_flag=retrans_flag, broadcast_flag=broadcast_flag, symbol_num=pb_format['sym_num'],
                                  ver=0, tmi_e=pb_format['tmi_ext_mode'])

        total_pb_num = pb_format['pb_num']
        pb_size = pb_format['pb_size']
    else:
        # 生成FC
        sym_num = tb.tonemask_param.calc_payload_sym_num(tmi_b, tmi_e, pb_num)
        frame_len = plc_packet_helper.calc_frame_len(sym_num, False)

        assert pb_num is not None, "pb_num is None"
        sof_var_region_ver = dict(lid=lid, dst_tei=dst_tei, src_tei=src_tei, pb_num=pb_num,
                                  frame_len=frame_len, tmi_b=tmi_b,
                                  encrypt_flag=encrypt_flag, retrans_flag=retrans_flag,
                                  broadcast_flag=broadcast_flag,
                                  symbol_num=sym_num, ver=0, tmi_e=tmi_e)

        if total_pb_num is None:
            total_pb_num = pb_num

        pb_size = plc_packet_helper.query_pb_size_by_tmi(tmi_b, tmi_e)

    fc['var_region_ver'] = sof_var_region_ver
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    fc_crc = plc_packet_helper.calc_crc24(sof_fc[0:13])
    fc['crc'] = fc_crc
    sof_fc = plc_packet_helper.build_mpdu_fc(dict_content=fc)
    assert sof_fc is not None, "sof_fc is none"

    sof_payload = ''
    for i in range(pb_num):
        sof_payload += plc_packet_helper.build_sof_one_pb(mac_frame, pb_size, pb_start_sn+i, total_pb_num)

    # 生成fc_pl_data的payload
    payload = sof_fc + sof_payload

    fc_pl_data = dict(timestamp=timestamp, pb_size=pb_size, pb_num=pb_num, phase=1, payload=dict(data=payload))

    return fc_pl_data

# convert str type to list type
def convert_str2lst(src_str=None, dst_lst=None):
    if (src_str != None) and (dst_lst != None):
        for i in range (len(src_str)):
            dst_lst.append(ord(src_str[i]))
    return dst_lst


def calc_timeout(timeout):
    return timeout*config.CLOCK_RATE


def apl_sta_rx_one_apm_ul(tb_inst, pkt_id = None, time_out = 3, timeout_cb = None):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    result = [None, None, None, None]
    time_out = calc_timeout(time_out)
    time_stop = time.time() + time_out
    while True:
        if time_stop <= time.time():
            break

        [timestamp, fc, mac_frame_head, apm] = tb_inst._wait_for_plc_apm_ul(pkt_id, time_out, timeout_cb)

    #    plc_tb_ctrl._debug("mac_frame_head = {}".format(mac_frame_head))

        if mac_frame_head is None:
            continue

        if apm.header.id  == pkt_id:
            result = [timestamp, fc, mac_frame_head, apm]
            break

    return result

def wait_for_tx_complete_ind(tb_inst, time_out = 2):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    time_out = calc_timeout(time_out)
    time_stop = time.time() + time_out

    plc_tb_ctrl._debug('wait for TX_COMPLETE_IND')
    while True:
        if time_stop <= time.time():
            break

        test_frame = tb_inst.tb_uart.wait_for_test_frame("TX_COMPLETE_IND", time_out, False)
        if test_frame is not None:
            plc_tb_ctrl._debug('TX_COMPLETE_IND received')
            return

    plc_tb_ctrl._debug('TX_COMPLETE_IND Timeout')
    return

def send_nml_heart_beat(tb_inst, sta_tei=2, cco_tei=1):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    plc_tb_ctrl._debug('Send out nml heart beat pkt to CCO')

    pkt = tb_inst._load_data_file(data_file='nml_heartbeat_report.yaml')
    assert pkt is not None,                    'failed to load nml_heartbeat_report.yaml'

    pkt['body']['org_src_tei']   = sta_tei
    pkt['body']['good_ear_tei']  = sta_tei

    plc_tb_ctrl._debug(pkt)
    msdu = plc_packet_helper.build_nmm(dict_content=pkt)

    tb_inst.mac_head.org_dst_tei = cco_tei
    tb_inst.mac_head.org_src_tei = sta_tei
    tb_inst.mac_head.msdu_type   = "PLC_MSDU_TYPE_NMM"

    tb_inst._send_msdu(msdu, tb_inst.mac_head, src_tei=sta_tei, dst_tei=cco_tei,auto_retrans=False)

 #   wait_for_tx_complete_ind(tb_inst)

    return

########################################################################
#     模拟DUT入网
########################################################################
# DUT == CCO
def apl_cco_network_connect(tb_inst, cct_inst, cco_addr, sta_addr):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench), "tb_inst  type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct_inst, concentrator.Concentrator),     "cct_inst type is not concentrator.Concentrator"

    plc_tb_ctrl._debug("apl_cco_network_connect: de-activate tb")
    tb_inst._deactivate_tb()

    plc_tb_ctrl._debug("apl_cco_network_connect: activate tb")
    activate_tb(tb_inst, work_band = 1)
    cct_inst.clear_port_rx_buf()
    time.sleep(1)

    plc_tb_ctrl._debug("apl_cco_network_connect: set CCO addr={}".format(cco_addr))
    set_cco_mac_addr(cct_inst,cco_addr)

    #set sub node address
    plc_tb_ctrl._debug("apl_cco_network_connect: set SUB NODE addr={}".format(sta_addr))
    sub_nodes_addr = [sta_addr]
    add_sub_node_addr(cct_inst, sub_nodes_addr)

    #wait for beacon from DUT
    plc_tb_ctrl._debug("apl_cco_network_connect: wait for beacon from DUT")
    [beacon_fc, beacon_payload] = tb_inst._wait_for_plc_beacon(60)[1:]

    #sync the nid and sn between tb and DTU
    plc_tb_ctrl._debug("apl_cco_network_connect: sync nid and nw_sn")
    sync_tb_configurations(tb_inst, beacon_fc.nid, beacon_payload.nw_sn)

    #send association request to DUT
    plc_tb_ctrl._debug("apl_cco_network_connect: send MME_ASSOC_REQ to DUT")

    tb_inst.mac_head.org_dst_tei   = 1
    tb_inst.mac_head.org_src_tei   = 0
    tb_inst.mac_head.mac_addr_flag = 1
    tb_inst.mac_head.src_mac_addr  = sta_addr
    tb_inst.mac_head.dst_mac_addr  = cco_addr
    tb_inst._send_nmm('nml_assoc_req.yaml', tb_inst.mac_head, src_tei = 0, dst_tei = 1)

    wait_for_tx_complete_ind(tb_inst)

    plc_tb_ctrl._debug("apl_cco_network_connect: wait for MME_ASSOC_CNF or  MME_ASSOC_GATHER_IND from DUT")
    [fc, mac_frame_head, nmm] = tb_inst._wait_for_plc_nmm(['MME_ASSOC_CNF','MME_ASSOC_GATHER_IND'], timeout = 60)
#    plc_tb_ctrl._debug("rx nmm = {}".format(nmm))

    assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc fail"

    return nmm.body.tei_sta

# DUT == STA
def apl_sta_network_connect(tb_inst, m_inst, cco_mac, meter_addr, sta_tei, beacon_loss=0, beacon_proxy_flag=0, need_tb_deactive=False):

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(m_inst, meter.Meter),"m_inst type is not meter.Meter"

    m_inst.clear_port_rx_buf()
    time.sleep(1)

#    if need_tb_deactive:
#        plc_tb_ctrl._debug("apl_sta_network_connect: de-activate tb")
#        tb_inst._deactivate_tb()
    plc_tb_ctrl._debug("apl_sta_network_connect: de-activate tb")
    tb_inst._deactivate_tb()

    plc_tb_ctrl._debug("apl_sta_network_connect: activate tb")
    activate_tb(tb_inst,work_band = 1)

    # 软件平台(电能表)模拟电表，在收到待测STA请求读表号后，向其下发电表地址信息()。
    #wait for meter read request
    plc_tb_ctrl._debug("apl_sta_network_connect: wait for meter request")

    sta_init(m_inst, meter_addr)

    if beacon_loss == 1:     # do not send the beacon, that is, reject STA to connect the network
        return

    # 软件平台模拟CCO通过透明物理设备向待测STA设备发送“中央信标”，
    # 在收到待测STA发出的“关联请求”后，向其发送“关联确认”，令其入网；
    #send beacon periodically
    plc_tb_ctrl._debug("apl_sta_network_connect: send beacon periodically")

    beacon_dict = tb_inst._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb_inst._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    plc_tb_ctrl._debug("apl_sta_network_connect: config nid and nw_sn")

    tb_inst._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    plc_tb_ctrl._debug("apl_sta_network_connect: wait for MME_ASSOC_REQ")

    [fc, mac_frame_head, nmm] = tb_inst._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)

    #send associate confirm to STA
    plc_tb_ctrl._debug("apl_sta_network_connect: send nml_assoc_cnf to sta")

    asso_cnf_dict = tb_inst._load_data_file('nml_assoc_cnf.yaml')
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn']  = nmm.body.p2p_sn
    asso_cnf_dict['body']['tei_sta'] = sta_tei

#    plc_tb_ctrl._debug("asso_cnf_dict={}".format(asso_cnf_dict))

    #config the mac header
    tb_inst.mac_head.org_dst_tei   = 0
    tb_inst.mac_head.org_src_tei   = 1
    tb_inst.mac_head.mac_addr_flag = 1
    tb_inst.mac_head.src_mac_addr  = cco_mac
    tb_inst.mac_head.dst_mac_addr  = meter_addr
    tb_inst.mac_head.tx_type       = 'PLC_LOCAL_BROADCAST'

    tb_inst.mac_head.msdu_sn       = 0
    tb_inst.mac_head.msdu_len      = 0
    tb_inst.mac_head.msdu_type     = 'PLC_MSDU_TYPE_NMM'
    tb_inst.mac_head.broadcast_dir = 0

#    plc_tb_ctrl._debug("tb_inst.mac_head={}".format(tb_inst.mac_head))
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb_inst._configure_nw_static_para(nid, nw_org_sn)
    tb_inst._send_msdu(msdu, tb_inst.mac_head, src_tei = 1, dst_tei = 0, broadcast_flag = 1)

    wait_for_tx_complete_ind(tb_inst)

    if beacon_proxy_flag == 0:
        return

    # configure STA to act as PCO
    plc_tb_ctrl._debug("apl_sta_network_connect: configure STA to act as PCO")

    ncb_info = {'tei': sta_tei, 'type': 1}
    slot_alloc_item = beacon_dict['payload']['value']['beacon_info']['beacon_item_list'][2]['beacon_item']
    slot_alloc_item['ncb_slot_num'] = 1
    slot_alloc_item['ncb_info'].append(ncb_info)

    pco_active_delay = slot_alloc_item['beacon_period_len'] / 1000

    tb_inst._configure_beacon(None, beacon_dict, update_beacon=True)
    time.sleep(pco_active_delay)     # wait for this action to take effect
    return


def check_nw_top(cct, nw_top, timeout=120):
    assert isinstance(cct, concentrator.Concentrator), "tb type is not plc_tb_ctrl.PlcSystemTestbench"
    succ = False
    node_num = len(nw_top)
    # 复制拓扑图
    out_nw_top = dict(nw_top)
    try:
        if  out_nw_top.has_key(cct.mac_addr):
            del out_nw_top[cct.mac_addr]
    except KeyError:
        pass
    else:
        pass
    start_time = time.time()
    stop_time = start_time + calc_timeout(timeout)
    timeoutcounter = 0
    while True:
        afn10f21_ul_frame = query_nw_top(cct, 1, 61)
        if afn10f21_ul_frame is None:
            timeoutcounter += 1
            cct.clear_port_rx_buf()
            cct.close_port()
            time.sleep(0.5)
            cct.open_port()
            assert timeoutcounter < 3, "read cco top info fail"
            continue
        else:
            timeoutcounter = 0
        data = afn10f21_ul_frame.user_data.value.data.data

        plc_tb_ctrl._debug("node num: {}".format(data.total_num))
        for n in data.node_list:
            if out_nw_top.has_key(n.addr):
                del out_nw_top[n.addr]
        if  out_nw_top.__len__() < 10:
            plc_tb_ctrl._debug(out_nw_top)

        if ((data.total_num >= node_num) and (data.curr_num >= node_num)):
            plc_tb_ctrl._debug("nw established within {:.2f} seconds".format(time.time() - start_time))
            for node in data.node_list:
                if nw_top.has_key(node.addr):
                    assert nw_top[node.addr] <= node.level, "{} expect: {} actual: {}".format(node.addr, str(nw_top[node.addr]), str(node.level))
                    if 0 == node.level:
                        assert 1 == node.sta_tei, "invalid CCO TEI"
                        assert 0 == node.proxy_tei, "invalid proxy TEI"
                        assert "ROLE_CCO" == node.role, "{} should be CCO".format(node.addr)
                    # elif (node.level < level_num):
                    #     assert "ROLE_PCO" == node.role, "{} should be PCO".format(node.addr)
                    # else:
                    #     assert "ROLE_STA" == node.role, "{} should be STA".format(node.addr)
                elif node.level == 0:
                    # TODO: 海思CCO没有更新MAC地址z
                    pass
                else:
                    assert False, "invalid node address {},{}".format(node.addr, nw_top)

            succ = True
            break

        if time.time() > stop_time:
            break

        time.sleep((node_num - data.curr_num) // 10 + 1)

    if (succ):
        plc_tb_ctrl._debug("nw established within {:.2f} seconds".format(time.time() - start_time))
    else:
        assert False, ("fail to complete nw establishment within {:.2f} seconds".format(time.time() - start_time))

def pause_exec(message):
    plc_tb_ctrl._debug(message)
    Dialogs.pause_execution(message)

# 检查抄表结果
# dlt645_frame: string
# di_list: DI列表，每个元素即一个数据标识
def verify_mr_result(dlt645_frame, di_list):
    for di in di_list:
        di = [d+0x33 for d in di]

        parsed_frame = meter.parse_dlt645_07_frame(dlt645_frame)

        if parsed_frame is None:
            plc_tb_ctrl._debug("invalid dlt645 frame")
            return False

        if ('DATA_READ' != parsed_frame.head.code):
            plc_tb_ctrl._debug("wrong dlt645 code {}".format(parsed_frame.head.code))
            return False

        if ('NORMAL_REPLY' != parsed_frame.head.reply_flag):
            plc_tb_ctrl._debug("abnormal reply")
            return False

        if ((parsed_frame.body.value.DI0 != di[0])
                or (parsed_frame.body.value.DI1 != di[1])
                or (parsed_frame.body.value.DI2 != di[2])
                or (parsed_frame.body.value.DI3 != di[3])):

            plc_tb_ctrl._debug("mismatched DI")
            return False

        frame_len = meter.calc_dlt645_07_frame_len(parsed_frame)
        dlt645_frame = dlt645_frame[frame_len:]

    return True


# 使用13F1点抄STA
def exec_cct_mr_single(tb, cct, cco_addr, sta_addr, timeout, num, di_list):
    succ_cnt = 0
    total_time_used = 0
    sn = 0
    for i in range(num):
        dl_afn13f1_pkt = tb._load_data_file(data_file='afn13f1_dl.yaml')
        for sta in sta_addr:
            for di in di_list:
                sn += 1
                dl_afn13f1_pkt['cf']['prm']  = 'MASTER'
                dl_afn13f1_pkt['user_data']['value']['r']['comm_module_flag']  = 1
                dl_afn13f1_pkt['user_data']['value']['r']['sn'] = i
                dl_afn13f1_pkt['user_data']['value']['a']['src'] = cco_addr
                dl_afn13f1_pkt['user_data']['value']['a']['dst'] = sta
                dlt645_frame = create_dlt645_data_read_req_frame(sta, di)
                dl_afn13f1_pkt['user_data']['value']['data']['data']['packet_len'] = len(dlt645_frame)
                dl_afn13f1_pkt['user_data']['value']['data']['data']['packet'] = [ord(d) for d in dlt645_frame]

                msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn13f1_pkt)
                assert msdu is not None

                start_time = time.time()
                cct.send_frame(msdu)

                gdw1376p2_frame = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=timeout, tm_assert=False)
                time_used = time.time() - start_time

                if gdw1376p2_frame is None:
                    result = "[{}]: FAIL".format(i)
                else:
                    afn13f1_data = gdw1376p2_frame.user_data.value.data.data
                    if 0 == afn13f1_data.packet_len:
                        continue

                    dlt645_frame = "".join([chr(d) for d in afn13f1_data.packet])
                    if (verify_mr_result(dlt645_frame, [di])):
                        succ_cnt += 1
                        result = "[{}]: SUCC. Time: {:.2f} second".format(i, time_used)
                        total_time_used += time_used

        plc_tb_ctrl._debug(result)
    total = num * len(sta_addr) * len(di_list)
    if succ_cnt > 0:
        plc_tb_ctrl._debug("Total: {}, Succ: {}, Percentage: {}%, Avg Time: {:.2f}".\
                        format(total, succ_cnt, round(succ_cnt * 100.0 / total), total_time_used / succ_cnt))
    else:
        plc_tb_ctrl._debug("Total: {}, Succ: {}, Percentage: {}%, Avg Time: {:.2f}".\
                        format(total, succ_cnt, round(succ_cnt * 100.0 / total), total_time_used))


# 使用F1F1并发抄读STA
def exec_cct_mr_multiple(tb, cct, cco_addr, sta_addr_list, timeout, num, di_list):
    succ_cnt = 0
    total_time_used = 0
    sn = 0
    for i in range(num):
        dl_afnf1f1_pkt = tb._load_data_file(data_file='afnf1f1_dl_empty.yaml')
        start_time = []
        for sta_addr in sta_addr_list:
            sn += 1
            dl_dlt645 = ''
            for di in di_list:
                frame = create_dlt645_data_read_req_frame(sta_addr, di)
                dl_dlt645 += frame

            dl_data_len = len(dl_dlt645)

            dl_afnf1f1_pkt['cf']['prm'] = 'MASTER'
            dl_afnf1f1_pkt['user_data']['value']['r']['comm_module_flag'] = 1
            dl_afnf1f1_pkt['user_data']['value']['r']['sn'] = sn
            dl_afnf1f1_pkt['user_data']['value']['a']['src'] = cco_addr
            dl_afnf1f1_pkt['user_data']['value']['a']['dst'] = sta_addr
            dl_afnf1f1_pkt['user_data']['value']['data']['data']['data_len'] = dl_data_len
            dl_afnf1f1_pkt['user_data']['value']['data']['data']['data'] = [ord(d) for d in dl_dlt645]

            msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afnf1f1_pkt)
            assert msdu is not None

            cct.send_frame(msdu)

        sta_addr_list_copy = sta_addr_list[:]
        start_time = time.time()
        stop_time = time.time() + calc_timeout(timeout)
        succ = True
        timeout_copy = calc_timeout(timeout)
        while len(sta_addr_list_copy) > 0:
            gdw1376p2_frame = cct.wait_for_gdw1376p2_frame(afn=0xF1, dt1=0x01, dt2=0, timeout=timeout_copy, tm_assert=False)
            timeout_copy = stop_time - time.time()
            if gdw1376p2_frame is None:
                succ = False
                break
            else:
                src_addr = gdw1376p2_frame.user_data.value.a.src
                if (src_addr in sta_addr_list_copy):
                    sta_addr_list_copy.remove(src_addr)
                    afnf1f1_data = gdw1376p2_frame.user_data.value.data.data
                    if afnf1f1_data.data_len == 0:
                        plc_tb_ctrl._debug("{}: data_Len is 0 ".format(src_addr))
                        succ = False
                        break

                    dlt645_frame = "".join([chr(d) for d in afnf1f1_data.data])
                    if (not verify_mr_result(dlt645_frame, di_list)):
                        plc_tb_ctrl._debug("mr result mismatch")
                        succ = False
                        break

        time_used = time.time() - start_time

        if not succ:
            result = "[{}]: FAIL".format(i)
        else:
            succ_cnt += 1
            result = "[{}]: SUCC. Time: {:.2f} second".format(i, time_used)
            total_time_used += time_used

        plc_tb_ctrl._debug(result)

    if succ_cnt > 0:
        plc_tb_ctrl._debug("Total: {}, Succ: {}, Percentage: {}%, Avg Time: {:.2f}".\
                        format(num, succ_cnt, round(succ_cnt * 100.0 / num), total_time_used / succ_cnt))
    else:
        plc_tb_ctrl._debug("Total: {}, Succ: {}, Percentage: {}%, Avg Time: {:.2f}".\
                        format(num, succ_cnt, round(succ_cnt * 100.0 / num), total_time_used))

def tx_gain_control(sitrace, afe_control=-1, afe_gain_db=0, dac_shift=0, reg1104='a3d400'):
    if afe_control>=0:
        if afe_control == 0:    #atheros, gain step = 2db
            afe_gain_cw = int(afe_gain_db + 24)/2
            if afe_gain_cw<0:
                afe_gain_cw = 0
            elif afe_gain_cw>15:
                afe_gain_cw = 15
        elif afe_control == 1:
            afe_gain_cw = int(6-afe_gain_db)/3
            if afe_gain_cw<0:
                afe_gain_cw = 0
            elif afe_gain_cw > 2:
                afe_gain_cw = 2
            afe_gain_cw = 128+afe_gain_cw
        afe_tx_ctrl_hex = "0x{:02x}".format(afe_gain_cw)+reg1104
        sitrace.send_cli_cmd("memwrite 32 0x50071104 "+afe_tx_ctrl_hex)
        plc_tb_ctrl._debug("afe tx gain is set, 0x50071104 = " + afe_tx_ctrl_hex)
        time.sleep(0.5)

    if dac_shift<0:
        dac_shift_cw = dac_shift + 16
    else:
        dac_shift_cw = dac_shift
    dac_shift_hex = "0x000{:x}".format(dac_shift_cw) + "01FF"
    sitrace.send_cli_cmd("memwrite 32 0x500711fc " + dac_shift_hex)
    plc_tb_ctrl._debug("DAC tx gain is set, 0x500711fc = "+dac_shift_hex)
    time.sleep(0.5)

def tx_inbandpwr_measure(scope, band, fs=50E+6, differential_en=0, channel=1, detect_type=1):
    # 校准示波器的频谱测量功能
    result = None
    if (band == 0):
        sample_len = 25E+3
        time_pos = 250E-6
        fc_meas = 7000000
        bw_meas = 9000000
    elif (band == 1):
        sample_len = 50E+3
        time_pos = 500E-6
        fc_meas = 4000000
        bw_meas = 2500000
    elif (band == 2):
        sample_len = 50E+3
        time_pos = 500E-6
        fc_meas = 1855000
        bw_meas = 2000000
    else:
        sample_len = 2E+6
        time_pos = 2E-3
        fc_meas = 2344000
        bw_meas = 1000000

    sample_len = sample_len * config.CLOCK_RATE
    time_pos = time_pos * config.CLOCK_RATE
    #fs = 50E+6
    voltage_range = 10.0
    trigger_level = 0.3
    #differential_en = 0
    scope.capture_timedomain_waveform(fs, sample_len, voltage_range, 0, time_pos * 2, trigger_level,
                                         differential_en, time_pos, channel)
    Vmax = scope.measure_Vmax(channel=channel)
    #plc_tb_ctrl._debug("###################Vmax: {}V".format(Vmax))
    voltage_range = Vmax * 2.5
    trigger_level = Vmax * 0.4
    scope.capture_timedomain_waveform(fs, sample_len, voltage_range, 0, time_pos * 2, trigger_level,
                                         differential_en, time_pos,channel)
    f_start = 250000 / config.CLOCK_RATE
    f_end = 50000000 / config.CLOCK_RATE
    f_center = fc_meas / config.CLOCK_RATE
    bw = bw_meas / config.CLOCK_RATE
    scope.function_fft(f_start, f_end, 10, -10,channel,detect_type)
    result1 = scope.measure_fft(f_center, bw, 99)
    time.sleep(2)
    result1 = scope.query_fft_meas_result(f_center, bw, 99)

    if (result1[0] != None):
        channel_pwr = result1[0]
        psd_inband = result1[1]
        result = [channel_pwr, psd_inband]

    return result

def tx_psd_measure(scope, band, fs=100E+6, differential_en=0, channel=1, detect_type=1):
    # 校准示波器的频谱测量功能
    result = None
    if (band == 0):
        sample_len = 50E+3
        time_pos = 250E-6
        fc_meas = 7000000
        bw_meas = 10000000
    elif (band == 1):
        sample_len = 100E+3
        time_pos = 500E-6
        fc_meas = 4000000
        bw_meas = 2500000
    elif (band == 2):
        sample_len = 100E+3
        time_pos = 500E-6
        fc_meas = 1855000
        bw_meas = 2000000
    else:
        sample_len = 4E+6
        time_pos = 2E-3
        fc_meas = 2344000
        bw_meas = 1000000
    outband1_bw = 37000000
    outband2_bw = 450000
    sample_len = sample_len * config.CLOCK_RATE
    time_pos = time_pos * config.CLOCK_RATE
    #fs = 50E+6
    voltage_range = 10.0
    trigger_level = 0.3
    #differential_en = 0
    scope.capture_timedomain_waveform(fs, sample_len, voltage_range, 0, time_pos * 2, trigger_level,
                                         differential_en, time_pos, channel)
    Vmax = scope.measure_Vmax(channel=channel)
    #plc_tb_ctrl._debug("###################Vmax: {}V".format(Vmax))
    voltage_range = Vmax * 2.5
    trigger_level = Vmax * 0.4
    scope.capture_timedomain_waveform(fs, sample_len, voltage_range, 0, time_pos * 2, trigger_level,
                                         differential_en, time_pos,channel)
    f_start = 250000 / config.CLOCK_RATE
    f_end = 50000000 / config.CLOCK_RATE
    f_center = fc_meas / config.CLOCK_RATE
    bw = bw_meas / config.CLOCK_RATE
    plc_tb_ctrl._debug("inband:  f_center:{}MHz, bw:{}MHz".format(f_center/1000000.0, bw/1000000.0))
    scope.function_fft(f_start, f_end, 10, -10, channel, detect_type)
    result1 = scope.measure_fft(f_center, bw, 99)
    time.sleep(2)
    result1 = scope.query_fft_meas_result(f_center, bw, 99)

    # if (result1[0]  psd_inband]

    bw = outband1_bw / config.CLOCK_RATE
    f_center = (12500000 + (outband1_bw / 2)) / config.CLOCK_RATE
    # self.scope.function_fft(f_start, f_end, 10, -10)!= None):
    #     #     channel_pwr = result1[0]
    #     #     psd_inband = result1[1]
    #     #     result = [channel_pwr,
    plc_tb_ctrl._debug("upperband:  f_center:{}MHz, bw:{}MHz".format(f_center / 1000000.0, bw / 1000000.0))
    result2 = scope.measure_fft(f_center, bw, 99)
    time.sleep(2)
    result2 = scope.query_fft_meas_result(f_center, bw, 99)

    bw = outband2_bw / config.CLOCK_RATE
    f_center = (250000 + (outband2_bw / 2)) / config.CLOCK_RATE
    plc_tb_ctrl._debug("lowerband:  f_center:{}MHz, bw:{}MHz".format(f_center / 1000000.0, bw / 1000000.0))
    # self.scope.function_fft(f_start, f_end, 10, -10)
    result3 = scope.measure_fft(f_center, bw, 99)
    time.sleep(2)
    result3 = scope.query_fft_meas_result(f_center, bw, 99)

    result = [result1[0], result1[1], result2[1], result3[1]]

    return result

def get_cco_route_period_from_beacon(tb,cco_mac_addr,timeout=60):
    #wait for beacon from DTU
    start = time.time()
    while time.time() < start + timeout:
        [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(timeout)[1:]

        #sync the nid and sn between tb and DTU
        sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

        #check beacon payload
        #assert
        if beacon_payload.cco_mac_addr != cco_mac_addr:
            continue

        for item in beacon_payload.beacon_info.beacon_item_list:
            if item.head == 'ROUTE_PARAM':
                route_period = item.beacon_item.route_period
                assert route_period is not None
                return route_period


def sta_init(mtr, meter_addr='00-00-00-00-00-01'):
    #wait for meter read request
    plc_tb_ctrl._debug("wait for meter read request")
    dlt645_frame = mtr.wait_for_dlt645_frame(dir='REQ_FRAME', timeout=10)

    assert dlt645_frame is not None
    assert dlt645_frame.head.addr.upper() == 'AA-AA-AA-AA-AA-AA'
    if dlt645_frame.head.code == "ADDR_READ":
        assert dlt645_frame.head.len == 0
        #prepare reply frame for meter read request
        plc_tb_ctrl._debug("send reply to meter read request")
        send_dlt645_addr_read_reply_frame(mtr, meter_addr)
    elif dlt645_frame.head.code == "DATA_READ":
        assert dlt645_frame.head.len == 4
        reply_data = [1,2,3,4]
        reply_data = [d + 0x33 for d in reply_data]
        dis = [dlt645_frame.body.value.DI0,
               dlt645_frame.body.value.DI1,
               dlt645_frame.body.value.DI2,
               dlt645_frame.body.value.DI3]
        send_dlt645_reply_frame(mtr, meter_addr, dis, reply_data, len(reply_data))
    else:
        assert False, "unexpected 645 code"

# send afn03f16, 读取CCO频段
def read_cco_band(cct):
    assert isinstance(cct, concentrator.Concentrator)
    cct.clear_port_rx_buf()
    dl_afn03f16_pkt = plc_tb_ctrl.PlcSystemTestbench._load_data_file(data_file='afn03f16_dl.yaml')
    frame = concentrator.build_gdw1376p2_frame(dict_content=dl_afn03f16_pkt)  # end of dict_content

    assert frame is not None
    cct.send_frame(frame)
    # 等待回复
    afn03h16 = cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x80, dt2=1)
    return afn03h16.user_data.value.data.data.band

# send afn05f16, 设置CCO频段
def write_cco_band(cct, band):
    assert isinstance(cct, concentrator.Concentrator)
    cct.clear_port_rx_buf()
    if type(band) is not int:
        band = int(band)
    dl_afn05f16_pkt = plc_tb_ctrl.PlcSystemTestbench._load_data_file(data_file='afn05f16_dl.yaml')
    dl_afn05f16_pkt['user_data']['value']['data']['data']['band'] = band
    frame = concentrator.build_gdw1376p2_frame(dict_content=dl_afn05f16_pkt)
    assert frame is not None
    cct.send_frame(frame)
    # 等待确认
    cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)


def read_node_top_list(file, cco_mac_addr=None, log=False):
    # type: (unicode, str, bool) -> object
    """
    :param file: 电表地址和预期层级的txt文件
    :param cco_mac_addr: 如果赋值，那么拓扑信息中会带有cco的信息
    :return: 第一个值是拓扑信息字典，第二个是地址列表
    """
    f = open(file, 'r')
    addr_list = f.readlines()
    if cco_mac_addr is None:
        nw_top_main = { }
    else:
        nw_top_main = { cco_mac_addr : 0}
    for l in addr_list:
        # key is meter address, value is level
        key, value = l.split(':')
        nw_top_main[key] = int(value.strip())
    f.close()
    sec_nodes_addr_list = []
    for meter_addr, level in nw_top_main.iteritems():
        if (level > 0):
            sec_nodes_addr_list.append(meter_addr)
    if log:
        plc_tb_ctrl._debug(sec_nodes_addr_list)
    return nw_top_main, sec_nodes_addr_list

def wait_cco_power_on(tb, cct, *channel):
    '''
    :param tb:
    :param cct:
    :param channel: cco所在的继电器通道
    :return: None
    '''
    res = None
    for i in range(3):
        tb.meter_platform_power(channel)
        res = cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1, tm_assert=False)
        if res is None:
            continue
        else:
            break
    assert res is not None, "wait 03H_F10 failed, check cco device"
