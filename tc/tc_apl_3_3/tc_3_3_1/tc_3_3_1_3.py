# -- coding: utf-8 --
# CCO 通过集中器主动并发抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper
import meter
import time

'''
1. 连接设备，上电初始化。
2. 软件平台模拟集中器向待测CCO 下发“设置主节点地址”命令，在收到“确认”后，向待测CCO 下发“添加从节点”命令，
   将目标网络站点的MAC 地址下发到CCO 中，等待“确认”。
3. 软件模拟集中器向待测CCO 启动集中器主动并发抄表业务，用于抄读STA 所在设备（DL/T645-2007 规约虚拟电表000000000001 ）
   多个数据项（读当前正向有功总电能、读日期和星期、读时间）。
4. 软件模拟STA+电表，待测CCO 向其下发集中器主动并发抄表下行报文，抄读当前的多个数据项，测试平台向组织抄表上行报文回复待测CCO。
5. 测试平台监控是否能够在n(n = 模拟集中器对被测CCO 下发GDW1376.2 的AFN=03HFN=7
   查询从节点监控最大时间)秒内收到CCO 上报的Q／GDW 1376.2 协议AFN13HF1应答报文，如未收到，则指示CCO 抄表上行转发失败，
   如收到1376.2 协议AFN13HF1 中包含的数据与电表应答报文不同，则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功，
   此测试流程结束，最终结论为此项测试通过。
check:
1. 测试CCO 转发的下行抄表数据报文时其报文端口号是否为0x11；
2. 测试CCO 转发的下行抄表数据报文时其报文ID 是否为0x0003（集中器主动并发抄表）；
3. 测试CCO 转发的下行抄表数据报文时其协议版本号是否为1；
4. 测试CCO 转发的下行抄表数据报文时其报文头长度是否符合在0-64 范围内；
5. 测试CCO 转发的下行抄表数据报文时其配置字是否为0x30 (未应答重试标志:1, 否认重试标志:1 )
6. 测试CCO 转发的下行抄表数据报文时其转发数据的规约类型是否为1（DL/T645-97）或2（DL/T645-07）；
7. 测试CCO 转发的下行抄表数据报文时其下发的报文序号是否递增；
8. 测试CCO 转发的下行抄表数据报文时其设备（电能表）超时时间是否为100ms 或设备（采集器）超时时间是否为200ms；
9. 测试CCO 转发的下行抄表数据报文时其数据（DATA）在规约类型00H 时，是否仅有一条抄表报文；
   规约类型为01H 或02H 时，报文内容是否有多条DL/T 645 报文（最多不超过13条），其中报文表地址一致；
10. 测试STA 转发抄表上行报文其应答状态是否为0（正常）；
11. 测试STA 转发抄表上行报文时其报文序号是否和抄表下行报文序号一致；
12. 监控集中器是否能收到待测CCO 转发的抄表上行报文。
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

    # 3. 软件模拟集中器向待测CCO 启动集中器主动并发抄表业务，用于抄读STA 所在设备（DL/T645-2007 规约虚拟电表000000000001 ）
    #    多个数据项（读当前正向有功总电能、读日期和星期、读时间）。
    plc_tb_ctrl._debug("Step 3: simulate CCT to send CCO 1376.2 pkt (AFN=F1, F=1) - the SIMU Meter Read cmd (Read Power, Read Date, Read Time)...")

    dl_afnf1f1_pkt = tb._load_data_file(data_file='afnf1f1_dl_empty.yaml')

    dl_dlt645_1           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x11, 0x04, 0x33, 0x33, 0x34, 0x33, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [0,1,0,0] 正向有功总电能

    dl_dlt645_2           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x11, 0x04, 0x34, 0x34, 0x33, 0x37, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [4,0,1,1] 日期和星期

    dl_dlt645_3           = [0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x11, 0x04, 0x35, 0x34, 0x33, 0x37, 0x00, 0x16,]    # [DI3,DI2,DI1,DI0] = [4,0,1,2] 时间

    dl_dlt645_1[-2]       = meter.calc_dlt645_cs8(map(chr, dl_dlt645_1))
    dl_dlt645_2[-2]       = meter.calc_dlt645_cs8(map(chr, dl_dlt645_2))
    dl_dlt645_3[-2]       = meter.calc_dlt645_cs8(map(chr, dl_dlt645_3))

    dl_dlt645             = []
    dl_dlt645.extend(dl_dlt645_1)
    dl_dlt645.extend(dl_dlt645_2)
    dl_dlt645.extend(dl_dlt645_3)

    dl_data_len           = len(dl_dlt645)

    dl_afnf1f1_pkt['cf']['prm']                                      = 'MASTER'
    dl_afnf1f1_pkt['user_data']['value']['r']['comm_module_flag']    = 1
    dl_afnf1f1_pkt['user_data']['value']['r']['sn']                  = gdw1376p2_sn
    dl_afnf1f1_pkt['user_data']['value']['a']['src']                 = cco_mac
    dl_afnf1f1_pkt['user_data']['value']['a']['dst']                 = sta_mac
    dl_afnf1f1_pkt['user_data']['value']['data']['data']['data_len'] = dl_data_len

    dl_afnf1f1_pkt['user_data']['value']['data']['data']['data'].extend(dl_dlt645)

    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afnf1f1_pkt)
    assert msdu is not None
    
    time.sleep(10)
    tb.tb_uart.clear_tb_port_rx_buf()
    cct.send_frame(msdu)

    # 4. 软件模拟STA+电表，待测CCO 向其下发集中器主动并发抄表下行报文，
    #    抄读当前的多个数据项，测试平台向组织抄表上行报文回复待测CCO。
    plc_tb_ctrl._debug("Step 4: simulate STA to receive and ack APL SIMU Meter Read cmd (Read Power, Read Date, Read Time)...")
    plc_tb_ctrl._debug("Step 4.1: simulate STA to receive APL SIMU Meter Read cmd (Read Power, Read Date, Read Time)...")
    
    pkt_id     = 'APL_CCT_SIMU_METER_READ'
    [timestamp, fc, mac_frame_head, apm] = tb._wait_for_plc_apm_dl(pkt_id, 3)

    dl_apl_645 = apm.body.data
    dl_apl_sn  = apm.body.sn
    # check 1. 测试CCO 转发的下行抄表数据时其报文端口号是否为0x11；
    assert apm.header.port                 == 0x11,                 "pkt header port id err"
    # check 2. 测试CCO 转发的下行抄表数据报文时其报文ID 是否为0x0003（集中器主动并发抄表）；
    assert apm.header.id                   == pkt_id,               "pkt header packet id err"
    # check . 测试STA 转发下行抄表数据时其报文控制字是否为0；
    assert apm.header.ctrl_word            == 0,                    "pkt header ctrl word err"
    # check 3. 测试CCO 转发的下行抄表数据时其协议版本号是否为1；
    assert apm.body.proto_ver              == 'PROTO_VER1',         "pkt body proto ver err"
    # check 4. 测试STA 转发的下行抄表数据时其报文头长度是否符合在0-64 范围内；
    assert apm.body.hdr_len                 < 64,                   "pkt body hdr len err"
    # check 5. 测试CCO 转发的下行抄表数据报文时其配置字是否为0x30 (未应答重试标志:1, 否认重试标志:1 )
    assert apm.body.no_rsp_retry           == 'RETRY',              "pkt body no rsp retry err"
    assert apm.body.nack_retry             == 'RETRY',              "pkt body nack retry err"

    # check 6. 测试CCO 转发的下行抄表数据报文时其转发数据的规约类型是否为1（DL/T645-97）或2（DL/T645-07）；
    assert (apm.body.data_proto_type == 'PROTO_DLT645_2007') or (apm.body.data_proto_type == 'PROTO_DLT645_97'),  "pkt body proto type err"
    # check 7. 测试CCO 转发的下行抄表数据报文时其下发的报文序号是否递增；
    # check 8. 测试CCO 转发的下行抄表数据报文时其设备（电能表）超时时间是否为100ms 或设备（采集器）超时时间是否为200ms；
    #assert apm.body.exp_time               == 1,                    "pkt body exp time err"

    # check 9. 测试CCO 转发的下行抄表数据报文时其数据（DATA）在规约类型00H 时，是否仅有一条抄表报文；
    #    规约类型为01H 或02H 时，报文内容是否有多条DL/T 645 报文（最多不超过13条），其中报文表地址一致；
    assert cmp(dl_apl_645, dl_dlt645)      == 0,                    "pkt body data - 645 pkt err"

    plc_tb_ctrl._debug("Step 4.2: simulate STA to ack APL SIMU Meter Read cmd (Read Power, Read Date, Read Time)...")

    ul_apl_pkt = tb._load_data_file(data_file='apl_cct_simu_meter_read_ul_empty.yaml')

    ul_dlt645_1           = [   # [DI3,DI2,DI1,DI0] = [0,1,0,0] 正向有功总电能 (123.45 kWh)
                             0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x91, 0x08, 0x33, 0x33, 0x34, 0x33, 0x33, 0x34,
                             0x4A, 0x60, 0x00, 0x16,
                            ]

    ul_dlt645_2           = [   # [DI3,DI2,DI1,DI0] = [4,0,1,1] 日期和星期 (2018-04-19, 星期四)
                             0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x91, 0x08, 0x34, 0x34, 0x33, 0x37, 0x45, 0x37,
                             0x46, 0x37, 0x00, 0x16,
                            ]

    ul_dlt645_3           = [   # [DI3,DI2,DI1,DI0] = [4,0,1,2] 时间 (16:09:41)
                             0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x68,
                             0x91, 0x07, 0x35, 0x34, 0x33, 0x37, 0x43, 0x3c,
                             0x5c, 0x00, 0x16,
                            ]

    ul_dlt645_1[-2]       = meter.calc_dlt645_cs8(map(chr, ul_dlt645_1))
    ul_dlt645_2[-2]       = meter.calc_dlt645_cs8(map(chr, ul_dlt645_2))
    ul_dlt645_3[-2]       = meter.calc_dlt645_cs8(map(chr, ul_dlt645_3))

    ul_dlt645             = []
    ul_dlt645.extend(ul_dlt645_1)
    ul_dlt645.extend(ul_dlt645_2)
    ul_dlt645.extend(ul_dlt645_3)

    ul_data_len           = len(ul_dlt645)

    ul_apl_pkt['body']['sn']             = dl_apl_sn
    ul_apl_pkt['body']['data_len']       = ul_data_len
    ul_apl_pkt['body']['pkt_rsp_status'] = 0x0007
    ul_apl_pkt['body']['data'].extend(ul_dlt645)

    plc_tb_ctrl._debug("dl_apl_sn = {}, ul_data_len={}".format(dl_apl_sn, ul_data_len))

    msdu = plc_packet_helper.build_apm(dict_content=ul_apl_pkt, is_dl=False)
#    plc_tb_ctrl._debug("msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=0, dst_tei=1)

    tc_common.wait_for_tx_complete_ind(tb)

    # 5. 测试平台监控是否能够在n(n = 模拟集中器对被测CCO 下发GDW1376.2 的AFN=03H FN=7
    #    查询从节点监控最大时间)秒内收到CCO 上报的Q／GDW 1376.2 协议AFNF1HF1应答报文，
    #    如未收到，则指示CCO 抄表上行转发失败，如收到1376.2 协议AFNF1HF1 中包含的数据与电表应答报文不同，
    #    则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功，此测试流程结束，最终结论为此项测试通过。
    plc_tb_ctrl._debug("Step 5: simulate CCT to receive 1376.2 pkt (AFN=F1H, F=1)...")
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0xF1, dt1=0x01, dt2=0, timeout=3)

    # check 12. 监控集中器是否能收到待测CCO 转发的抄表上行报文。
    assert frame1376p2 is not None,                               "AFNF1H F1 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir               == 'UL',              "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm               == 'SLAVE',           "cf prm err"
    # PROTO_DLT645_07
    proto_type = frame1376p2.user_data.value.data.data.proto_type
    assert proto_type                       == 'PROTO_DLT645_07', "data proto ver err"

    # 10. 测试STA 转发抄表上行报文其应答状态是否为0（正常）； <- The DUT is CCO instead of STA in this case...
    # 11. 测试STA 转发抄表上行报文时其报文序号是否和抄表下行报文序号一致；
    assert frame1376p2.user_data.value.r.sn == gdw1376p2_sn,      "pkt sn err"
    # 如收到1376.2 协议AFNF1HF1 中包含的数据与电表应答报文不同，则指示CCO 抄表上行转发数据错误，否则指示CCO 抄表上行转发数据成功
    frame645 = frame1376p2.user_data.value.data.data.data
    assert cmp(frame645, ul_dlt645)         == 0,                 "pkt body data - 645 pkt err"

    cct.close_port()






