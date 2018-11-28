# -- coding: utf-8 --
# CCO 发送通信测试帧测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import time


'''
1. 连接设备，上电初始化；
2. 软件平台模拟集中器，通过串口向待测CCO下发“设置主节点地址”命令，在收到“确认”后，再通过串口向待测CCO下发“添加从节点”命令，
   将目标网络站点的MAC地址下发到CCO中，等待“确认”；
3. 软件平台收到待测CCO发送的“中央信标”后，模拟未入网STA向待测CCO发送“关联请求”，在收到待测CCO发送的“关联确认”后，
   确定模拟STA入网成功；
4. 软件平台模拟集中器，通过串口向待测CCO下发“本地通信模块报文通信测试”命令（目标地址不在白名单中），同时开启定时器（2s），
   定时器溢出前，查看是否收到待测CCO从串口发来的“否认”报文（表号不存在）；
5. 软件平台模拟集中器，通过串口向待测CCO下发正确的“本地通信模块报文通信测试”命令，同时开启定时器（2s），
   定时器溢出前，查看是否收到待测CCO从透明设备发来的“通信测试命令”报文和从串口发来的“确认”报文；
注：所有需要“选择确认帧”确认的，当没有收到“选择确认帧”，则fail。所有的本测试例不关心的报文被收到后，直接丢弃，不做判断。
check:
1. CCO在收到正常的“本地通信模块报文通信测试”376.2报文后，
   是否能够发出正确的“通信测试命令”宽带PLC应用层报文并通过串口发送“确认”376.2报文；
2. CCO在收到异常的“本地通信模块报文通信测试”376.2报文后，
   是否不会发出“通信测试命令”宽带PLC应用层报文并通过串口发送“否认”376.2报文；
'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    cct = concentrator.Concentrator()
    cct.open_port()
    cco_addr = '00-00-00-00-00-9C'
    sta_addr = '00-00-00-00-00-01'

    # 1. 连接设备，上电初始化；
    plc_tb_ctrl._debug("Step 1: connect devices, power up init...")

    tc_common.activate_tb(tb,work_band = 1)
    cct.clear_port_rx_buf()

    # 2. 软件平台模拟集中器，通过串口向待测CCO下发“设置主节点地址”命令，
    #    在收到“确认”后，再通过串口向待测CCO下发“添加从节点”命令，将目标网络站点的MAC地址下发到CCO中，等待“确认”；
    plc_tb_ctrl._debug("Step 2.1: simulate CCT to send CCO Set CCO ADDR command ...")

    tc_common.set_cco_mac_addr(cct,cco_addr)

    #set sub node address
    plc_tb_ctrl._debug("Step 2.2: simulate CCT to send CCO Set sub node ADDR list command ...")
    sub_nodes_addr = [sta_addr]
    tc_common.add_sub_node_addr(cct,sub_nodes_addr)

    # 3. 软件平台收到待测CCO发送的“中央信标”后，
    #    模拟未入网STA向待测CCO发送“关联请求”，在收到待测CCO发送的“关联确认”后，确定模拟STA入网成功；
    #wait for beacon from DUT
    plc_tb_ctrl._debug("Step 3.1: simulate STA to wait for CCO beacon ...")
    [beacon_fc, beacon_payload] = tb._wait_for_plc_beacon(30)[1:]

    #sync the nid and sn between tb and DTU
    plc_tb_ctrl._debug("Step 3.2: sync the nid and sn between tb and DTU ...")

    tc_common.sync_tb_configurations(tb,beacon_fc.nid, beacon_payload.nw_sn)

    #send association request to DUT
    #  3.1 MAC地址不在白名单中
    plc_tb_ctrl._debug("Step 3.3: simulate STA to send association request to DUT, with invalid MAC (not in white list)...")

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb._send_nmm('nml_assoc_req_invalid.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    tc_common.wait_for_tx_complete_ind(tb)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF','MME_ASSOC_GATHER_IND'], timeout = 15)
    assert (nmm.body.result == 'NML_ASSOCIATION_KO_NOT_IN_WL'), "assoc not in whitelist fail"

    time.sleep(1)
    tb.tb_uart.clear_tb_port_rx_buf()
    #  3.2 MAC地址在白名单中
    plc_tb_ctrl._debug("Step 3.5: simulate STA to send association request to DUT, with valid MAC (in white list) ...")

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = 0
    tb._send_nmm('nml_assoc_req_valid.yaml', tb.mac_head, src_tei = 0,dst_tei = 1)

    tc_common.wait_for_tx_complete_ind(tb)

    [fc, mac_frame_head, nmm] = tb._wait_for_plc_nmm(['MME_ASSOC_CNF','MME_ASSOC_GATHER_IND'], timeout = 15)
    assert (nmm.body.result == 'NML_ASSOCIATION_OK') or (nmm.body.result == 'NML_ASSOCIATION_KO_RETRY_OK'), "assoc in whitelist fail"
    sta_tei = nmm.body.tei_sta

    # 4. 软件平台模拟集中器，通过串口向待测CCO下发“本地通信模块报文通信测试”命令（AFN04F3,目标地址不在白名单中），
    #    同时开启定时器（2s），定时器溢出前，查看是否收到待测CCO从串口发来的“否认”报文（表号不存在）；
    plc_tb_ctrl._debug("Step 4.1: simulate CCT to send CCO 1376.2 pkt (AFN=04, F=3) - comm test cmd, with invalid dst addr...")
    frame = concentrator.build_gdw1376p2_frame(data_file='afn04f3_dl_invalid.yaml')
    assert frame is not None
    cct.send_frame(frame)

    plc_tb_ctrl._debug("Step 4.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=2) - deny...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x02, dt2=0, timeout=2)
    # 2. CCO在收到异常的“本地通信模块报文通信测试”376.2报文后，
    #    是否不会发出“通信测试命令”宽带PLC应用层报文并通过串口发送“否认”376.2报文；
    assert frame1376p2 is not None, "AFN00H F2 upstream deny not received"  #监控集中器是否能收到待测CCO 发送的否认上行报文。

    # 5. 软件平台模拟集中器，通过串口向待测CCO下发正确的“本地通信模块报文通信测试”命令（AFN04F3,目标在白名单中），
    #     同时开启定时器（2s），定时器溢出前，查看是否收到待测CCO从透明设备发来的“通信测试命令”报文和从串口发来的“确认”报文；
    plc_tb_ctrl._debug("Step 5.1: simulate CCT to send CCO 1376.2 pkt (AFN=04, F=3) - comm test cmd, with valid dst addr...")
    frame = concentrator.build_gdw1376p2_frame(data_file='afn04f3_dl_valid.yaml')
    assert frame is not None
    cct.send_frame(frame)

    plc_tb_ctrl._debug("Step 5.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=1) - confirm...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0, timeout=2)
    # check 1. CCO在收到正常的“本地通信模块报文通信测试”376.2报文后，
    #    是否能够发出正确的“通信测试命令”宽带PLC应用层报文并通过串口发送“确认”376.2报文；
    assert frame1376p2 is not None, "AFN00H F1 upstream confirm not received"  #监控集中器是否能收到待测CCO 发送的确认上行报文。

    # 等待CCO发送通信测试命令（ID=0006）给STA
    plc_tb_ctrl._debug("Step 5.3: simulate STA to receive CCO APL COMM TEST cmd...")
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm('APL_COMM_TEST', timeout = 3)
    assert apm is not None,                                  "APL_COMM_TEST not received"
    # 报文端口号是否为0x11
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # 报文ID 是否为0x0006（通信测试）
    assert apm.header.id            == 'APL_COMM_TEST',      "pkt header packet id err"
    # 报文控制字是否为0
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # 协议版本号是否为1
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
    # 转发数据的规约类型是否为2（DL/T645-07）
    assert apm.body.dl.prot_type    == 'PROTO_DLT645_2007',  "pkt body data proto type err"

    cct.close_port()






