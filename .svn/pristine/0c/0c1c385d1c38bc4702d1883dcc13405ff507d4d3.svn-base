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

    #send association request to DTU
    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = sub_nodes_addr[0]
    tb.mac_head.dst_mac_addr = '00-00-00-00-00-9C'
    tb._send_nmm('nml_assoc_req.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF','MME_ASSOC_GATHER_IND'], timeout = 15)

    if nmm.header.mmtype == 'MME_ASSOC_CNF':
        cnf = nmm.body
        assert cnf.mac_sta == sub_nodes_addr[0]
        assert cnf.result == 'NML_ASSOCIATION_OK' or cnf.result =='NML_ASSOCIATION_KO_RETRY_OK'
        assert cnf.tei_proxy == 1
    else:
        ind = nmm.body
        assert ind.result == 'NML_ASSOCIATION_OK' or cnf.result =='NML_ASSOCIATION_KO_RETRY_OK'
        assert ind.proxy_tei == 1
        assert ind.sta_num >= 1

        sta_list = filter(lambda x:x.addr == sub_nodes_addr[0],ind.sta_list)

        assert len(sta_list) > 0
#         flag = 0
#         for sta_info in ind.sta_list:
#             flag |= sta_info.addr == sub_nodes_addr[0]
#
#         #ensure sub node's address is in the list
#         assert flag == 1


    cct.close_port()






