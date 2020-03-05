# -- coding: utf-8 --
# CCO 通过集中器主动抄表测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import datetime
import meter
import tc_4_1


'''
4.6 广播校时测试
验证多 STA 站点时广播校时命令是否能准确下发
'''

def run(tb, band):
    """
    Args:
        tb (plc_tb_ctrl.PlcSystemTestbench): testbench object .
    """
    assert isinstance(tb, plc_tb_ctrl.PlcSystemTestbench),"tb type is not plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(tb.cct, concentrator.Concentrator), "tb.cct type is not concentrator"
    band = int(band)
    plc_tb_ctrl._debug("step1: switch band if needed, wait for net working")
    nw_top, nodes_list = tc_4_1.run(tb, band, False)

    # 激活tb，监听CCO发出广播校时帧
    for i in range(3):
        tb._change_band(band)

    plc_tb_ctrl._debug("step6: start time calibration")
    dl_1376p2_pkt = tb._load_data_file(data_file='afn05f3_dl.yaml')
    dl_1376p2_645 = dl_1376p2_pkt['user_data']['value']['data']['data']['data']
    now = datetime.datetime.now()
    now.second.__add__(1)
    snow = now.strftime("%S-%M-%H-%d-%m-%y")
    snow = snow.split('-')
    dl_1376p2_645[10] = int(snow[0])
    dl_1376p2_645[11] = int(snow[1])
    dl_1376p2_645[12] = int(snow[2])
    dl_1376p2_645[13] = int(snow[3])
    dl_1376p2_645[14] = int(snow[4])
    dl_1376p2_645[15] = int(snow[5])
    # 计算校验和必须放在645帧最后
    dl_1376p2_645[-2] = meter.calc_dlt645_cs8(map(chr, dl_1376p2_645))

    frame = concentrator.build_gdw1376p2_frame(dict_content=dl_1376p2_pkt)

    assert frame is not None
    tb.cct.send_frame(frame)
    tb.cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)
    pkt_id = "APL_TIME_CALI"
    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, 10)

    # check FC broadcast flag
    assert fc.var_region_ver.broadcast_flag == 1, "cco don't use broadcast mode"
    # check mac_head broadcast direction
    assert  mac_frame_head.broadcast_dir != 2, 'cco use wrong broadcast direction'
    # apl packet check
    assert apm is not None, "APL_TIME_CALI not received"
    # check 1. 测试CCO 转发的下行广播校时报文时其报文端口号是否为0x11；
    assert apm.header.port == 0x11, "pkt header port id err"
    # check 2. 测试CCO 转发的下行广播校时报文时其报文ID 是否为0x0001（集中器主动抄表）；
    assert apm.header.id == pkt_id, "pkt header packet id err"
    # check 3. 测试CCO 转发的下行广播校时报文时其报文控制字是否为0；
    assert apm.header.ctrl_word == 0, "pkt header ctrl word err"
    # check 4. 测试CCO 转发的下行广播校时数据没有改变内容
    dl_apl_645 = apm.body.dl.data
    assert cmp(dl_apl_645, dl_1376p2_645) == 0, "pkt body data - 645 pkt err"
