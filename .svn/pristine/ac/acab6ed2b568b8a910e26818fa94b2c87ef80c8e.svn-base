# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper


'''
1. DUT 上电，通过软件平台配置透明转发设备通过DUT 成功入网。
2. 软件 平台向DUT 发送【11HF5/376.2】命令，激活DUT 下发【启动从节点注册】命令。
3. 在从节点注册过程中，DUT 下发【查询从节点注册结果】命令。
4. 软件平台让透明转发设备上报【查询从节点注册结果】，确保存在三块电表：
   #1 DL/T645 2007 电表能，
   #2 DL/T645 1997 电能表，
   #3 DL/T 698 电能表
5. DUT 通过【06HF4/376.2】命令上报从节点注册信息
check:
1.  确认DUT 下发【启动从节点注册】报文中，【报文端口号】是否为 0x11？
2.  确认DUT 下发【启动从节点注册】报文中，【报文ID】是否为0x0012？
3.  确认DUT 下发【启动从节点注册】报文中，【报文控制字】是否为 0？
4.  确认DUT 下发【启动从节点注册】报文中，【协议版本号】是否为 1？
5.  确认DUT 下发【启动从节点注册】报文中，【报文头长度】符合实际？
6.  确认DUT 下发【启动从节点注册】报文中，【强制应答标志】是否为0（固定值）？
7.  确认DUT 下发【启动从节点注册】报文中，【从节点注册参数】是否为1（启动从节点主动注册命令）？
8.  确认DUT 下发【查询从节点注册结果】报文中，【报文端口号】是否为 0x11？
9.  确认DUT 下发【查询从节点注册结果】报文中，【报文ID】是否为0x0011？
10. 确认DUT 下发【查询从节点注册结果】报文中，【报文控制字】是否为 0？
11. 确认DUT 下发【查询从节点注册结果】报文中，【协议版本号】是否为 1？
12. 确认DUT 下发【查询从节点注册结果】报文中，【报文头长度】符合实际？
13. 确认DUT 下发【查询从节点注册结果】报文中，【强制应答标志】是否为0（非强制应答）？
14. 确认DUT 下发【查询从节点注册结果】报文中，【从节点注册参数】是否为0（查询从节点注册结果命令）？
15. 确认DUT 下发【查询从节点注册结果】报文中，【源MAC 地址】是否为CCO 的MAC 地址？
16. 确认DUT 下发【查询从节点注册结果】报文中，【目的MAC 地址】是否为STA 的 MAC 地址？
17. 确认DUT 通过【06HF4/376.2】上报注册结果与实际匹配？
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

    # 1. DUT 上电，通过软件平台配置透明转发设备通过DUT 成功入网。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 2. 软件 平台向DUT 发送【11HF5/376.2】命令，激活DUT 下发【启动从节点注册】命令。
    plc_tb_ctrl._debug("Step 2.1: simulate CCT to send CCO 1376.2 pkt (AFN=11, F=5) - start node register...")

    dl_afn11f5_pkt = tb._load_data_file(data_file='afn11f5_dl.yaml')
    dl_afn11f5_pkt['cf']['prm']  = 'MASTER'
    dl_afn11f5_pkt['user_data']['value']['r']['sn']  = gdw1376p2_sn
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f5_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    plc_tb_ctrl._debug("Step 2.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=1)...")
    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0, timeout=3)
    assert frame1376p2 is not None,           "AFN00H F1 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir                == 'UL',          "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm                == 'SLAVE',       "cf prm err"
    assert frame1376p2.user_data.value.r.sn  == gdw1376p2_sn,  "sn err"
    gdw1376p2_sn += 1


    # 3. 在从节点注册过程中，DUT 下发【查询从节点注册结果】命令。
    plc_tb_ctrl._debug("Step 3.1: simulate STA to receive CCO APL NODE REG START cmd...")

    pkt_id = 'APL_NODE_REG_START'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 3)
    assert apm is not None,                                  "APL_NODE_REG_START not received"
    # check 1.  确认DUT 下发【启动从节点注册】报文中，【报文端口号】是否为 0x11？
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # check 2.  确认DUT 下发【启动从节点注册】报文中，【报文ID】是否为0x0012？
    assert apm.header.id            == pkt_id,               "pkt header packet id err"
    # check 3.  确认DUT 下发【启动从节点注册】报文中，【报文控制字】是否为 0？
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # check 4.  确认DUT 下发【启动从节点注册】报文中，【协议版本号】是否为 1？
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
    # check 5.  确认DUT 下发【启动从节点注册】报文中，【报文头长度】符合实际？
    assert apm.body.dl.hdr_len      == 8,                    "pkt body hdr len err"
    # check 6.  确认DUT 下发【启动从节点注册】报文中，【强制应答标志】是否为0（固定值）？
    assert apm.body.dl.must_answer  == 'NOT_MUST_ANSWER',    "pkt body must answer err"
    # check 7.  确认DUT 下发【启动从节点注册】报文中，【从节点注册参数】是否为1（启动从节点主动注册命令）？
    assert apm.body.dl.reg_para     == 'START_REG',          "pkt body reg para err"

    plc_tb_ctrl._debug("Step 3.2: simulate STA to receive CCO APL NODE REG QUERY cmd...")

    pkt_id = 'APL_NODE_REG_QUERY'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 5)
    assert apm is not None, "APL_NODE_REG_QUERY not received"
    # check 8.  确认DUT 下发【查询从节点注册结果】报文中，【报文端口号】是否为 0x11？
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # check 9.  确认DUT 下发【查询从节点注册结果】报文中，【报文ID】是否为0x0011？
    assert apm.header.id            == pkt_id,               "pkt header packet id err"
    # check 10. 确认DUT 下发【查询从节点注册结果】报文中，【报文控制字】是否为 0？
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # check 11. 确认DUT 下发【查询从节点注册结果】报文中，【协议版本号】是否为 1？
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
    # check 12. 确认DUT 下发【查询从节点注册结果】报文中，【报文头长度】符合实际？
    assert apm.body.dl.hdr_len      == 20,                   "pkt body hdr len err"
    # check 13. 确认DUT 下发【查询从节点注册结果】报文中，【强制应答标志】是否为0（非强制应答）？
    assert apm.body.dl.must_answer  == 'NOT_MUST_ANSWER',    "pkt body must answer err"
    # check 14. 确认DUT 下发【查询从节点注册结果】报文中，【从节点注册参数】是否为0（查询从节点注册结果命令）？
    assert apm.body.dl.reg_para     == 'QUERY_REG_RESULT',   "pkt body reg para err"
    # check 15. 确认DUT 下发【查询从节点注册结果】报文中，【源MAC 地址】是否为CCO 的MAC 地址？
    assert apm.body.dl.src_mac      == cco_mac,              "pkt body src MAC err"
    # check 16. 确认DUT 下发【查询从节点注册结果】报文中，【目的MAC 地址】是否为STA 的 MAC 地址？
    assert apm.body.dl.dst_mac      == sta_mac,              "pkt body dst MAC err"

    dl_sn = apm.body.dl.sn

    # 4. 软件平台让透明转发设备上报【查询从节点注册结果】，确保存在三块电表：#1DL/T645 2007 电表能，#2DL/T645 1997 电能表，#3 DL/T 698 电能表
    plc_tb_ctrl._debug("Step 4: simulate STA to ack CCO APL NODE REG QUERY cmd...")

    ul_node_reg_query_pkt = tb._load_data_file(data_file='apl_node_reg_query_ul.yaml')
    ul_node_reg_query_pkt['body']['sn'] = dl_sn
    plc_tb_ctrl._debug("dl_sn = {}".format(dl_sn))

    ul_node_reg_query_pkt['body']['dev_addr'] = sta_mac
    ul_node_reg_query_pkt['body']['dev_id']   = sta_mac
    ul_node_reg_query_pkt['body']['src_mac']  = sta_mac
    ul_node_reg_query_pkt['body']['dst_mac']  = cco_mac

    msdu = plc_packet_helper.build_apm(dict_content=ul_node_reg_query_pkt, is_dl=False)
    plc_tb_ctrl._debug("msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=0, dst_tei=1)

    tc_common.wait_for_tx_complete_ind(tb)

    # 5. DUT 通过【06HF4/376.2】命令上报从节点注册信息
    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN06HF4 应答报文
    plc_tb_ctrl._debug("Step 5: simulate CCT to receive CCO 1376.2 ack pkt (AFN=06, F=4)...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=0x08, dt2=0, timeout=3)

    # check 17. 确认DUT 通过【06HF4/376.2】上报注册结果与实际匹配？
    assert frame1376p2 is not None,        "AFN06H F4 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir  == 'UL',    "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm  == 'SLAVE', "cf prm err"
#    assert frame1376p2.user_data.value.data.node[0].dev_type == 0, "data device type err"  # GDW1376P2_DEV_METER

    cct.close_port()






