# -- coding: utf-8 --
# CCO 收到STA 事件主动上报的应答禁止事件主动上报测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time

'''
1. 待测CCO 与透明物理转发设备处于隔变环境。
2. 软件平台（集中器）模拟集中器向待测CCO 下发主节点地址（Q／GDW 1376.2 协议格式报文），
   并添加从节点地址（Q／GDW 1376.2 协议格式报文），
3. 软件平台（STA）模拟STA（）向待测CCO 发送入网请求，CCO 批准入网，分配TEI=2，并确保组网完成。
4. 软件平台（集中器）模拟集中器向待测CCO 下发禁止从节点上报帧（Q／GDW 1376.2 协议格式报文），待测CCO 应答确认。
5. 事件报文上行帧，其中状态事件标识位设置为电表失压，报文序号设置为1，透明物理设备转发该帧至待测CCO。
6. 待测CCO 收到事件报文上行帧，判断事件状态为禁止上报的类型，产生并发送事件报文下行帧（禁止上报）。
7. 透明物理设备收到该报文后，将其转发给软件平台（STA），软件平台（STA）判断事件报文下行帧（禁止上报）是否满足帧格式要求
check:
1. 事件报文下行帧（禁止上报）中的“方向位”是否为0
2. 事件报文下行帧（禁止上报）中的“启动位”是否为0
3. 事件报文下行帧（禁止上报）中的“功能码”是否为3
4. 事件报文下行帧（禁止上报）中的“协议版本号”是否为1
5. 软件平台（集中器）是否收到待测CCO 上报的从节点事件帧（收到则不通过，未收到则通过）

'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    gdw1376p2_sn = 1
    cco_mac      = '00-00-00-00-00-9C'
    sta_mac      = '00-00-00-00-00-01'
    apl_sn       = 1
    meter_mac    = '00-00-00-00-AA-01'
    cct          = concentrator.Concentrator()
    cct.open_port()

    # 1. 待测CCO与透明物理转发设备处于隔变环境。
    # 2. 软件平台（集中器）模拟集中器向待测CCO下发主节点地址（Q／GDW 1376.2协议格式报文），
    #    并添加从节点地址（Q／GDW 1376.2协议格式报文），其中待测CCO的节点地址为，从节点地址为。
    # 3. 软件平台（STA）模拟STA（）向待测CCO发送入网请求，CCO批准入网，分配TEI，并确保组网完成。
    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 4.软件平台（集中器）模拟集中器向待测CCO 下发
    #   禁止从节点上报帧（Q／GDW 1376.2 协议格式报文），待测CCO 应答确认。
    plc_tb_ctrl._debug("Step 4.1: simulate CCT to send CCO 1376.2 pkt (AFN=05, F=2) - disable node event report...")

    dl_afn05f2_pkt = tb._load_data_file(data_file='afn05f2_dl.yaml')
    dl_afn05f2_pkt['cf']['prm']                      = 'MASTER'
    dl_afn05f2_pkt['user_data']['value']['r']['sn']  = gdw1376p2_sn
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn05f2_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    plc_tb_ctrl._debug("Step 4.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=1)...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0, timeout=3)
    assert frame1376p2 is not None,           "AFN00H F1 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir                == 'UL',          "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm                == 'SLAVE',       "cf prm err"
    assert frame1376p2.user_data.value.r.sn  == gdw1376p2_sn,  "sn err"
    gdw1376p2_sn += 1

    time.sleep(1)
    tb.tb_uart.clear_tb_port_rx_buf()

    # 5.事件报文上行帧，其中状态事件标识位设置为电表失压，报文序号设置为1，
    #   透明物理设备转发该帧至待测CCO。
    plc_tb_ctrl._debug("Step 5: simulate STA to send APL EVENT REPORT upstream pkt...")

    plc_tb_ctrl._debug("apl_sn = {}, meter_mac = {}".format(apl_sn, meter_mac))

    ul_event_report_pkt                 = tb._load_data_file(data_file='apl_event_report_ul.yaml')
    ul_event_report_pkt['body']['sn']   = apl_sn
    ul_event_report_pkt['body']['addr'] = meter_mac
    apl_645 = ul_event_report_pkt['body']['data']
    msdu    = plc_packet_helper.build_apm(dict_content=ul_event_report_pkt, is_dl=False)
#    plc_tb_ctrl._debug("msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=0, dst_tei=1,auto_retrans=False)

    tc_common.wait_for_tx_complete_ind(tb)

    # 6.待测CCO 收到事件报文上行帧，判断事件状态为禁止上报的类型，
    #   产生并发送事件报文下行帧（禁止上报）。

    # 7.透明物理设备收到该报文后，将其转发给软件平台（STA），
    #   软件平台（STA）判断事件报文下行帧（禁止上报）是否满足帧格式要求
    plc_tb_ctrl._debug("Step 6,7: simulate STA to receive APL EVENT REPORT downstream pkt (disable event report)...")

    pkt_id = 'APL_EVENT_REPORT'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 3)
    # 监控透明设备是否能收到待测CCO下行帧。
    assert apm is not None,                                        "APL_EVENT_REPORT downstream not received"
    # 报文端口号是否为0x11
    assert apm.header.port        == 0x11,                         "pkt header port id err"
    # 报文ID 是否为0x0008（事件上报）
    assert apm.header.id          == pkt_id,                       "pkt header packet id err"
    # check 1. 事件报文下行帧（禁止上报）中的“方向位”是否为0 (下行)
    assert apm.body.dl.direction  == 'DL',                         "pkt body directrion bit err"
    # check 2. 事件报文下行帧（禁止上报）中的“启动位”是否为0 (从动站)
    assert apm.body.dl.prm        == 'SLAVE',                      "pkt body prm bit err"
    # check 3. 事件报文下行帧（禁止上报）中的“功能码”是否为3 （CCO应答确认给STA）
    assert apm.body.dl.op_code    == 'EVENT_CODE_DISABLE_REPORT',  "pkt body op_code err"
    # check 4. 事件报文下行帧（禁止上报）中的“协议版本号”是否为1
    assert apm.body.dl.proto_ver  == 'PROTO_VER1',                 "pkt body proto_ver err"
    # 电表地址
    assert apm.body.dl.sn         ==  apl_sn,                      "pkt body sn err"
    # 电表地址
    assert apm.body.dl.addr       ==  meter_mac,                   "pkt body meter_mac err"

    # 软件平台（集中器）是否收到待测CCO 上报的从节点事件帧（收到则不通过，未收到则通过）
    plc_tb_ctrl._debug("Step 8: simulate CCT to receive CCO 1376p2 (AFN=06H F=5), the expected result = not received...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=16, dt2=0, timeout=3, tm_assert=False)

    # check 5. 软件平台（集中器）是否收到待测CCO 上报的从节点事件帧（收到则不通过，未收到则通过）
    assert frame1376p2 is None,        "AFN06H F5 upstream ACK should not be received"
    plc_tb_ctrl._debug("Test Is Passed - AFN06HF5 is not received as expected")


    cct.close_port()






