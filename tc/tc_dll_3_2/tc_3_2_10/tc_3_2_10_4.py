# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time


def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    cct = concentrator.Concentrator()
    cct.open_port()

    tc_common.activate_tb(tb,work_band = 1)

    tc_common.set_cco_mac_addr(cct,'00-00-00-00-00-9C')


    #set sub node address
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,4))
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #sync the nid and sn between tb and DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

    req_dict = tb._load_data_file('nml_assoc_req_2.yaml')
    assert req_dict is not None
    plc_tb_ctrl._debug(sub_nodes_addr)

    #associate request from MAC 02
    req_dict['body']['mac'] = sub_nodes_addr[0]

    #send association request to DUT (mac address is not in the white list)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sub_nodes_addr[0]
    tb.mac_head.dst_mac_addr = '00-00-00-00-00-9C'

    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)
    assert nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK' or nmm.body.result == 'NML_ASSOCIATION_OK'

    plc_tb_ctrl._debug('sta tei allocated:' + str(nmm.body.tei_sta))
    time.sleep(15)


    #clear unrelated msg in the buffer
    tb.tb_uart.clear_tb_port_rx_buf()
    #relay MAC 03's  associate request
    req_dict['body']['mac'] = sub_nodes_addr[1]

    #send association request to DUT (mac address is not in the white list)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = nmm.body.tei_sta
    tb.mac_head.mac_addr_flag = 0
    req_dict['body']['proxy_tei'][0] = nmm.body.tei_sta
    msdu = plc_packet_helper.build_nmm(req_dict)
    tb._send_msdu(msdu, tb.mac_head, src_tei = nmm.body.tei_sta, dst_tei = 1)


    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 10)


    # plc_tb_ctrl._debug(nmm.body.result)
    # plc_tb_ctrl._debug(nmm.body.mac_sta)
    assert nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK' or nmm.body.result == 'NML_ASSOCIATION_OK'
    assert nmm.body.mac_sta == sub_nodes_addr[1]



    cct.close_port()






