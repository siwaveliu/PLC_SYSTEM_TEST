# -- coding: utf-8 --
# CCO 发送广播校时消息测试
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import meter


'''
1. 软件平台选择组网用例，待测设备CCO 上电；
2. 组网用例通过透明物理设备模拟STA 发送组网相关帧，配合待测CCO 和模拟集中器，组建一级网络；
3. 软件平台选择广播校时测试用例；
4. 测试用例启动模拟集中器通过串口向待测设备CCO发送符合376.2格式的集中器广播校时帧，同时启动定时器（3S）；
5. 待测设备CCO 启动广播校时任务，发送广播校时SOF 帧到电力线；
6. 在定时器耗尽前，透明物理设备接收到待测设备CCO 发送的广播校时SOF 帧，则上传到测试平台，再传到一致性评价模块。
   若未接收到广播校时SOF 帧，则测试失败。
7. 一致性评价模块判断广播校时SOF 帧的应用报文头及应用数据是否符合标准要求。
check:
1. 一致性评价模块应在定时器耗尽前，检测到CCO 发送的广播校时SOF 帧；
2. 一致性评价模块比较接收到的SOF 帧的应用报文头是否符合标准帧格式规范。
3. 一致性评价模块比较接收到的广播校时报文的日历时间应和系统时间相匹配（误差不超过2秒），否则测试失败；

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

    # 1. 软件平台选择组网用例，待测设备CCO 上电；
    # 2. 组网用例通过透明物理设备模拟STA 发送组网相关帧，配合待测CCO 和模拟集中器，组建一级网络；
    # 3. 软件平台选择广播校时测试用例；
    plc_tb_ctrl._debug("Step 1, 2, 3: Wait for system to finish network connecting...")

    sta_tei = tc_common.apl_cco_network_connect(tb, cct, cco_mac, sta_mac)

    # 4. 测试用例启动模拟集中器通过串口向待测设备CCO发送符合376.2格式的集中器广播校时帧，同时启动定时器（3S）；
    plc_tb_ctrl._debug("Step 4.1: simulate CCT to send CCO 1376.2 pkt (AFN=05, F=3) - time cali...")

#    frame = concentrator.build_gdw1376p2_frame(data_file='afn05f3_dl.yaml')

    dl_1376p2_pkt      = tb._load_data_file(data_file='afn05f3_dl.yaml')
    dl_1376p2_645      = dl_1376p2_pkt['user_data']['value']['data']['data']['data']
    dl_1376p2_645[-2]  = meter.calc_dlt645_cs8(map(chr, dl_1376p2_645))

    frame              = concentrator.build_gdw1376p2_frame(dict_content=dl_1376p2_pkt)

    assert frame is not None
    cct.send_frame(frame)

    # 等待CCO回应确认报文给集中器
    #    - 标准或测试规范未提及，但在“各个厂家测试用例汇总20170304_海思反馈.docs” 中提及
    plc_tb_ctrl._debug("Step 4.2: simulate CCT to receive CCO 1376.2 ack pkt (AFN=00, F=1)...")

    frame = cct.wait_for_gdw1376p2_frame(afn=0x00, dt1=0x01, dt2=0)
    #assert frame.user_data.value.data.data.cmd_status == 1

    # 5. 待测设备CCO 启动广播校时任务，发送广播校时SOF 帧到电力线；
    # 6. 在定时器耗尽前，透明物理设备接收到待测设备CCO 发送的广播校时SOF 帧，则上传到测试平台，
    #    再传到一致性评价模块。若未接收到广播校时SOF 帧，则测试失败。

    # 3秒内在模拟STA设备上应收到CCO发送的广播校时报文
    plc_tb_ctrl._debug("Step 5, 6: simulate STA to receive CCO APL TIME CALI cmd...")
    pkt_id = 'APL_TIME_CALI'

    [fc, mac_frame_head, apm] = tb._wait_for_plc_apm(pkt_id, timeout = 3)
    # check 1. 一致性评价模块应在定时器耗尽前，检测到CCO 发送的广播校时SOF 帧；
    # check 2. 一致性评价模块比较接收到的SOF 帧的应用报文头是否符合标准帧格式规范。
    assert apm is not None                         , "APL_TIME_CALI not received"

    # check 3. 一致性评价模块比较接收到的广播校时报文的日历时间应和系统时间相匹配（误差不超过2秒），否则测试失败；
    dl_apl_645 = apm.body.dl.data
    assert cmp(dl_apl_645, dl_1376p2_645)      == 0,                    "pkt body data - 645 pkt err"


    # 报文ID 是否为0x0004（广播校时报文）
#    assert apm.header.id        == pkt_id          , "pkt header packet id err"
#    assert apm.body.dl.length   == 18              , "time cali data length err" # length of the whole data field
#    assert apm.body.dl.data[7]  == 0x68            , "time cali 0x68 err"        #
#    assert apm.body.dl.data[8]  == 0x08            , "time cali ctrl word err"   # control word
#    assert apm.body.dl.data[9]  == 0x06            , "time cali time length err" # length of time field
#    assert apm.body.dl.data[10] == (0x33 + 0x32)   , "time cali seond err"       # second
#    assert apm.body.dl.data[11] == (0x33 + 0x16)   , "time cali minute err"      # minute
#    assert apm.body.dl.data[12] == (0x33 + 0x08)   , "time cali hour err"        # hour
#    assert apm.body.dl.data[13] == (0x33 + 0x04)   , "time cali day err"         # day
#    assert apm.body.dl.data[14] == (0x33 + 0x02)   , "time cali month err"       # month
#    assert apm.body.dl.data[15] == (0x33 + 0x18)   , "time cali year err"        # year

    cct.close_port()

