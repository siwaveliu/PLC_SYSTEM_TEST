# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import tc_4_1
import time


'''
4.8 事件主动上报测试
验证多 STA 站点时，表端产生故障事件，事件主动上报准确性和效率
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"

    addListFile = u'./addrlist/互操作性表架拓扑地址_事件上报.txt'

    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    tc_4_1.run(tb, band)

    # 重新复位表架，造成上电的事件上报
    tb.meter_platform_power_reset()
    # 读取事件上报的地址列表
    top, nodelist = tc_common.read_node_top_list(addListFile, log=True)
    # 记录起始时间
    starttime = time.time()
    # 600s时间等待组网完成和事件上报，该时间与电科院并不一致
    while time.time() - starttime < 600:
        plc_tb_ctrl._debug("wait for AFN06F5")
        frame1376p2 = tb.cct.wait_for_gdw1376p2_frame(afn=0x06, dt1=16, dt2=0, timeout=time.time() - starttime, tm_assert=False)
        if frame1376p2 is not None:
            plc_tb_ctrl._debug(frame1376p2.userdata.a.src)

    if nodelist.__len__() != 0:
        s = ''
        for n in nodelist:
            s += n + "; "
        plc_tb_ctrl._debug("these are meters who don't report event: " + s)

    assert nodelist.__len__() == 0, "still have event that don't report"




