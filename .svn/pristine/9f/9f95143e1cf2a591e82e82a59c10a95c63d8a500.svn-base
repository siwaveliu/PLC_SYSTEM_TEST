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
    sub_nodes_addr = map(lambda x: '00-00-00-00-00-' + str(x).zfill(2), range(2,11))

    tc_common.add_sub_node_addr(cct,sub_nodes_addr)


    #wait for beacon from DUT
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

#     tb._configure_proxy('tb_time_config_req.yaml')
#     tb._configure_nw_static_para(beacon_fc.nid, beacon_payload.nw_sn)

    req_dict = tb._load_data_file('nml_assoc_req_2.yaml')

    assert req_dict is not None

    plc_tb_ctrl._debug(sub_nodes_addr)
    
    sub_nodes_addr_copy = sub_nodes_addr[:]

    #send 02-10 associate request
    for addr in sub_nodes_addr:
        req_dict['body']['mac'] = addr

        #send association request to DUT (mac address is not in the white list)
        tb.mac_head.org_dst_tei = 1
        tb.mac_head.org_src_tei = 0
        tb.mac_head.mac_addr_flag = 1
        tb.mac_head.src_mac_addr = addr
        tb.mac_head.dst_mac_addr = '00-00-00-00-00-9C'

        msdu = plc_packet_helper.build_nmm(req_dict)
        tb._send_msdu(msdu, tb.mac_head, src_tei = 0, dst_tei = 1)
        #time.sleep(0.5)

    #while(len(sub_nodes_addr) > 0):
        while True:
            ret = tb._wait_for_plc_nmm(['MME_ASSOC_CNF','MME_ASSOC_GATHER_IND'], 2,lambda:None)
            
            if ret is None:
                break
             
            [fc, mac_frame_head, nmm] = ret
    
            if nmm.header.mmtype == 'MME_ASSOC_CNF':
                if nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK' or nmm.body.result == 'NML_ASSOCIATION_OK':
                    plc_tb_ctrl._debug(nmm.body.mac_sta)
                    #assert nmm.body.mac_sta == addr
                    if nmm.body.mac_sta in sub_nodes_addr_copy:
                        sub_nodes_addr_copy.remove(nmm.body.mac_sta)
                        plc_tb_ctrl._debug(sub_nodes_addr_copy)
                        break
            else:
                if nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK' or nmm.body.result == 'NML_ASSOCIATION_OK':
                    plc_tb_ctrl._debug(nmm.body.sta_list)
                    #assert addr in nmm.body.sta_list
                    for x in nmm.body.sta_list:
                        if x.addr in sub_nodes_addr_copy:
                            sub_nodes_addr_copy.remove(x.addr)
                            plc_tb_ctrl._debug(sub_nodes_addr_copy)
                            break


    assert len(sub_nodes_addr_copy) == 0
    
    cct.close_port()






