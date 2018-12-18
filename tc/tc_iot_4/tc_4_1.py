# -- coding: utf-8 --
import plc_tb_ctrl
import concentrator
import tc_common
import cco_switch_band
import config

'''
4.1 全网组网测试
验证多 STA 站点时组网准确性和效率
'''

def run(tb, band, escort=False):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
        如果没有开启陪测CCO，那么该函数会返回整个表架的拓扑图和地址列表
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"
    if  escort:
        node_addr_list_file = config.IOT_TOP_LIST_DETERMINAND
        node_addr_list_file_other = config.IOT_TOP_LIST_ESCORT
    else:
        node_addr_list_file = config.IOT_TOP_LIST_ALL

    cco_mac_addr = '00-00-00-00-00-9C'  # type: str
    cco_mac_addr_other = '00-00-00-00-00-9D'  # type: str

    if  escort:
        cct_other = concentrator.Concentrator(config.CONCENTRATOR_OTHER_PORT)
        cct_other.open_port()

    band = int(band)
    if  band != config.DEFAULT_BAND:
        cco_switch_band.run(tb, tb.cct, band)
        config.DEFAULT_BAND = band

    # 必须先打开串口以免上电后的延迟导致无法收到03H_F10


    # 确认CCO已经激活
    res = None
    for i in range(3):
        res = tb.cct.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1, tm_assert=False)
        if  res is None:
            tb.meter_platform_power_reset()
            continue
        else:
            break
    assert res is not None, "wait 03H_F10 failed, check cco device"
    if escort:
        for i in range(3):
            res = cct_other.wait_for_gdw1376p2_frame(afn=0x03, dt1=0x02, dt2=1, tm_assert=False)
            if res is None:
                tb.meter_platform_power_reset()
                continue
            else:
                break
        assert res is not None, "wait 03H_F10 failed, check cco_other device"
    # 设置CCO主节点地址
    plc_tb_ctrl._debug("set CCO addr={}".format(cco_mac_addr))
    tc_common.set_cco_mac_addr(tb.cct, cco_mac_addr)
    tb.cct.mac_addr = cco_mac_addr
    if escort:
        plc_tb_ctrl._debug("set other CCO addr={}".format(cco_mac_addr_other))
        tc_common.set_cco_mac_addr(cct_other, cco_mac_addr_other)
    # 清除CCO档案
    plc_tb_ctrl._debug("reset CCO param area")
    tc_common.reset_cco_param_area(tb.cct)
    if escort:
        plc_tb_ctrl._debug("reset other CCO param area")
        tc_common.reset_cco_param_area(cct_other)

    #set sub node address
    # 启动陪测CCO和STA组网
    if escort:
        plc_tb_ctrl._debug("set sub node address to consorting cco, and start the escort net")
        nw_top_main_other, sec_nodes_addr_list = tc_common.read_node_top_list(node_addr_list_file_other, cco_mac_addr, False)
        tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)
    # set sub node address
    plc_tb_ctrl._debug("set sub node address to main cco, and start the main net")
    nw_top_main, sec_nodes_addr_list = tc_common.read_node_top_list(node_addr_list_file, cco_mac_addr, False)
    tc_common.add_sub_node_addr(tb.cct, sec_nodes_addr_list)
    tc_common.check_nw_top(tb.cct, nw_top_main, 600)
    return nw_top_main, sec_nodes_addr_list










