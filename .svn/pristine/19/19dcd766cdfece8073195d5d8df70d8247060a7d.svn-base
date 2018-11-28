# -- coding: utf-8 --
# STA 事件主动上报测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import time
import meter



'''
1. 待测STA 与透明物理转发设备处于隔变环境。
2. 软件平台(电能表)模拟电表，在收到待测STA 请求读表号后，向其下发电表地址信息()。
3. 软件平台(CCO)模拟CCO 功能，通过透明物理转发设备，处理待测STA 的入网请求，分配TEI=2 给待测STA，确保被测STA 成功入网。
4. 软件平台（电能表）将待测STA 的EventOut 管脚输出高阻态，在收到待测STA 发来的读数据主站请求帧(645 协议)后，
   模拟失压事件，应答状态事件数据(645 协议)
5. 待测STA 将状态事件按应用层事件报文封装并发送，透明物理转发设备将接收到的应用层事件报文转发至软件平台(CCO)。
6. 软件平台(CCO)判定应用层事件报文是否符合规定的帧格式。
check:
1. 事件报文上行帧中的“方向位”是否为1
2. 事件报文上行帧中的“启动位”是否为1
3. 事件报文上行帧中的“功能码”是否为1
4. 事件报文上行帧中的“电能表地址”是否与分配的表地址一致
5. 事件报文上行帧中的“协议版本号”是否为1
'''
def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    global timeout_flag

    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    m = meter.Meter()
    m.open_port()

    cco_mac            = '00-00-C0-A8-01-01'
    meter_addr         = '01-00-00-00-00-00'
    invalid_addr       = '00-00-00-11-22-33'

    beacon_loss        = 0
    beacon_proxy_flag  = 0

    sta_tei            = 2
    apl_sn             = 0x1000


    # 1. 待测STA 与透明物理转发设备处于隔变环境。
    # 2. 软件平台(电能表)模拟电表，在收到待测STA 请求读表号后，向其下发电表地址信息()。
    # 3. 软件平台(CCO)模拟CCO 功能，通过透明物理转发设备，处理待测STA 的入网请求，
    #    分配TEI=2 给待测STA，确保被测STA 成功入网。

    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    tc_common.apl_sta_network_connect(tb, m, cco_mac, meter_addr, sta_tei, beacon_loss, beacon_proxy_flag)

    # 4. 软件平台（电能表）将待测STA 的EventOut 管脚输出高阻态，在收到待测STA 发来的读数据主站请求帧(645 协议)后，
    #    模拟失压事件，应答状态事件数据(645 协议)
    plc_tb_ctrl._debug("Step 4: simulate meter to trigger STA event by pin, and to receive/ack 645 pkt from/to STA...")
    tc_common.trig_event_report(tb)

    plc_tb_ctrl._debug("Step 4.1: simulate meter to receive 645 pkt from STA...")

    # 期望的下行645报文是[04,00,15,01]
    expected_di = [(0x33 + 0x01), (0x33 + 0x15), (0x33 + 0x00), (0x33 + 0x04)]

    dlt645_frame = m.wait_for_dlt645_frame(code = 'DATA_READ', dir = 'REQ_FRAME', timeout = 20)
    plc_tb_ctrl._debug(dlt645_frame)
    assert dlt645_frame.head.len == 4,            "645 pkt head len err"

    dis = [dlt645_frame.body.value.DI0,
           dlt645_frame.body.value.DI1,
           dlt645_frame.body.value.DI2,
           dlt645_frame.body.value.DI3]
    assert cmp(dis, expected_di) == 0,            "645 pkt DI is not the expected err"

    plc_tb_ctrl._debug("Step 4.2: simulate meter to ack 645 pkt to STA...")
    # 模拟电表应答 - 全失压
    reply_data     = [0x33 for i in range(10)]  # 10 字节
    reply_data[9] += 4                          # bit[74] - 全失压

    ul_mtr_645_str = tc_common.send_dlt645_reply_frame(m,meter_addr,dis,reply_data,len(reply_data))
    tc_common.untrig_event_report(tb)

    ul_mtr_645_lst = []
    tc_common.convert_str2lst(ul_mtr_645_str, ul_mtr_645_lst)

    # 5. 待测STA 将状态事件按应用层事件报文封装并发送，透明物理转发设备将接收到的应用层事件报文转发至软件平台(CCO)。
    plc_tb_ctrl._debug("Step 5: simulate CCO to receive the APL event pkt from STA...")

    pkt_id = 'APL_EVENT_REPORT'
    [timestamp, fc, mac_frame_head, apm] = tc_common.apl_sta_rx_one_apm_ul(tb, pkt_id, 10)

    # 6. 软件平台(CCO)判定应用层事件报文是否符合规定的帧格式。
    plc_tb_ctrl._debug("Step 6: simulate CCO to check the valid of the APL event pkt from STA...")

    assert apm is not None,                                      "APL EVENT REPORT is not received err"
    ul_apl_645 = apm.body.data
#    plc_tb_ctrl._debug("rx apm = {}".format(apm))

    # check . 测试STA 转发上行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port              == 0x11,                 "pkt header port id err"
    # check . 测试STA 转发上行抄表数据时其报文ID 是否为0x0008（事件上报）；
    assert apm.header.id                == pkt_id,               "pkt header packet id err"
    # check . 测试STA 转发上行抄表数据时其报文控制字是否为0；
    assert apm.header.ctrl_word         == 0,                    "pkt header ctrl word err"
    # check . 测试STA 转发上行抄表数据时其报文头长度是否符合在0-64 范围内；
    assert apm.body.hdr_len              < 64,                   "pkt body hdr len err"
    # check 1. 测试STA 转发上行抄表数据时其选项字是否为1（方向位：上行）；
    assert apm.body.direction           == 'UL',                 "pkt body directrion bit err"
    # check 2. 事件报文上行帧中的“启动位”是否为1 (MASTER)
    assert apm.body.prm                 == 'MASTER',             "pkt body prm bit err"
    # check 3. 事件报文上行帧中的“功能码”是否为1, (STA主动上报事件给CCO)
    assert (apm.body.op_code == 'EVENT_CODE_REPORT') or (apm.body.op_code == 'EVENT_CODE_ACK'),  "pkt body op code err"
    # check 4. 事件报文上行帧中的“电能表地址”是否与分配的表地址一致
    assert apm.body.addr                == meter_addr,           "pkt body addr err"
    # check 5. 测试STA 转发上行抄表数据时其协议版本号是否为1；
    assert apm.body.proto_ver           == 'PROTO_VER1',         "pkt body proto ver err"

    # check . 测试STA 上行转发数据是否与电能表应答报文相同。
    assert cmp(ul_apl_645, ul_mtr_645_lst) == 0,                 "pkt body data - 645 pkt err"


    time.sleep(1)

    m.close_port()



