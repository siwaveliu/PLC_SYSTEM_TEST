# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common


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
    sub_nodes_addr = ['00-00-00-00-00-01']
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DTU
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

#     tb._configure_proxy('tb_time_config_req.yaml')
#     tb._configure_nw_static_para(beacon_fc.nid, beacon_payload.nw_sn)

    #send association request to DUT (mac address is not in the white list)
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sub_nodes_addr[0]
    tb.mac_head.dst_mac_addr = '00-00-00-00-00-9C'
    tb._send_nmm('nml_assoc_req_2.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF'], timeout = 15)

    assert nmm.header.mmtype == 'MME_ASSOC_CNF'
    assert nmm.body.result == 'NML_ASSOCIATION_KO_NOT_IN_WL'

    cct.close_port()






