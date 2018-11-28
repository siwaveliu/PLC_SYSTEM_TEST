# -- coding: utf-8 --
# STA 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import config
import serial
import plc_packet_helper
import time
import meter
import plc_packet_helper
from robot.api import logger
from construct import *
import test_data_reader
import test_frame_helper

Fadding_table = ['\x7e\x7e\x10\x00\x10','\x7e\x7e\x10\x0a\x1a','\x7e\x7e\x10\x14\x24','\x7e\x7e\x10\x1e\x2e',
    '\x7e\x7e\x10\x28\x38','\x7e\x7e\x10\x32\x42','\x7e\x7e\x10\x3c\x4c','\x7e\x7e\x10\x46\x56','\x7e\x7e\x10\x50\x60',
    '\x7e\x7e\x10\x5a\x6a','\x7e\x7e\x10\x64\x74','\x7e\x7e\x10\x6e\x7e','\x7e\x7e\x10\x78\x88']

#Fadding_table2 = ['\x7e\x7e\x10\x46\x56','\x7e\x7e\x10\x47\x57','\x7e\x7e\x10\x48\x58','\x7e\x7e\x10\x49\x59',
#    '\x7e\x7e\x10\x4a\x5a','\x7e\x7e\x10\x4b\x5b','\x7e\x7e\x10\x4c\x5c','\x7e\x7e\x10\x4d\x5d',
#    '\x7e\x7e\x10\x4e\x5e','\x7e\x7e\x10\x4f\x5f','\x7e\x7e\x10\x50\x60']

Fadding_table2 = [
    '\x7e\x7e\x10\x00\x10','\x7e\x7e\x10\x02\x12','\x7e\x7e\x10\x04\x14','\x7e\x7e\x10\x06\x16',
    '\x7e\x7e\x10\x08\x18','\x7e\x7e\x10\x0a\x1a','\x7e\x7e\x10\x0c\x1c','\x7e\x7e\x10\x0e\x1e',
    '\x7e\x7e\x10\x10\x20','\x7e\x7e\x10\x12\x22','\x7e\x7e\x10\x14\x24','\x7e\x7e\x10\x16\x26',
    '\x7e\x7e\x10\x18\x28','\x7e\x7e\x10\x1a\x2a','\x7e\x7e\x10\x1c\x2c','\x7e\x7e\x10\x1e\x2e',
    '\x7e\x7e\x10\x20\x30','\x7e\x7e\x10\x22\x32','\x7e\x7e\x10\x24\x34','\x7e\x7e\x10\x26\x36',
    '\x7e\x7e\x10\x28\x38','\x7e\x7e\x10\x2a\x3a','\x7e\x7e\x10\x2c\x3c','\x7e\x7e\x10\x2e\x3e',
    '\x7e\x7e\x10\x30\x40','\x7e\x7e\x10\x32\x42','\x7e\x7e\x10\x34\x44','\x7e\x7e\x10\x36\x46',
    '\x7e\x7e\x10\x38\x48','\x7e\x7e\x10\x3a\x4a','\x7e\x7e\x10\x3c\x4c','\x7e\x7e\x10\x3e\x4e',
    '\x7e\x7e\x10\x40\x50','\x7e\x7e\x10\x42\x52','\x7e\x7e\x10\x44\x54','\x7e\x7e\x10\x46\x56',
    '\x7e\x7e\x10\x48\x58','\x7e\x7e\x10\x4a\x5a','\x7e\x7e\x10\x4c\x5c','\x7e\x7e\x10\x4e\x5e'
]

'''
1. 连接设备，上电初始化。
2. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功。
3. 软件平台模拟电表，在收到被测STA 请求读表号后，向其下发电表地址信息。
4. 软件平台模拟CCO 向被测STA 启动集中器主动抄表业务 ，发送SOF 帧（抄表报文下行），
   用于点抄STA 所在设备的特定数据项（ DL/T645-2007 规约虚拟电表000000000001）当前时间。
5. 软件平台模拟电表向被测STA 返回抄读数据项，收到其返回的S0F 帧（抄表报文上行）。
6. 在虚拟电表的TTL 串口监控是否收STA 转发的数据报文，如在n 秒内未收到 ，则指示STA 抄表下行转发失败。
   如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
7. 软件平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指示STA 抄表上行转发失败，
   如收到数据与电表应答报文不同，则指示STA 抄表上行转发数据错误，否则指示STA 抄表上行转发数据成功，
   此测试流程结束，最终结论为此项测试通过。
check:
1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0001（集中器主动抄表）；
4. 测试STA 转发上行抄表数据时其报文控制字是否为0；
5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
6. 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
7. 测试STA 转发上行抄表数据时其应答状态是否为0（正常）；
8. 测试STA 转发上行抄表数据时其转发数据的规约类型是否为2（DL/T645-07））；
9. 测试STA 转发上行抄表数据时其报文序号是否与下行报文序号一致；
10. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
11. 测试STA 转发上行抄表数据时其数据（DATA）是否为DL/T645 规约报文；
12. 测试STA 上行转发数据是否与电能表应答报文相同。
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"


    S = serial.Serial('COM1')
    cmd_send = '\x7e\x7e\x10\x00\x10'
    #cmd_send = '\x7e\x7e\x10\x16\x26'
    S.write(cmd_send)

    band=0
    file_obj = open('hs_sensitivity_test_result.txt','w')

    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '00-00-00-00-00-01'
    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 1

    # 1. 连接设备，上电初始化。
    # 2. 软件平台模拟CCO 对入网请求的STA 进行处理，确定站点入网成功。
    # 3. 软件平台模拟电表，在收到被测STA 请求读表号后，向其下发电表地址信息。



    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    plc_tb_ctrl._debug("activate tb")
    tc_common.activate_tb(tb,work_band = 1)

    #wait for meter read request
    plc_tb_ctrl._debug("wait for meter read request")
    dlt645_frame = m.wait_for_dlt645_frame(code = 'ADDR_READ', dir = 'REQ_FRAME', timeout = 30)

    assert dlt645_frame.head.len == 0
    assert dlt645_frame.head.addr.upper() == 'AA-AA-AA-AA-AA-AA'

    #prepare reply frame for meter read request
    plc_tb_ctrl._debug("send reply to meter read request")
    tc_common.send_dlt645_addr_read_reply_frame(m, meter_addr)

    # 配置TB周期性发送中央信标
    plc_tb_ctrl._debug("configure TB to send central beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    cco_mac = beacon_dict['payload']['value']['cco_mac_addr']

    beacon_period_start_time = tb._configure_beacon(None, beacon_dict)

    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    # 等待STA1发送关联请求
    plc_tb_ctrl._debug("wait for assoc req")
    [fc, mac_head, nmm] = tb._wait_for_plc_nmm(mmtype=['MME_ASSOC_REQ'], timeout=50)
    assert fc.var_region_ver.dst_tei == 1
    assert mac_head.org_dst_tei == 1
    assert nmm.body.mac == meter_addr
    assert nmm.body.proxy_tei[0] == 1

    # 发送关联确认
    plc_tb_ctrl._debug("send assoc cnf to STA1")
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf.yaml')
    assert asso_cnf_dict is not None

    sta_tei = asso_cnf_dict['body']['tei_sta']

    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn
    asso_cnf_dict['body']['random_num'] = nmm.body.rand_num
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_NMM"

    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0, broadcast_flag=1, ack_needed=False)

    # 修改TB发送的中央信标, 添加发现信标
    plc_tb_ctrl._debug("re-config central beacon which allocates discovery beacon")
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 0xFFFF
    beacon_dict['payload']['value']['association_start'] = 1
    beacon_slot_alloc = plc_packet_helper.get_beacon_slot_alloc(beacon_dict['payload']['value'])
    beacon_slot_alloc['ncb_slot_num'] = 1
    beacon_slot_alloc['ncb_info'] = [dict(type=0, tei = 2)]
    # 增加了一个信标时隙，缩短CSMA时隙避免总时间超过信标周期
    beacon_slot_alloc['csma_slot_info'][1]['slot_len'] = 600
    beacon_slot_len = beacon_slot_alloc['beacon_slot_len']

    tb._configure_beacon(None, beacon_dict, True)

    # 4. 软件平台模拟CCO 向被测STA 启动集中器主动抄表业务 ，发送SOF 帧（抄表报文下行），
    #    用于点抄STA 所在设备的特定数据项（ DL/T645-2007 规约虚拟电表000000000001）当前时间。

    plc_tb_ctrl._debug("Step 4: simulate CCO to send cct meter read pkt...")

    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')

    for tmi_cnt in range(5,26):
        if tmi_cnt < 15 :
            test_tmi_b = tmi_cnt
            test_tmi_e = 0
        elif tmi_cnt < 21 :
            test_tmi_b = 15
            test_tmi_e = tmi_cnt - 14
        else :
            test_tmi_b = 15
            test_tmi_e = tmi_cnt - 11

        for test_pb_num in range(1,2):
            file_obj.write("'tmi_b': {},  'tmi_e': {}, 'pb_num': {}".format(test_tmi_b,test_tmi_e,test_pb_num))
            n = 0
            cmd_send = Fadding_table2[n]
            S.write(cmd_send)
            while n < len(Fadding_table2):
                error_cnt = 0
                for i in range(100):
                    plc_tb_ctrl._debug("send mr req")
                    apl_sn += 1
                    dl_meter_read_pkt['body']['sn'] = apl_sn
                    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))
                    #plc_tb_ctrl._debug(dl_meter_read_pkt)
                    dl_apl_645 = dl_meter_read_pkt['body']['data']
                    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)
                    m.clear_port_rx_buf()
                    tb.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
                    tb.mac_head.org_src_tei         = 1
                    tb.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
                    tb.mac_head.tx_type             = 'PLC_MAC_UNICAST'
                    tb.mac_head.mac_addr_flag       = 0
                    tb.mac_head.hop_limit           = 15
                    tb.mac_head.remaining_hop_count = 15
                    tb.mac_head.broadcast_dir       = 0 #downlink broadcast
                    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=sta_tei, tmi_b=test_tmi_b, tmi_e=test_tmi_e, pb_num=test_pb_num)
                    tc_common.wait_for_tx_complete_ind(tb)
                    # 5. 软件平台模拟电表向被测STA 返回抄读数据项，收到其返回的S0F 帧（抄表报文上行）。
                    # 6. 在虚拟电表的TTL 串口监控是否收STA 转发的数据报文，如在n 秒内未收到 ，则指示STA 抄表下行转发失败。
                    #    如在n 秒内收到，则指示STA 下行转发数据成功，虚拟电表针对数据报文进行解析并应答电表当前时间报文。
                    plc_tb_ctrl._debug("wait dlt645 frame")
                    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 5)
                    #plc_tb_ctrl._debug("645 pkt rx by meter: {}".format(dlt645_frame))
                    if dlt645_frame is not None:
                        #plc_tb_ctrl._debug(dlt645_frame)
                        assert dlt645_frame.head.len == 4,            "645 pkt head len err"
                        plc_tb_ctrl._debug("dlt645 received")
                        #time.sleep(10)
                    else:
                        plc_tb_ctrl._debug("DLT645 NOT RECEIVED")
                        error_cnt += 1
                    tb.tb_uart.clear_tb_port_rx_buf()
                    if error_cnt > 10 :
                        break
                #偏移值+16dB初始偏移值+40dB固定衰减
                threshold_snr = float(2*n+16+40-2)
                if(error_cnt > 10) :
                    plc_tb_ctrl._debug("current Fadding's threshold is {} dB".format(float(threshold_snr)))
                    file_obj.write("current Fadding's threshold is {} dB".format(float(threshold_snr)))
                    break
                else :
                    n += 1
                    cmd_send = Fadding_table2[n]
                    S.write(cmd_send)
                    plc_tb_ctrl._debug("current Fadding's threshold is {} dB".format(float(threshold_snr)))



'''
    # check 1. 测试STA 转发下行抄表数据时是否与CCO 下发的数据报文相同；
    dl_mtr_645_lst = []
    dl_mtr_645_str = meter.build_dlt645_07_frame(dict_content=dlt645_frame)
    tc_common.convert_str2lst(dl_mtr_645_str, dl_mtr_645_lst)

    if dl_mtr_645_lst != dl_apl_645:
        plc_tb_ctrl._debug(dl_apl_645)
        plc_tb_ctrl._debug(dl_mtr_645_lst)
        #assert 0,  "STA -> Meter - 645 packet err"



    # prepare reply frame for meter read request
    reply_data = [1,2,3,4]
    dis = [dlt645_frame.body.value.DI0,
           dlt645_frame.body.value.DI1,
           dlt645_frame.body.value.DI2,
           dlt645_frame.body.value.DI3]

    ul_mtr_645_lst = []
    ul_mtr_645_str = tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))

    tc_common.convert_str2lst(ul_mtr_645_str, ul_mtr_645_lst)
    plc_tb_ctrl._debug("645 pkt lst in upstream meter : {}".format(ul_mtr_645_lst))

    # 7. 软件平台监控是否能够在n 秒内收到STA 转发的电表当前时间报文，如未收到，则指示STA 抄表上行转发失败，
    #    如收到数据与电表应答报文不同，则指示STA 抄表上行转发数据错误，否则指示STA 抄表上行转发数据成功，
    #    此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 7: simulate CCO to receive the CCT METER READ reply from STA, with the meter data forwarded...")

#    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_ul('APL_CCT_METER_READ',10)

    pkt_id = 'APL_CCT_METER_READ'
    [timestamp, fc, mac_frame_head, apm] = tc_upg_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    plc_tb_ctrl._debug("rx apl cct meter read: {}".format(apm))

    ul_apl_645 = apm.body.data
    # check 2. 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port              == 0x11,                 "pkt header port id err"
    # check 3. 测试STA 转发上行抄表数据时其报文ID 是否为0x0001（集中器主动抄表）；
    assert apm.header.id                == pkt_id,               "pkt header packet id err"
    # check 4. 测试STA 转发上行抄表数据时其报文控制字是否为0；
    assert apm.header.ctrl_word         == 0,                    "pkt header ctrl word err"
    # check 5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
    assert apm.body.proto_ver           == 'PROTO_VER1',         "pkt body proto ver err"
    # check 6. 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
    assert apm.body.hdr_len              < 64,                   "pkt body hdr len err"
    # check 7. 测试STA 转发上行抄表数据时其应答状态是否为0（正常）；
    assert apm.body.rsp_status          == 'NORMAL_ACK',         "pkt body rsp status err"
    # check 8. 测试STA 转发上行抄表数据时其转发数据的规约类型是否为2（DL/T645-07））；
    assert apm.body.data_proto_type     == 'PROTO_DLT645_2007',  "pkt body data proto type err"
    # check 9. 测试STA 转发上行抄表数据时其报文序号是否与下行报文序号一致；
    assert apm.body.sn                  ==  apl_sn,              "pkt body sn err"
    # check 10. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
    assert apm.body.dir_bit             == 'UL',                 "pkt body directrion bit err"

    # check 11. 测试STA 转发上行抄表数据时其数据（DATA）是否为DL/T645 规约报文；
    # check 12. 测试STA 上行转发数据是否与电能表应答报文相同。
#    plc_tb_ctrl._debug("645 pkt in upstream apl : {}".format(ul_apl_645))
#    plc_tb_ctrl._debug("645 pkt in upstream meter : {}".format(ul_mtr_645_lst))

    assert cmp(ul_apl_645, ul_mtr_645_lst) == 0,                 "pkt body data - 645 pkt err"

    time.sleep(1)

    m.close_port()
'''


