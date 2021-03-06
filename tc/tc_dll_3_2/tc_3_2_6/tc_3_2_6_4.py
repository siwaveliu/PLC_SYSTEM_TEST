# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter

'''
1. 连接设备，上电初始化；
2. 软件平台模拟电表，在收到待测 STA 的读表号请求后，下发表地址；
3. 软件平台模拟 CCO 向待测设备发送“中央信标”；
4. 软件平台模拟 CCO 在收到待测 STA 发送的“关联请求报文” 后，向待测 STA 发送“关
联确认报文”；
5. 软件平台模拟 CCO 在收到待测 STA 发送的“选择确认报文”之后，发送 SOF1 帧（全网
广播抄表报文），并设定 10s 的等待定时器；
6. 软件平台在收到待测 STA 转发的 SOF3 帧之后，模拟 STA 转发出全网广播 SOF2 帧（对
SOF1 帧的转发），并设定 10s 的定时器。
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
    asso_cnf_dict = tb._load_data_file('nml_assoc_cnf.yaml')
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




    # 软件模拟集中器+CCO, 发送集中器主动抄表下行报文，全网广播。
    #tb._send_plc_apm('apl_cct_meter_read_ul.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)
    dl_meter_read_pkt = tb._load_data_file(data_file='apl_cct_meter_read_dl.yaml')
    #ul_meter_read_pkt['body']['sn'] = apm.body.sn

    dl_meter_read_pkt['body']['data'][-2] = meter.calc_dlt645_cs8(map(chr,dl_meter_read_pkt['body']['data']))

    plc_tb_ctrl._debug(dl_meter_read_pkt)

    msdu = plc_packet_helper.build_apm(dict_content=dl_meter_read_pkt, is_dl=True)

    tb.mac_head.org_dst_tei = 3  #DUT tei is 2, here, we need DUT to relay the packet
    tb.mac_head.org_src_tei = 1
    tb.mac_head.msdu_type = "PLC_MSDU_TYPE_APP"
    tb.mac_head.tx_type = 'PLC_MAC_ENTIRE_NW_BROADCAST'
    tb.mac_head.mac_addr_flag = 0
    tb.mac_head.hop_limit = 15
    tb.mac_head.remaining_hop_count = 15
    tb.mac_head.broadcast_dir= 1 #downlink broadcast



#     msdu_structure = plc_packet_helper.parse_apm(msdu, True)
#     #
#
#     msdu_structure.body.data[-2] = meter.calc_dlt645_cs8(msdu_structure.body.data)
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=0xFFF,broadcast_flag = 1,auto_retrans=False)


    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ',10)

    assert mac_frame_head.remaining_hop_count == tb.mac_head.remaining_hop_count - 1


    time.sleep(1)

    #simulate another msdu, it is relay of previous msdu, it should be filtered by DUT
    tb.mac_head.remaining_hop_count = 14
    tb.mac_head.reset_times += 1
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=1, dst_tei=0xFFF,broadcast_flag = 1,sn = tb.mac_head.msdu_sn,auto_retrans=False)

    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl('APL_CCT_METER_READ',10, lambda:{None})

    assert apm is not None


    m.close_port()


