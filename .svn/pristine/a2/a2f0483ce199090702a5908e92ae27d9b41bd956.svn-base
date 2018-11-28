# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper


'''
1. 连接设备，上电初始化。
2. 软件平台模拟集中器向待测CCO 下发“设置主节点地址”命令，在收到“确认”后，向待测CCO 下发“添加从节点”命令，
   将目标网络站点的MAC 地址下发到CCO 中，等待“确认”。
3. 软件平台模拟集中器向待测CCO 发送目标站点为STA 的Q／GDW 1376.2 协议AFN13HF1（“监控从节点”命令） 启动集中器主动抄表业务，
   用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
4. 软件模拟STA+电表，待测CCO 向其下发抄表下行报文，抄读当前的时间数据项，测试平台回复抄表上行报文。
5. 测试平台监控是否能够在n(n=模拟集中器对被测CCO 下发GDW1376.2 的AFN=03H FN=7
   查询从节点监控最大时间)秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文，如未收到，则指示CCO 抄表上行转发失败，
   如收到1376.2 协议AFN13HF1 中包含的数据与电表应答报文不同，则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功，
   此测试流程结束，最终结论为此项测试通过。
check:
1. 测试CCO 转发的下行抄表数据报文时其报文端口号是否为0x11；
2. 测试CCO 转发的下行抄表数据报文时其报文ID 是否为0x0001（集中器主动抄表）；
3. 测试CCO 转发的下行抄表数据报文时其报文控制字是否为0；
4. 测试CCO 转发的下行抄表数据报文时其协议版本号是否为1；
5. 测试CCO 转发的下行抄表数据报文时其报文头长度是否符合在0-64 范围内；
6. 测试CCO 转发的下行抄表数据报文时其配置字是否为0；
7. 测试CCO 转发的下行抄表数据报文时其转发数据的规约类型是否为2（DL/T645-07）；
8. 测试CCO 转发的下行抄表数据报文时其报文序号是否递增；
9. 测试CCO 转发的下行抄表数据报文时其选项字=0（方向位：下行）；
10. 测试CCO 转发的下行抄表数据报文时其数据（DATA）是否为DL/T645 规约报文。
11. 监控集中器是否能收到待测CCO 转发的抄表上行报文。
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
    cct          = concentrator.Concentrator()
    cct.open_port()

    # 1. 连接设备，上电初始化。
    # 2. 软件平台模拟集中器向待测CCO 下发“设置主节点地址”命令，在收到“确认”后，
    #    向待测CCO 下发“添加从节点”命令，将目标网络站点的MAC 地址下发到CCO 中，等待“确认”。
    plc_tb_ctrl._debug("Step 1, 2: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 3. 软件平台模拟集中器向待测CCO 发送目标站点为STA 的Q／GDW 1376.2 协议AFN13HF1（“监控从节点”命令）
    #    启动集中器主动抄表业务，用于点抄 STA 所在设备（DL/T645-2007 规约虚拟电表000000000001）当前时间。
    plc_tb_ctrl._debug("Step 3: simulate CCT to send CCO 1376.2 pkt (AFN=13, F=1), MONITOR NODE ...")

    dl_afn13f1_pkt = tb._load_data_file(data_file='afn13f1_dl.yaml')
    dl_afn13f1_pkt['cf']['prm']  = 'MASTER'
    dl_afn13f1_pkt['user_data']['value']['r']['comm_module_flag']  = 1
    dl_afn13f1_pkt['user_data']['value']['r']['sn']                = gdw1376p2_sn
    dl_afn13f1_pkt['user_data']['value']['a']['src']               = cco_mac
    dl_afn13f1_pkt['user_data']['value']['a']['dst']               = sta_mac

    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn13f1_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    # 4. 软件模拟STA+电表，待测CCO 向其下发抄表下行报文，抄读当前的时间数据项，测试平台回复抄表上行报文。
    # 等待CCO发送抄表命令（ID=0001）给STA
    plc_tb_ctrl._debug("Step 4: simulate STA to receive and ack APL CCT METER READ cmd ...")
    plc_tb_ctrl._debug("Step 4.1: simulate STA to receive APL CCT Meter Read cmd ...")

    pkt_id = 'APL_CCT_METER_READ'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 3)
    assert apm is not None,                                    "APL_CCT_METER_READ not received"
    # check 1. 测试CCO 转发的下行抄表数据报文时其报文端口号是否为0x11；
    assert apm.header.port             == 0x11,                "pkt header port id err"
    # check 2. 测试CCO 转发的下行抄表数据报文时其报文ID 是否为0x0001（集中器主动抄表）；
    assert apm.header.id               == pkt_id,              "pkt header packet id err"
    # check 3. 测试CCO 转发的下行抄表数据报文时其报文控制字是否为0；
    assert apm.header.ctrl_word        == 0,                   "pkt header ctrl word err"
    # check 4. 测试CCO 转发的下行抄表数据报文时其协议版本号是否为1；
    assert apm.body.dl.proto_ver       == 'PROTO_VER1',        "pkt body proto ver err"
    # check 5. 测试CCO 转发的下行抄表数据报文时其报文头长度是否符合在0-64 范围内；
    assert apm.body.dl.hdr_len         <= 64,                  "pkt body data len err"
    # check 6. 测试CCO 转发的下行抄表数据报文时其配置字是否为0；
    assert apm.body.dl.cfg_word        == 0,                   "pkt body cfg word err"
    # check 7. 测试CCO 转发的下行抄表数据报文时其转发数据的规约类型是否为2（DL/T645-07）；
    assert apm.body.dl.data_proto_type == 'PROTO_DLT645_2007', "pkt body data proto type err"
    # check 8. 测试CCO 转发的下行抄表数据报文时其报文序号是否递增；
#    assert apm.body.sn                 == 1,                   "pkt body sn not increased err"
    # check 9. 测试CCO 转发的下行抄表数据报文时其选项字=0（方向位：下行）；
    assert apm.body.dl.dir_bit         == 'DL',                "pkt body directrion bit err"
    # check 10. 测试CCO 转发的下行抄表数据报文时其数据（DATA）是否为DL/T645 规约报文。
    assert apm.body.dl.data[0]         == 0x68,                "pkt body data err"
    assert apm.body.dl.data[7]         == 0x68,                "pkt body data err"
    assert apm.body.dl.data[15]        == 0x16,                "pkt body data err"

    dl_meter_read_pkt_sn = apm.body.dl.sn
    plc_tb_ctrl._debug("dl_meter_read_pkt_sn = {}".format(dl_meter_read_pkt_sn))

    # 软件模拟STA+电表, 回复抄表上行报文。
    plc_tb_ctrl._debug("Step 4.2: simulate STA to ack APL CCT Meter Read cmd ...")

    ul_meter_read_pkt               = tb._load_data_file(data_file='apl_cct_meter_read_ul.yaml')
    ul_meter_read_pkt['body']['sn'] = dl_meter_read_pkt_sn

    ul_dlt645 = []
    ul_dlt645.extend(ul_meter_read_pkt['body']['data'])
    msdu      = plc_packet_helper.build_apm(dict_content=ul_meter_read_pkt, is_dl=False)
#    plc_tb_ctrl._debug("msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=0, dst_tei=1)

    tc_common.wait_for_tx_complete_ind(tb)

    # 5. 测试平台监控是否能够在n(n=模拟集中器对被测CCO 下发GDW1376.2 的AFN=03H FN=7
    #    查询从节点监控最大时间)秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文，如未收到，则指示CCO 抄表上行转发失败，
    #    如收到1376.2 协议AFN13HF1 中包含的数据与电表应答报文不同，则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功，
    #    此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 5: simulate CCT to receive 1376.2 pkt (AFN=13H, F=1)...")

    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1 应答报文
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x13, dt1=0x01, dt2=0, timeout=3)
    # check 11. 监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is not None,                               "AFN13H F1 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir               == 'UL',              "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm               == 'SLAVE',           "cf prm err"
    # PROTO_DLT645_07
    proto_type = frame1376p2.user_data.value.data.data.proto_type
    assert  proto_type                      == 'PROTO_DLT645_07', "data proto ver err"

    # 如收到1376.2 协议AFN13HF1 中包含的数据与电表应答报文不同，则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功
    frame645 = frame1376p2.user_data.value.data.data.packet
    assert cmp(frame645, ul_dlt645)         == 0,                 "pkt body data - 645 pkt err"

    cct.close_port()






