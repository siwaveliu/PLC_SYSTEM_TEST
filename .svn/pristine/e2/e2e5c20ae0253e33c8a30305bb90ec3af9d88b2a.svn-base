# -- coding: utf-8 --
# CCO 作为DUT,停止从节点注册测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import plc_packet_helper


'''
1. DUT 上电，通过软件平台配置透明转发设备通过DUT 成功入网。
2. 软件 平台向DUT 发送【11HF5/376.2】命令，激活DUT 下发【启动从节点注册】命令。
3. 在确保搜表没有完成的情况下，软件平台向DUT 发送【11HF6/376.2】命令，激活DUT 下发【停止从节点注册】命令
check:
1. 确认DUT 下发【停止从节点注册】报文中，【报文端口号】是否为 0x11？
2. 确认DUT 下发【停止从节点注册】报文中，【报文ID】是否为0x0012？
3. 确认DUT 下发【停止从节点注册】报文中，【报文控制字】是否为 0？
4. 确认DUT 下发【停止从节点注册】报文中，【协议版本号】是否为 1？
5. 确认DUT 下发【停止从节点注册】报文中，【报文头长度】符合实际？
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

    plc_tb_ctrl._debug("Step 2.3: simulate STA to receive CCO APL NODE REG START cmd...")
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

    # 3. 在确保搜表没有完成的情况下，软件平台向DUT 发送【11HF6/376.2】命令，激活DUT 下发【停止从节点注册】命令
    plc_tb_ctrl._debug("Step 3.1: simulate CCT to send CCO 1376.2 pkt (AFN=11, F=6) - stop node register...")

    dl_afn11f5_pkt = tb._load_data_file(data_file='afn11f6_dl.yaml')
    dl_afn11f5_pkt['user_data']['value']['r']['sn']  = gdw1376p2_sn
    msdu = concentrator.build_gdw1376p2_frame(dict_content=dl_afn11f5_pkt)
    assert msdu is not None
    cct.send_frame(msdu)

    plc_tb_ctrl._debug("Step 3.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=1)...")

    frame1376p2 = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0, timeout=3)
    assert frame1376p2 is not None,           "AFN00H F1 upstream ACK not received"
    # 方向位=1 （上行）
    assert frame1376p2.cf.dir                == 'UL',          "cf directrion bit err"
    # prm=0 (SLAVE)
    assert frame1376p2.cf.prm                == 'SLAVE',       "cf prm err"
    assert frame1376p2.user_data.value.r.sn  == gdw1376p2_sn,  "sn err"
    gdw1376p2_sn += 1

    plc_tb_ctrl._debug("Step 3.3: simulate STA to receive CCO APL NODE REG STOP cmd...")

    pkt_id = 'APL_NODE_REG_STOP'
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 3)
    assert apm is not None,                                  "APL_NODE_REG_STOP not received"
    # check 1. 确认DUT 下发【停止从节点注册】报文中，【报文端口号】是否为 0x11？
    assert apm.header.port          == 0x11,                 "pkt header port id err"
    # check 2. 确认DUT 下发【停止从节点注册】报文中，【报文ID】是否为0x0012？
    assert apm.header.id            == pkt_id,               "pkt header packet id err"
    # check 3. 确认DUT 下发【停止从节点注册】报文中，【报文控制字】是否为 0？
    assert apm.header.ctrl_word     == 0,                    "pkt header ctrl word err"
    # check 4. 确认DUT 下发【停止从节点注册】报文中，【协议版本号】是否为 1？
    assert apm.body.dl.proto_ver    == 'PROTO_VER1',         "pkt body proto ver err"
    # check 5. 确认DUT 下发【停止从节点注册】报文中，【报文头长度】符合实际？
    assert apm.body.dl.hdr_len      == 8,                    "pkt body hdr len err"

    cct.close_port()






