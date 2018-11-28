# -- coding: utf-8 --
# CCO 作为DUT,报文序号测试
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
   #1 DL/T6452007  电表能，
   #2 DL/T645 1997 电能表，
   #3 DL/T 698 电能表，并且报文序号与DUT下发【】查询从节点注册结果】命令中不吻合。
5. DUT 不通过【06HF4/376.2】命令上报从节点注册信息
check:
1. 确认DUT 没有成功获取从节点信息
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
    # 报文端口号是否为0x11
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # 报文ID 是否为0x0012（启动从节点注册）
    assert apm.header.id            == pkt_id,               "pkt header packet id err"
    # 报文控制字是否为0
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # 协议版本号是否为1
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
     # 报文头长度符合实际？
    assert apm.body.dl.hdr_len      == 8,                    "pkt body hdr len err"
    # 强制应答标志是否为0（固定值）？
    assert apm.body.dl.must_answer  == 'NOT_MUST_ANSWER',    "pkt body must answer err"
    # 从节点注册参数是否为1（启动从节点主动注册命令）？
    assert apm.body.dl.reg_para     == 'START_REG',          "pkt body reg para err"

    plc_tb_ctrl._debug("Step 3.2: simulate STA to receive CCO APL NODE REG QUERY cmd...")

    pkt_id = 'APL_NODE_REG_QUERY'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 5)
    assert apm is not None, "APL_NODE_REG_QUERY not received"
    # 报文端口号是否为0x11
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # 报文ID 是否为0x0011（查询从节点注册结果）
    assert apm.header.id            == pkt_id,               "pkt header packet id err"
    # 报文控制字是否为0
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # 协议版本号是否为1
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
    # 报文头长度符合实际？
    assert apm.body.dl.hdr_len      == 20,                   "pkt body hdr len err"
    # 强制应答标志是否为0（非强制应答）？
    assert apm.body.dl.must_answer  == 'NOT_MUST_ANSWER',    "pkt body must answer err"
    # 从节点注册参数是否为0（查询从节点注册结果命令）？
    assert apm.body.dl.reg_para     == 'QUERY_REG_RESULT',   "pkt body reg para err"
    # 源MAC 地址是否为CCO 的MAC 地址？
    assert apm.body.dl.src_mac      == cco_mac,              "pkt body src MAC err"
    # 源MAC 地址是否为CCO 的MAC 地址
    assert apm.body.dl.dst_mac      == sta_mac,              "pkt body dst MAC err"

    dl_sn = apm.body.dl.sn
    # 4. 软件平台让透明转发设备上报【查询从节点注册结果】，确保存在三块电表：
    #    #1DL/T645 2007 电表能，#2DL/T645 1997 电能表，#3 DL/T 698 电能表,
    #    并且报文序号与DUT下发【】查询从节点注册结果】命令中不吻合。
    plc_tb_ctrl._debug("Step 4: simulate STA to ack CCO APL NODE REG QUERY cmd, with invalid sn...")

    ul_sn = (dl_sn + 0x00FF0000) & 0xFFFFFFFF
    plc_tb_ctrl._debug("dl_sn = {}, ul_sn= {}".format(dl_sn, ul_sn))

    ul_node_reg_query_pkt = tb._load_data_file(data_file='apl_node_reg_query_ul.yaml')
    ul_node_reg_query_pkt['body']['sn']       = ul_sn
    ul_node_reg_query_pkt['body']['dev_addr'] = sta_mac
    ul_node_reg_query_pkt['body']['dev_id']   = sta_mac
    ul_node_reg_query_pkt['body']['src_mac']  = sta_mac
    ul_node_reg_query_pkt['body']['dst_mac']  = cco_mac

    msdu = plc_packet_helper.build_apm(dict_content=ul_node_reg_query_pkt, is_dl=False)
#    plc_tb_ctrl._debug("msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb.mac_head.org_dst_tei = 1
    tb.mac_head.org_src_tei = sta_tei
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb._send_msdu(msdu=msdu, mac_head=tb.mac_head, src_tei=0, dst_tei=1)
    tc_common.wait_for_tx_complete_ind(tb)

    # 5. DUT 不通过【06HF4/376.2】命令上报从节点注册信息
    # 监控是否能够在n秒内收到CCO 上报的Q／GDW 1376.2 协议AFN06HF4 应答报文
    plc_tb_ctrl._debug("Step 5: simulate CCT to receive CCO 1376.2 ack pkt (AFN=06, F=4), expected result = not received...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=0x08, dt2=0, timeout=3, tm_assert=False)

    # check 1. 确认DUT 没有成功获取从节点信息
    assert frame1376p2 is None,        "AFN06H F4 upstream ACK should not be received"
    plc_tb_ctrl._debug("Test Is Passed - AFN06HF4 is not received as expected")

    cct.close_port()






