# -- coding: utf-8 --
# CCO 在线升级补包机制测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_upg_common
import time

'''
1. 系统完成组网过程。
2. 平台模拟虚拟集中器，发送AFN=15，Fn=1（清除下装文件操作）。
3. 虚拟集中器通过376.2 帧发送AFN=15，Fn=1（子节点升级文件）。
4. CCO 下发开始升级报文，软件平台模拟STA 回复开始升级应答报文。
5. CCO 下发传输文件数据报文。
6. CCO 下发查询站点升级状态报文，软件平台模拟STA 回复查询站点升级状态应答报文，该报文提示部分数据包接收失败。
7. CCO 下发未成功传输文件数据报文。
8. CCO 下发查询站点升级状态报文，软件平台模拟STA 回复查询站点升级状态应答报文，该报文提示所有数据包接收完成。
9. CCO 下发执行升级报文。
check:
1. 检测虚拟STA 回复部分升级块接收失败升级状态应答报文后，查看CCO 是否补发未成功传输文件数据报文。
2. 检测CCO 在补发接收失败文件数据包后，查看是否发送查询站点升级状态报文。
3. 检测虚拟STA 回复数据块全部接收完成升级状态应答报文后，查看CCO 是否下发执行升级报文。

'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    cco_mac  = '00-00-00-00-00-9C'
    sta_mac  = '00-00-00-00-00-01'
    cct      = concentrator.Concentrator()
    cct.open_port()

    # 1. 系统完成组网过程。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 2. 平台模拟虚拟集中器，发送AFN=15，Fn=1（清除下装文件操作），
    plc_tb_ctrl._debug("Step 2: simulate CCT to send CCO AFN=15, Fn=1, FILE ID=00H (clear loaded file)")
    tc_upg_common.afn15f1_cmd_clear_file(tb_inst=tb, cct_inst=cct)

    # 3. 虚拟集中器通过376.2 帧发送AFN=15，Fn=1（子节点升级文件）。
    plc_tb_ctrl._debug("Step 3: simulate CCT to send CCO AFN=15, Fn=1, FILE ID=08H (load upgrade file)")
    tc_upg_common.afn15f1_file_download(tb_inst=tb, cct_inst=cct, insert_heart_beat=True, sta_tei=sta_tei)

    tb.tb_uart.clear_tb_port_rx_buf()

    tc_common.send_nml_heart_beat(tb, sta_tei=sta_tei) # to keep STA on-line

    time.sleep(5)

    # 4. CCO 下发开始升级报文，软件平台模拟STA 回复开始升级应答报文。
    # 5. CCO 下发传输文件数据报文。
    # 6. CCO 下发查询站点升级状态报文，软件平台模拟STA回复查询站点升级状态应答报文，该报文提示部分数据包接收失败。
    # 7. CCO 下发未成功传输文件数据报文。
    plc_tb_ctrl._debug("Step 3,4,5,6,and 7: simulate STA to ACK CCO START UPG pkts, and simulate some data rx failed, then get the re-sent pkts")
    tc_upg_common.apl_upg_sta_run_to_rx_complete(tb_inst=tb, sta_tei=sta_tei, simu_loss=True, loss_start=33, loss_end=44)
    # check 1. 检测虚拟STA 回复部分升级块接收失败升级状态应答报文后，查看CCO 是否补发未成功传输文件数据报文。

#    tc_common.send_nml_heart_beat(tb, sta_tei=sta_tei) # to keep STA on-line

    # 8. CCO 下发查询站点升级状态报文，软件平台模拟STA 回复查询站点升级状态应答报文，该报文提示所有数据包接收完成。
    plc_tb_ctrl._debug("Step 8: simulate STA to receive CCO QUERY STA UPG STATE pkt")
    tc_upg_common.apl_upg_sta_expect_pkt_id_rx_tx(tb_inst=tb, sta_tei=sta_tei, pkt_id='APL_UPGRADE_STATE_QUERY')
    # check 2. 检测CCO 在补发接收失败文件数据包后，查看是否发送查询站点升级状态报文。

    # 9. CCO 下发执行升级报文。
    plc_tb_ctrl._debug("Step 9: simulate STA to receive CCO EXEC UPG pkt and also QUERY STA INFO pkt")

    plc_tb_ctrl._debug("Step 9.1: simulate STA to receive CCO EXEC upgrade pkt")
    tc_upg_common.apl_upg_sta_expect_pkt_id_rx_tx(tb_inst=tb, sta_tei=sta_tei, pkt_id='APL_UPGRADE_EXEC')
    # check 3. 检测虚拟STA 回复数据块全部接收完成升级状态应答报文后，查看CCO 是否下发执行升级报文。

    tc_common.send_nml_heart_beat(tb, sta_tei=sta_tei) # to keep STA on-line
    tb.tb_uart.clear_tb_port_rx_buf()
    plc_tb_ctrl._debug("Step 9.2: simulate STA to receive CCO QUERY STA INFO pkt")
    tc_upg_common.apl_upg_sta_expect_pkt_id_rx_tx(tb_inst=tb, sta_tei=sta_tei, pkt_id='APL_STATE_INFO_QUERY')

    cct.close_port()






