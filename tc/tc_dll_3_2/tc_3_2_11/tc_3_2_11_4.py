# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 选择链路层网络维护测试用例，被测 sta 上电
2. 测试用例通过载波透明接入单元发送中央信标帧，路由周期为 20s。
3. 被测 sta 收到中央信标帧后，发起关联请求报文，申请入网。
4. 载波信道侦听单元收到被测试 sta 的关联请求报文后，上传给测试台体，再送给一致
性评价模块。
5. 一致性评价模块判断被测 sta 的关联请求报文正确后，通知测试用例。
6. 测试用例通过载波透明接入单元发送关联确认报文。
7. 被测 sta 收到关联确认报文后。
8. 测试用例通过载波透明接入单元发送中央信标报文，中央信标中安排被测 sta 发现信
标时隙，路由周期为 20s，发现站点发现列表周期为 2s。
9. 被测 sta 收到中央信标帧后，根据发现列表周期发送发现列表报文。
10. 载波信道侦听单元收到被测 sta 的发现列表报文后，上传给测试台体，再送给一致性
评价模块，在一个路由周期内（20s）应接收到多个被测 sta 发现列表报文。
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    m = meter.Meter()
    m.open_port()

    tc_common.activate_tb(tb,work_band = 1)

    cco_mac = '00-00-C0-A8-01-01'
    meter_addr = '12-34-56-78-90-12'
    tc_common.sta_init(m, meter_addr)

    #send beacon periodically
    beacon_dict = tb._load_data_file('tb_beacon_data.yaml')
    beacon_dict['num'] = 65535
    beacon_dict['payload']['value']['association_start'] = 1

    tb._configure_beacon(None, beacon_dict)

    #config nid and nw_sn for sending of mpdu
    tb._configure_nw_static_para(beacon_dict['fc']['nid'], beacon_dict['payload']['value']['nw_sn'])

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_REQ'],15)


    #send associate confirm to STA
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf_4.yaml')
    asso_cnf_dict['body']['mac_sta'] = meter_addr
    asso_cnf_dict['body']['mac_cco'] = cco_mac
    asso_cnf_dict['body']['p2p_sn'] = nmm.body.p2p_sn

    #config the mac header
    tb.mac_head.org_dst_tei = 0
    tb.mac_head.org_src_tei = 1
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = cco_mac
    tb.mac_head.dst_mac_addr = meter_addr
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    msdu = plc_packet_helper.build_nmm(asso_cnf_dict)

    #tb._configure_nw_static_para(nid, nw_org_sn)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 1, dst_tei = 0,broadcast_flag = 1)


    #in this central beacon, discovering beacon slot is reserved for tei2

    beacon_dict = tb._load_data_file('tb_beacon_data_4.yaml')
    tb._configure_beacon(None, beacon_dict,True)

    #get sta discover packet sending period
    for beacon_item in beacon_dict['payload']['value']['beacon_info']['beacon_item_list']:
        if beacon_item['head'] == 'ROUTE_PARAM':
            sta_discovery_period = beacon_item['beacon_item']['sta_discovery_period']



    beacon_num = 0
    discover_packet_num = 0

    plc_tb_ctrl._debug('begin to do discover packet statistics')

#     [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_DISCOVER_NODE_LIST'],15)
#     [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    cur_time = time.time()
    while(time.time() < cur_time + tc_common.calc_timeout(sta_discovery_period*10)):
        ret = tb._wait_for_fc_pl_data(_check_plc_beacon_or_nmm,1,(lambda:None),['MME_DISCOVER_NODE_LIST'])
        if ret is not None:
            [msg_str, ts_or_fc, fc_or_mac_head, payload_or_nmm] = ret
            if msg_str == 'beacon':
                beacon_num += 1
                plc_tb_ctrl._debug('time:{0} beacon num:{1}'.format(time.time(),beacon_num))
                beacon_payload = payload_or_nmm
            else:
                discover_packet_num += 1
                plc_tb_ctrl._debug('time:{0} disc num:{1}'.format(time.time(),discover_packet_num))
                nmm = payload_or_nmm

#     for ii in range(0,10):
#         while ret is not None:
#             [msg_str, ts_or_fc, fc_or_mac_head, payload_or_nmm] = ret
#             if msg_str == 'beacon':
#                 beacon_num += 1
#                 beacon_payload = payload_or_nmm
#             else:
#                 discover_packet_num += 1
#                 plc_tb_ctrl._debug('time:{0} disc num:{1}'.format(time.time(),discover_packet_num))
#                 nmm = payload_or_nmm
#             ret = \
#             tb._wait_for_fc_pl_data(_check_plc_beacon_or_nmm,0,(lambda:None),['MME_DISCOVER_NODE_LIST'])
#
#         time.sleep(sta_discovery_period)


    assert beacon_num > 1
    assert discover_packet_num > 1
#         #wait for discovering beacon comming from DUT
#     [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(15)[1:]

    #check parameters inside the discover beacon
    assert beacon_payload.beacon_type == 'DISCOVERY_BEACON'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.level == 0 + 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.proxy_tei == 1
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.mac == meter_addr
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.role == 'STA_ROLE_STATION'
    assert beacon_payload.beacon_info.beacon_item_list[0].beacon_item.sta_tei == 2

    #check the parameters in discover packet body
    assert nmm.body.tei == 2
    assert nmm.body.sta_mac_addr == meter_addr


    m.close_port()


def _check_plc_beacon_or_nmm(fc_pl_data_payload, mmtype = None):
        '''
        Args:
            fc_pl_data_payload: plc_test_frame.fc_pl_data

        Return:
            [fc, beacon_payload]
        '''
        pb_size = fc_pl_data_payload.pb_size
        pb_num = fc_pl_data_payload.pb_num
        fc_pl_data = fc_pl_data_payload.payload.data
        beacon_payload = None
        mac_frame = None
        fc = fc_pl_data[0:16]
        fc = plc_packet_helper.parse_mpdu_fc(fc)

        if (fc is not None):
            if ("PLC_MPDU_BEACON" == fc.mpdu_type):
                pb_size = fc_pl_data_payload.pb_size
                beacon_payload = plc_packet_helper.get_beacon_payload(fc_pl_data_payload.pb_num, pb_size, fc_pl_data[16:(16+pb_size)])
            elif ("PLC_MPDU_SOF" == fc.mpdu_type):
                mac_frame = plc_packet_helper.reassemble_mac_frame(pb_num, pb_size, fc_pl_data[16:(16+pb_size*pb_num)])

        if (beacon_payload is None) and (mac_frame is None):
            return None

        if beacon_payload is not None:
            return ['beacon',fc_pl_data_payload.timestamp, fc, beacon_payload]

        elif mac_frame is not None:
            valid = plc_packet_helper.check_mac_frame_crc(mac_frame)
            if not valid:
                plc_tb_ctrl._debug('Invalid mac frame crc')
                return None

            if mac_frame.head.msdu_type != "PLC_MSDU_TYPE_NMM":
                plc_tb_ctrl._debug('Unexpected msdu type')
                return None

            nmm = mac_frame.msdu.value
            #if (mmtype is not None) and (mmtype != nmm.header.mmtype):
            if (mmtype is not None) and not (nmm.header.mmtype in mmtype):
                plc_tb_ctrl._debug('Unexpected nmm type:{}'.format(nmm.header.mmtype))
                return None

            return ['nmm',fc, mac_frame.head, nmm]

