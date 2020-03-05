# -- coding: utf-8 --
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import time
import config

CONCENTRATOR_OTHER_PORT = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6']  # type: list

def run(tb, num, band, power_on=True):
    tb.meter_platform_power(1, 1, 2, 3, 4)
    time.sleep(10)
    for i in range(num):
        cct = concentrator.Concentrator(CONCENTRATOR_OTHER_PORT[i])
        cct.open_port()
        cct.mac_addr = '00-12-34-56-78-9{}'.format(str(i + 1))
        plc_tb_ctrl._debug(cct.mac_addr)
        tc_common.set_cco_mac_addr(cct, cct.mac_addr)
        plc_tb_ctrl._debug("reset CCO param area")
        tc_common.reset_cco_param_area(cct)
        tc_common.add_sub_node_addr(cct, ['88-88-88-88-88-88'])
        tc_common.write_cco_band(cct, band)
        cct.close_port()
    plc_tb_ctrl._debug("sleep 300s for cco save parameters")
    time.sleep(300)
    if power_on == False:
        tb.meter_platform_power(0, 1, 2, 3, 4)


