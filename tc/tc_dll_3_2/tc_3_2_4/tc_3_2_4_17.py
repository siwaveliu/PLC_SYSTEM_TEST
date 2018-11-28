# -- coding: utf-8 --

from robot.api import logger
from construct import *
import time
import plc_packet_helper
import test_data_reader
import test_frame_helper
import plc_tb_ctrl
import tc_common

'''
3.2.4.17 长 MPDU 帧载荷多包 MPDU 的 SOF 帧有错误报文是否对被测模块造成异常测试
验证长 mpdu 帧载荷多包 mpdu 的 sof 帧有错误报文时是否对被测模块造成异常
'''
def run(tb):
    """
    run function.

    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench), "tb type is plc_tb_ctrl.PlcSystemTestbench"
    tc_common.activate_tb(tb, plc_packet_helper.WORK_BAND1, 0, 1)

    tdr = test_data_reader.TestDataReader()
    tdr.open_port()

    band=0

    # 在频段0发送20次频段设置命令
    tb._change_band(0)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    # 在频段1发送20次频段设置命令
    tb._change_band(1)
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='CONFIG_BAND', param=band)

    tb._change_band(band)
    # 在指定频段发送20次测试命令帧，进入MAC透传测试模式
    for i in range(20):
        tc_common.send_comm_test_command(test_mode_cmd='ENTER_MAC_TRANS_MODE', param=10)

    time.sleep(1)

    tdr.clear_port_rx_buf()

    pb_size = 136
    pb_num_per_mpdu = 4
    total_pb_num = 4
    msdu_len = 490 # 如果是498字节，则136*4的格式容纳不下mac_head+msdu+crc32
    msdu = "".join([chr(i&0xFF) for i in range(msdu_len)])

    tb.mac_head.org_dst_tei = 0xFFF
    tb.mac_head.org_src_tei = 0
    tb.mac_head.tx_type = 'PLC_LOCAL_BROADCAST'
    tb.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb.mac_head.mac_addr_flag = 1
    tb.mac_head.src_mac_addr = "00-00-00-00-00-01"
    tb.mac_head.dst_mac_addr = "00-00-00-00-00-02"
    tb.mac_head.msdu_len = len(msdu)
    tb.mac_head.msdu_sn = tb._gen_msdu_sn()
    mac_head = plc_packet_helper.build_mac_frame_head(dict_content=tb.mac_head)

    crc = plc_packet_helper.calc_crc32(msdu)
    mac_frame = mac_head + msdu + plc_packet_helper.build_mac_frame_crc(crc)

    cnt = 0
    # 测试规范要求发送20次，但没有说明是不是每次都要收对，这里为了加快测试时间，只发送5次
    plc_tb_ctrl._debug("send wrong sof")
    while cnt < 5:
        sof_fc_pl_data = tc_common.build_sof_fc_pl_data(mac_frame, pb_size, pb_num_per_mpdu, 0, total_pb_num)

        data = list(sof_fc_pl_data['payload']['data'])
        modify_pos = 16 + 2 * 136 + 55
        data[modify_pos] = chr((ord(data[modify_pos])+1)&0xFF)
        sof_fc_pl_data['payload']['data'] = "".join(data)
        tb._send_fc_pl_data(sof_fc_pl_data)

        plc_tb_ctrl._debug('wait for TX_COMPLETE_IND')
        test_frame = tb.tb_uart.wait_for_test_frame("TX_COMPLETE_IND")
        assert test_frame is not None, 'TX_COMPLETE_IND Timeout'

        rx_msdu = tdr.read_frame(msdu_len, 1)
        if len(rx_msdu) == msdu_len:
            plc_tb_ctrl._trace_byte_stream("tx msdu", msdu)
            plc_tb_ctrl._trace_byte_stream("rx msdu", rx_msdu)
            assert False, "msdu not expected"

        time.sleep(5)
        cnt += 1

    cnt = 0
    plc_tb_ctrl._debug("send correct sof")
    # 测试规范要求发送20次，但没有说明是不是每次都要收对，这里为了加快测试时间，只发送5次
    while cnt < 5:
        sof_fc_pl_data = tc_common.build_sof_fc_pl_data(mac_frame, pb_size, pb_num_per_mpdu, 0, total_pb_num)
        tb._send_fc_pl_data(sof_fc_pl_data)

        plc_tb_ctrl._debug('wait for TX_COMPLETE_IND')
        test_frame = tb.tb_uart.wait_for_test_frame("TX_COMPLETE_IND")
        assert test_frame is not None, 'TX_COMPLETE_IND Timeout'

        rx_msdu = tdr.read_frame(msdu_len, 1)
        if rx_msdu != msdu:
            plc_tb_ctrl._trace_byte_stream("tx msdu", msdu)
            plc_tb_ctrl._trace_byte_stream("rx msdu", rx_msdu)
            assert False, "msdu not match"

        time.sleep(5)
        cnt += 1
