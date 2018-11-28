# -- coding: utf-8 --
# CCO 在线本地升级流程测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_upg_common
import time

'''
1. 系统完成组网过程。
2. 平台模拟虚拟集中器，发送AFN=15，Fn=1（清除下装文件操作），虚拟集中器通过1376.2帧下发本地通信模块升级文件。

check:

'''

def run(tb):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"

    cco_mac = '00-00-00-00-00-9C'
    sta_mac = '00-00-00-00-00-01'
    cct     = concentrator.Concentrator()
    cct.open_port()

    # set the global variable image_file_name to cco image file name
    file_name_backup              = tc_upg_common.image_file_name
    tc_upg_common.image_file_name = tc_upg_common.cco_image_file_name

    # 1. 系统完成组网过程。
    plc_tb_ctrl._debug("Step 1: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 2. 平台模拟虚拟集中器，发送AFN=15，Fn=1（清除下装文件操作），
    #    虚拟集中器通过1376.2帧下发本地通信模块升级文件。
    plc_tb_ctrl._debug("Step 2.1: simulate CCT to send CCO AFN=15, Fn=1, FILE ID=00H (clear loaded file)")
    tc_upg_common.afn15f1_cmd_clear_file(tb_inst=tb, cct_inst=cct)

    plc_tb_ctrl._debug("Step 2.2: simulate CCT to send CCO AFN=15, Fn=1, FILE ID=03H (load upgrade file)")
    tc_upg_common.afn15f1_file_download(tb_inst=tb, cct_inst=cct, file_id=3, insert_heart_beat=True, sta_tei=sta_tei)

    # 等待CCO重启
#    plc_tb_ctrl._debug("Step 1: Wait for CCO reset and to finish network connecting...")
#    time.sleep(1)
#    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # recover the global variable image_file_name
    tc_upg_common.image_file_name = file_name_backup

    time.sleep(10)

    cct.close_port()






