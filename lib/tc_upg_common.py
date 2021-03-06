# -- coding: utf-8 --
# 在线升级流程测试通用子模块
import os
import robot
import plc_tb_ctrl
import concentrator
import tc_common
import time
import plc_packet_helper
import copy
import meter
import random
import config

from formats import plc_apl
from copy import deepcopy
from glob import glob

upg_clock_rate         = (config.CLOCK_RATE)
upg_pkt_interval       = (0.01 * upg_clock_rate)   # 10ms delay, between every ack and the relative downstream pkt
upg_pkt_rx_timeout     = 10
msdu_sn                = 0.1


########################################################################
#     模拟集中器与CCO之间交互（1375.2 AFN=15 F=1）的通用子函数
########################################################################
afn15f1_frame_template = None  # 存放来自文件“afn15f1_dl_blank.yaml”的空白的原始模板
afn15f1_org_data       = None

#sta_image_file_name    = 'staplc_150030_0x9D842E0F.img'
#cco_image_file_name    = 'ccoplc_168430_0x56FF89E5.img'

sta_image_file_name    = 'staplc_*.img'
# get STA image's detail file name
firmware_img_file      = os.path.join(plc_tb_ctrl.curr_tc_dir, sta_image_file_name)
firmware_img_file      = glob(firmware_img_file)[0]
sta_image_file_name    = os.path.split(firmware_img_file)[-1]

cco_image_file_name    = 'ccoplc_*.img'
# get CCO image's detail file name
firmware_img_file      = os.path.join(plc_tb_ctrl.curr_tc_dir, cco_image_file_name)
firmware_img_file      = glob(firmware_img_file)[0]
cco_image_file_name    = os.path.split(firmware_img_file)[-1]

firmware_img_file      = None
image_file_name        = sta_image_file_name

# get file length and crc from file name
sLst                   = image_file_name.split('_')
firmware_length        = int(sLst[1])
firmware_crc_lst       = sLst[2].split('.')
firmware_crc           = eval(firmware_crc_lst[0])

afn15f1_sn             = 0     # sn
afn15f1_block_size     = 2048  # 暂时以2048字节/帧下发文件
afn15f1_block_num      = 0

def afn15f1_var_init():
    global firmware_img_file
    global afn15f1_frame_template
    global afn15f1_org_data
    global afn15f1_sn
    global afn15f1_block_size
    global afn15f1_block_num
#    global upg_pkt_interval

    firmware_img_file      = None
    afn15f1_frame_template = None  # 存放来自文件“afn15f1_dl_blank.yaml”的空白的原始模板
    afn15f1_org_data       = None
    afn15f1_sn             = 0     # sn
    afn15f1_block_size     = 2048  # 暂时以2048字节/帧下发文件
    afn15f1_block_num      = 0
#    upg_pkt_interval       = 0.02  # 2ms delay
    return


# 获取固件文件的指定偏移中的指定长度数据,
# 以list格式返回，同时返回下一次访问的偏移和当前拷贝的长度以及文件长度
def afn15f1_get_firmware_data(offset=0, size=afn15f1_block_size):
    global image_file_name
    global firmware_img_file
    global afn15f1_org_data
    global afn15f1_block_num

    blk_data  = []

    if afn15f1_org_data is None:
        firmware_img_file = os.path.join(plc_tb_ctrl.curr_tc_dir, image_file_name)
        firmware  = open(firmware_img_file, "rb")
        err_info  = "open {} failed".format(image_file_name)
        assert firmware is not None, err_info

        plc_tb_ctrl._debug("open file {} ok".format(image_file_name))
        afn15f1_org_data  = firmware.read()
        afn15f1_block_num = (len(afn15f1_org_data) + size - 1) / size
        firmware.close()

    fw_len = len(afn15f1_org_data)
    if offset >= fw_len:
        plc_tb_ctrl._debug("Error, offset = {}, fw_len = {}".format(offset, fw_len))

    assert offset < fw_len, "offset should not exceed file size"

    next_offset = offset + size

    if next_offset  > fw_len:
        next_offset = fw_len

    for i in range(offset, next_offset):
        blk_data.append(ord(afn15f1_org_data[i]))

    plc_tb_ctrl._debug("next_offset = {}, size = {}".format(next_offset, next_offset-offset))
    return [blk_data, next_offset, (next_offset-offset), fw_len]

# 在空白的模板基础上(afn15f1_dl_blank.yaml)，构建新的AFN15 F1报文
def afn15f1_frame_build(tb_inst, sn=None, file_id=None, file_att=None, file_ind=None, block_num=None, block_id=None, block_len=None, data=None):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench), "tb_inst type is plc_tb_ctrl.PlcSystemTestbench"

    global afn15f1_frame_template
    global afn15f1_block_num
    global afn15f1_block_size
    global afn15f1_sn

    if afn15f1_frame_template is None:
        afn15f1_frame_template = tb_inst._load_data_file(data_file='afn15f1_dl_blank.yaml')
        assert afn15f1_frame_template is not None, "Load afn15f1_dl_blank.yaml failed"
    dict1376p2 = deepcopy(afn15f1_frame_template)
#    dict1376p2 = tb_inst._load_data_file(data_file='afn15f1_dl_blank.yaml')
    if sn is not None:
        dict1376p2['user_data']['value']['r']['sn']                   = sn         # sn
    else:
        dict1376p2['user_data']['value']['r']['sn']                   = afn15f1_sn # sn

    if file_id is not None:
        dict1376p2['user_data']['value']['data']['data']['file_id']   = file_id

    if file_att is not None:
        dict1376p2['user_data']['value']['data']['data']['file_att']  = file_att
    else:
        dict1376p2['user_data']['value']['data']['data']['file_att']  = 0          # 起始帧/中间帧

    if file_ind is not None:
        dict1376p2['user_data']['value']['data']['data']['file_ind']  = file_ind
    else:
        dict1376p2['user_data']['value']['data']['data']['file_ind']  = 0          # 报文方式下装

    if block_num is not None:
        dict1376p2['user_data']['value']['data']['data']['block_num'] = block_num
    else:
        dict1376p2['user_data']['value']['data']['data']['block_num'] = 0

    if block_id is not None:
        dict1376p2['user_data']['value']['data']['data']['block_id']  = block_id

    if block_len is not None:
        dict1376p2['user_data']['value']['data']['data']['block_len'] = block_len
    else:
        dict1376p2['user_data']['value']['data']['data']['block_len'] = 0

    if data is not None:
        dict1376p2['user_data']['value']['data']['data']['data'].extend(data)

    frame1376p2 = concentrator.build_gdw1376p2_frame(dict_content=dict1376p2)

    return frame1376p2

# 接收AFN=15,F=1 上行应答报文, 如果参数block_id不为空，则须检查block_id
def afn15f1_ack_rx(cct_inst, sn=None, block_id=None, timeout=3):
    assert isinstance(cct_inst, concentrator.Concentrator), "cct_inst type is concentrator.Concentrator"
    frame1376p2 = cct_inst.wait_for_gdw1376p2_frame(afn=0x15, dt1=0x01, dt2=0, timeout=timeout)
    assert frame1376p2 is not None,   "AFN15H F1 upstream ACK not received"  # 监控集中器是否能收到待测CCO 发出的上行应答报文。
    assert frame1376p2.cf.dir  == 'UL',  "cf directrion bit err"             # 方向位=1 （上行）
    assert frame1376p2.cf.prm  == 'SLAVE',  "cf prm err"                     # prm=0 (SLAVE)
    if sn is not None:
        assert frame1376p2.user_data.value.r.sn == sn, "sn err"              # sn
    if block_id is not None:
        assert frame1376p2.user_data.value.data.data.block_id == block_id, "block id err"  # block id

    return frame1376p2

# 下发清除下装文件，并接收应答
def afn15f1_cmd_clear_file(tb_inst, cct_inst):
    global afn15f1_sn
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench), "tb_inst type is plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct_inst, concentrator.Concentrator),     "cct_inst type is concentrator.Concentrator"

    afn15f1_var_init()    # global variable initialization

    sn = afn15f1_sn
    frame1376p2 = afn15f1_frame_build(tb_inst=tb_inst, sn=sn, file_id='AFN15F1_CLEAR_FILE', block_id=0)

    assert frame1376p2 is not None, "build 1376p2 Clear File frame failed"

    # 发送报文
    cct_inst.send_frame(frame1376p2)
    afn15f1_sn += 1

    # 接收应答
    afn15f1_ack_rx(cct_inst=cct_inst, sn=sn, block_id=0)
    return

# 下发文件块数据，并接收应答
def afn15f1_cmd_send_data(tb_inst, cct_inst, sn=None, file_id=8, blk_id=0, blk_size=None):
    global afn15f1_block_num
    global afn15f1_block_size
    global afn15f1_sn

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench), "tb_inst type is plc_tb_ctrl.PlcSystemTestbench"
    assert isinstance(cct_inst, concentrator.Concentrator),     "cct_inst type is concentrator.Concentrator"

    if sn is None:
        sn = afn15f1_sn

    if blk_size is None:
        blk_size = afn15f1_block_size

    fw_offset = blk_id * blk_size
    plc_tb_ctrl._debug("blk_id = {}, blk_size = {}, fw_offset= {}".format(blk_id, blk_size, fw_offset))

    [data, next_offset, size, fw_len] = afn15f1_get_firmware_data(offset=fw_offset, size=blk_size)
    assert afn15f1_block_num is not None, "error to get firwmare data"

    file_att = 0       # 起始帧/中间帧
    if next_offset == fw_len:
        plc_tb_ctrl._debug("Meet the last block, set file_att = 1 ")
        file_att = 1   # 结束帧

    if size > 0:
        frame = afn15f1_frame_build(tb_inst=tb_inst, sn=sn, file_id=file_id, file_att=file_att, block_id=blk_id, block_num=afn15f1_block_num, block_len=size, data=data)
        assert frame is not None, "construct afn15f1 frame failed"

    else:
        plc_tb_ctrl._debug("No data to be sent")
        frame = None
        return False

    # 发送报文
    plc_tb_ctrl._debug("frame len = {}, sn = {}".format(len(frame), afn15f1_sn))
    cct_inst.send_frame(frame)
    afn15f1_sn += 1
    afn15f1_sn &= 0xFF    # sn only occupies 1 byte

    # 接收应答
    afn15f1_ack_rx(cct_inst=cct_inst, sn=sn, block_id=blk_id)

    return True

def afn15f1_file_download(tb_inst, cct_inst, file_id=8, insert_heart_beat=False, sta_tei=2):
    global upg_pkt_interval
    global afn15f1_sn
    global afn15f1_block_size
    block_id = 0
    tmp_blk_id = 16
    ret_val = afn15f1_cmd_send_data(tb_inst=tb_inst, cct_inst=cct_inst, sn=afn15f1_sn, file_id=file_id, blk_id=block_id, blk_size=afn15f1_block_size)
    plc_tb_ctrl._debug('->ret_val = {},afn15f1_block_num = {},afn15f1_sn = {}'.format(ret_val,afn15f1_block_num,afn15f1_sn))
    while ret_val == True:
        block_id += 1
        if block_id == afn15f1_block_num:
            plc_tb_ctrl._debug("block id == block num, File download is ended")
            break
        if insert_heart_beat and (block_id == tmp_blk_id):
            tc_common.send_nml_heart_beat(tb_inst=tb_inst, sta_tei=sta_tei) # to keep STA on-line
            tmp_blk_id <<= 1

        time.sleep(upg_pkt_interval)
        ret_val = afn15f1_cmd_send_data(tb_inst=tb_inst, cct_inst=cct_inst, sn=afn15f1_sn, file_id=file_id, blk_id=block_id, blk_size=afn15f1_block_size)

    plc_tb_ctrl._debug("File_download finished, total block num={}, block_len={}, tx block num={}\n".format(afn15f1_block_num, afn15f1_block_size, block_id))

    return True

########################################################################
#     模拟STA与CCO之间交互的通用子函数
########################################################################
apl_upg_wait_for_sta_rst_s  = 60              # 等待STA重启时间, 暂定60秒
apl_upg_image_area_size     = 260 * 1024      # 每个固件分区大小为(256 + 4)KBytes
apl_upg_dft_blk_num         = (apl_upg_image_area_size + 400 - 1)/400
                                              # 数据块总数缺省值，
apl_upg_time_slot           = 3               # '升级时间窗', 单位: 分钟
apl_upg_time_to_rst         = 2               # '等待复位时间' 单位: 秒
apl_upg_try_running_time    = 20              # '试运行时间' 单位: 秒
apl_upg_blk_size_str        = 'UPG_BLK_SZ_4'  # APL 升级块大小
apl_upg_sent_blk_num        = 0               # 已发送数据块的数量，用于“查询升级状态应答报文”的检查

apl_upg_dev_info_type_num   = 6               # 基本信息元素类型总数
apl_upg_dev_info_bmp        = 0               # bitmap 用于检查应答

apl_upg_loss_flag           = False           # 是否模拟报文丢失标记


apl_upg_dev_info  = [
                      # 0 厂商编号,    2 Byte
                      {'length': 2, 'type': 'UPG_VENDOR_ID',    'value': [0x57, 0x53]},
                      # 1 版本信息,    2 Byte
                      {'length': 2, 'type': 'UPG_VERSION_INFO', 'value': [0x10, 0x20]},
                      # 2 Bootloader, 1 Byte
                      {'length': 1, 'type': 'UPG_BOOT_INFO',    'value': [0x11]},
                      # 3 CRC32,      4 Byte
                      {'length': 4, 'type': 'UPG_CRC32',        'value': [0x78, 0x56, 0x34, 0x12]},
                      # 4 文件长度，   4 Byte
                      {'length': 4, 'type': 'UPG_FILE_SIZE',    'value': [0x56, 0x34, 0x12, 0x00]},
                      # 5 设备类型，   1 Byte
                      {'length': 1, 'type': 'UPG_DEV_TYPE',     'value': [0xA5]},
                    ]

apl_upg_file_size         = 0            # 本次升级的文件大小
apl_upg_file_crc          = 0            # 本次升级的文件crc
apl_upg_img_buf           = [0 for i in range(apl_upg_image_area_size)]
                                         # 指向升级文件所存放的内存起始地址
apl_upg_blk_num           = 0            # 数据块总数，开始升级后，
                                         # 由收到的'升级文件大小'和'升级块大小'计算获得
apl_upg_blk_size          = 0            # 升级块大小
apl_sta_upg_id            = 0            # 本次升级的升级ID, 当模拟STA去测试CCO时使用
apl_cco_upg_id            = 0x1000       # 本次升级的升级ID，当模拟CCO去测试STA时使用
apl_bc_tei                = 0xFFF        # 广播TEI
apl_upg_state             = 0            # 当前状态机状态:
                                         # 0-空闲态, 1-接收进行态, 2-接收完成态, 3-升级进行态, 4-试运行态
apl_upg_start_err         = 0            # 开始升级文件的错误码，用于开始升级应答报文
apl_upg_bitmap            = [0 for i in range((apl_upg_dft_blk_num + 7)/8)]
                                         # 文件数据块对应的bitmap，
                                         # 此处按照最大字节数定义, 应该为 (apl_upg_blk_num+7)/8

# little endian
def apl_upg_ascii_str_2_num(asc_str):
    val = 0
    for i in range (len(asc_str)):
        ch = ord(asc_str[i])
        ch <<= (i << 3)
        val |= ch
    return val

# convert the Enum type 'apl_upg_block_size_enum_b16' to Integer
def apl_upg_blk_size_convert(size_e):
    size_str = plc_apl.apl_upg_block_size_enum_b16.build(size_e)
    size_int = apl_upg_ascii_str_2_num(size_str)
#    size_int=BytesInteger(len(size_str),swapped=True).parse(size_str)
    return size_int

# 清空升级过程中产生的记录
def apl_upg_record_clear():
    global msdu_sn
    global apl_upg_dft_blk_num
    global apl_upg_loss_flag
    global apl_sta_upg_id
    global apl_cco_upg_id
    global apl_upg_file_size
    global apl_upg_file_crc
    global apl_upg_blk_size
    global apl_upg_blk_num
    global apl_upg_start_err
    global apl_upg_state
    global apl_upg_bitmap
    global apl_upg_img_buf
    global apl_upg_sent_blk_num

    msdu_sn              = 0.1
    apl_upg_loss_flag    = False
    apl_sta_upg_id       = 0
    apl_cco_upg_id       = 0x1000
    apl_upg_file_size    = 0
    apl_upg_file_crc     = 0
    apl_upg_blk_size     = 0
    apl_upg_blk_num      = 0
    apl_upg_start_err    = 0
    apl_upg_state        = 0  # 0-空闲态
    apl_upg_bitmap       = [0 for i in range((apl_upg_dft_blk_num + 7)/8)]
    apl_upg_img_buf      = [0 for i in range(apl_upg_image_area_size)]
    apl_upg_sent_blk_num = 0

    return


# 判定指定字节串bitmap里面，从byte[0]的bit[0]开始，连续指定数量blk_num的位是否全为1
def apl_upg_is_all_bit_set(bitmap, blk_num):
    mask = [0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF]
    if blk_num == 0:
        return True
    byte_pos = (blk_num - 1) >> 3    # blk_num - 1 除以8的商，为最后一个bit所在的字节位置
    bit_pos  = (blk_num - 1) & 7     # blk_num - 1 除以8的余数，为最后一个bit所在字节的bit位置

    for i in range (byte_pos):
        if bitmap[i] != 0xFF:
            return False

    if mask[bit_pos] != (mask[bit_pos] & bitmap[byte_pos]):
        return False

    return True

# 根据指定的起始位(块号)st_blk和连续拷贝位数(块数)blk_num，从源位图src_bm中拷贝数据返回
def apl_upg_blk_bmp_copy(src_bm, st_blk, blk_num):
    dst_bmp         = []
    start_byte      = 0       # 需拷贝的起始字节
    start_bit       = 0       # 需拷贝的起始字节的起始bit
    total_byte      = 0       # 需拷贝的字节数
    tmp_cpy_byte    = 0       # 需拷贝的字节数
    mask            = [0x00, 0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F]
                              # 此处为对应start_bit需要移出，去往相邻的高字节的数据的掩码；
    if blk_num == 0:
        return None
    start_byte = st_blk >> 3        # 除以8的商
    start_bit  = st_blk & 0x7       # 除以8的余数
    total_byte = (blk_num +7) >> 3  # 如果起始bit是字节对齐的话, 则此处为涉及拷贝数据的最大字节数
    if start_bit == 0:
        tmp_cpy_byte = total_byte
    else:
        # 此处综合考虑起始bit不对齐情况，以及总拷贝数据非整字节数的情况
        tmp_cpy_byte = total_byte + (((blk_num & 7) + start_bit - 1) >> 3)

    # 先按照字节，从源字节串指定字节偏移，向目的字节串拷贝相应长度的数据
    dst_bmp.extend(src_bm[start_byte: start_byte + tmp_cpy_byte])
    # 然后处理起始位的偏移
    if start_bit != 0:
        dst_bmp[0] >>= start_bit           # 往低位移动
        for i in range(1, tmp_cpy_byte):
            tmp_data = dst_bmp[i] & mask[start_bit]
            tmp_data <<= (8 - start_bit)
            dst_bmp[i]   >>= start_bit     # 往低位移动
            dst_bmp[i-1] |=  tmp_data

    return dst_bmp[:total_byte]

###################################################
# 下面是CRC计算的相关算法所需子函数
crc_table = [0 for i in range(256)]

# 位逆转
def drv_bit_rev(value, bw):
    val = 0
    for i in range(bw):
        if (value & 0x01) > 0:
            val |= (1 << (bw - 1 - i))
        value >>= 1

    return val

# 生成crc_table, 供CRC计算
def drv_crc_init(poly, bw):
    global crc_table

    poly = drv_bit_rev(poly, bw)
    for i in range(256):
        c = i
        for j in range(8):
            if (c & 1) > 0:
                c = poly ^ (c >> 1)
            else:
                c = c >> 1
        crc_table[i] = c
    return

# CRC计算
def drv_crc_calc(crc, pch, size, crc_len, input_rev, output_rev):
    global crc_table

    for i in range (size):
        if input_rev is False:
            pch[i] = drv_bit_rev(pch[i], 8)
        index = (crc ^ pch[i]) & 0xFF
        crc = (crc >> 8) ^ crc_table[index]

    if input_rev is False:
        crc = drv_bit_rev(crc, crc_len)

    return crc

# HAL层计算给定长度size的数据data的32位CRC校验和
def hal_calc_crc32_rev(crc_init, data, size):
    poly = 0x04C11DB7
    bw = 32
    drv_crc_init(poly, bw)
    crc = drv_crc_calc(crc_init, data, size, bw, True, True)
    return crc

# 计算给定长度size的数据data的32位CRC校验和
def apl_upg_calc_crc(data, size):
    crc_value = 0xFFFFFFFF
    crc_value = hal_calc_crc32_rev(crc_value, data, size)
#    assert ret,    "apl_calc_crc32 return false"
    crc_value ^= 0xFFFFFFFF
    plc_tb_ctrl._debug("apl_upg_calc_crc crc_value={}".format(crc_value))
    return crc_value

########################################################################
#   对来自CCO的APL下行升级报文解析

# '开始升级'下行报文的解析 (需应答)
def apl_upg_start_parse(tb_inst, apm):
    global apl_upg_image_area_size

    global firmware_length
    global firmware_crc

    global apl_sta_upg_id
    global apl_upg_file_size
    global apl_upg_file_crc
    global apl_upg_blk_size
    global apl_upg_blk_num
    global apl_upg_start_err

    global apl_upg_state

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),   "tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"
    # 升级ID不能为0
    assert apm.body.dl.upg_id          > 0,                       "upg_start upg id err"
    if apl_sta_upg_id > 0:
        assert apm.body.dl.upg_id == apl_sta_upg_id,              "upg_start upg id err"
        return True                              # apl_sta_upg_id > 0, 非空闲态，应忽略本报文, 但可继续应答

    rx_file_size = apm.body.dl.upg_file_size
    rx_file_crc  = apm.body.dl.upg_file_crc
    # 升级时间窗不应为0
    assert apm.body.dl.upg_time_slot   > 0,                       "upg_start upg time slot err"
    # 升级文件大小不应为0, 不应超过FLASH中固件分区大小
    assert rx_file_size  > 0 and rx_file_size <= apl_upg_image_area_size,    "upg_start upg file size invalid err"
    assert rx_file_size == firmware_length,                       "upg_start upg file size is unexpected changed err"
    #assert rx_file_crc  == firmware_crc,                          "upg_start upg file crc is unexpected changed err"

    # 记录本次升级的相关信息
    apl_sta_upg_id    = apm.body.dl.upg_id
    # 升级块大小应为100,200,300,400
    apl_upg_file_size = rx_file_size
    apl_upg_file_crc  = rx_file_crc
    apl_upg_blk_size  = apl_upg_blk_size_convert(apm.body.dl.upg_block_size)

    # 因之前都采用assert检查, 故此处错误码为0(ok)
    apl_upg_start_err = 0
    apl_upg_blk_num   = (apl_upg_file_size + apl_upg_blk_size - 1) / apl_upg_blk_size

    apl_upg_state     = 1     # 1-接收进行态
    plc_tb_ctrl._debug("upg_start parse ok")

    return True

# '停止升级'下行报文的解析
def apl_upg_stop_parse(tb_inst, apm):
    global apl_sta_upg_id
    global apl_upg_state

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),   "tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 升级ID检查
    assert apm.body.dl.upg_id  == 0 or apm.body.dl.upg_id == apl_sta_upg_id,  "upg_stop upg id err"

    # 升级停止, 清空本次升级的相关信息
    apl_upg_record_clear()
    plc_tb_ctrl._debug("upg_stop parse ok, record cleared")

    apl_upg_state = 0   # 0-空闲态
    return True

# '传输文件数据'下行报文的解析
def apl_upg_data_tx_parse(tb_inst, apm, loss_start=0, loss_end=0, sta_tei=2):
    global apl_sta_upg_id
    global apl_upg_state
    global apl_upg_blk_num
    global apl_upg_blk_size

    global apl_upg_bitmap
    global apl_upg_img_buf
    global apl_upg_file_size
    global apl_upg_file_crc
    global apl_upg_state
    global apl_upg_loss_flag
#    global apl_upg_file_state

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),   "tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 升级ID检查
    assert apm.body.dl.upg_id    == apl_sta_upg_id,               "upg_data_tx upg id err"
    # 检查数据块编号
    blk_id   = apm.body.dl.data_blk_id
    blk_size = apm.body.dl.data_blk_size
    assert blk_id                 < apl_upg_blk_num,              "upg_data_tx upg data block id err"
    # 检查数据块大小
    if blk_id == (apl_upg_blk_num - 1):
        # 最后一块报文
        assert blk_size          <= apl_upg_blk_size,             "upg_data_tx upg file size err"
    else:
        # 非最后一块报文, 块大小应该与'开始升级报文'中指定的长度一致
        assert blk_size          == apl_upg_blk_size,             "upg_data_tx upg file size err"

    if apl_upg_loss_flag and (blk_id in range(loss_start, loss_end +1)):
        # 模拟接收失败
        plc_tb_ctrl._debug("upg_data_tx simulate loss (blk id={}, blk size={})".format(blk_id, apl_upg_blk_size))
        return True

    if blk_id > (loss_end + 1):
        apl_upg_loss_flag = False

    # 插入心跳帧
    if (blk_id == (apl_upg_blk_num >> 2)) or (blk_id == (apl_upg_blk_num >> 1)) or (blk_id == (apl_upg_blk_num - (apl_upg_blk_num >> 2))):
        tc_common.send_nml_heart_beat(tb_inst=tb_inst, sta_tei=sta_tei)

    # 检查数据块编号对应的bit是否已经在bitmap中置位，如果已经置位则表示收到的是重复报文，应忽略
    byte_pos = blk_id >> 3     # 本数据块对应bit所在的字节编号
    bit_pos  = blk_id & 7      # 本数据块对应bit所在字节的bit编号
    if (apl_upg_bitmap[byte_pos] & (1 << bit_pos)) > 0:
        # 收到重复报文，忽略本报文后续数据处理
        plc_tb_ctrl._debug("upg_data_tx duplicated packet (blk id={})" .format(blk_id))
        return True
    else:
        # 设置bitmap对应的位
        apl_upg_bitmap[byte_pos] |= (1 << bit_pos)

    # 保存报文中的块数据
    plc_tb_ctrl._debug("Rx packet (blk id={}, blk size={})".format(blk_id, apl_upg_blk_size))
    for i in range(blk_size):
        data_offset = blk_id * apl_upg_blk_size
        apl_upg_img_buf[data_offset + i] = apm.body.dl.data[i]

    # 判断是否所有数据块收到，如果是的话，应该检查CRC; 并用CRC检查结果来触发状态机运行；
    if apl_upg_is_all_bit_set(apl_upg_bitmap, apl_upg_blk_num) == False:
        return True

    plc_tb_ctrl._debug("All blocks (num={}) RX done".format(apl_upg_blk_num))

    # CRC 检查
    crc32 = apl_upg_calc_crc(apl_upg_img_buf, apl_upg_file_size)
    plc_tb_ctrl._debug('apl_upg_file_size = {}'.format(apl_upg_file_size))
    apl_upg_file_crc = crc32
    if crc32 != apl_upg_file_crc:
        plc_tb_ctrl._debug("upg_data_tx CRC err - RX CRC={}, calc CRC={}".format(apl_upg_file_crc, crc32))
#        apl_upg_file_state = 2  # 2 - crc检查失败
        assert False

    plc_tb_ctrl._debug("upg_data_tx CRC check passed")
#    apl_upg_file_state = 1      # 1 - crc检查通过
    apl_upg_state = 2            # 2 - 接收完成态
    return True

# '传输文件数据（单播转本地广播）'下行报文的解析
def apl_upg_data_tx_bc_parse(tb_inst, apm):
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),   "tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"
    plc_tb_ctrl._debug("file data transfer (unicast to broadcast) is not supported yet")
    return True

# '查询站点升级状态'下行报文的解析 (需应答)
def apl_upg_state_query_parse(tb_inst, apm):
    global apl_sta_upg_id
    global apl_upg_blk_num

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),   "tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    query_blk_num = apm.body.dl.blk_num
    start_blk_id  = apm.body.dl.start_blk_id
    upg_id        = apm.body.dl.upg_id

    # 检查连续查询的块数
    if query_blk_num == 0xFFFF:
        # 查询所有块
        query_blk_num            = apl_upg_blk_num
        start_blk_id             = 0
        apm.body.dl.blk_num      = query_blk_num
        apm.body.dl.start_blk_id = start_blk_id
    else:
        # 检查起始块号
        assert start_blk_id < apl_upg_blk_num,                    "upg_state_query start block id err"
        # 检查起始块号 + 连续查询块数
        assert (start_blk_id + query_blk_num) <= apl_upg_blk_num, "upg_state_query start_blk_id + blk_num err"
    # 检查升级ID
    if upg_id != 0 or apl_sta_upg_id != 0:
        assert upg_id == apl_sta_upg_id,                          "upg_state_query upg id err"

    plc_tb_ctrl._debug("upg_state_query parse ok")

    return True

# '执行升级'下行报文的解析
def apl_upg_exec_parse(tb_inst, apm):
    global apl_sta_upg_id
    global apl_upg_dev_info
    global apl_upg_file_size
    global apl_upg_file_crc
    global apl_upg_wait_for_sta_rst_s
    global upg_clock_rate

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 检查升级ID
    assert apm.body.dl.upg_id == apl_sta_upg_id,                  "upg_exec upg id err"

    # 模拟STA重启, 更新设备信息中的CRC和length
    file_crc     = apl_upg_dev_info[3]['value']     # 3 - CRC32, 4Byte
    file_crc[0]  = apl_upg_file_crc          & 0xFF
    file_crc[1]  = (apl_upg_file_crc >>  8)  & 0xFF
    file_crc[2]  = (apl_upg_file_crc >> 16)  & 0xFF
    file_crc[3]  = (apl_upg_file_crc >> 24)  & 0xFF

    file_size    = apl_upg_dev_info[4]['value']     # 4 - 文件长度，4Byte
    file_size[0] = apl_upg_file_size         & 0xFF
    file_size[1] = (apl_upg_file_size >>  8) & 0xFF
    file_size[2] = (apl_upg_file_size >> 16) & 0xFF
    file_size[3] = (apl_upg_file_size >> 24) & 0xFF

#    apl_upg_wait_for_sta_rst_s = apm.body.dl.time_2_rst

    # 更新升级状态
    apl_upg_state = 3     # 3 - 升级进行态
    plc_tb_ctrl._debug("upg_exec - update record file_crc={}, file_size={}".format(file_crc, file_size))

    # 模拟STA重启（时间开销）
    plc_tb_ctrl._debug("upg_exec - simulate STA reboot, with {} seconds to be elapsed".format(apl_upg_wait_for_sta_rst_s * upg_clock_rate))
    time.sleep(apl_upg_wait_for_sta_rst_s * upg_clock_rate)
    return True

# '查询站点信息'下行报文的解析 (需应答)
def apl_upg_state_info_query_parse(tb_inst, apm):

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    info_num = apm.body.dl.info_num

    # 检查信息列表元素个数, 每个元素ID占 1 Byte
    # 信息元素个数不应该超过255，因为上行报文中该字段只有一个字节
    assert info_num <= 255,  "upg_state_info_query info num err"
    plc_tb_ctrl._debug("upg_state_info_query parse ok")

    return True

########################################################################
#   对来自CCO的APL下行升级报文的应答

# 发送'开始升级'上行应答报文
def apl_upg_start_ack(tb_inst, apm, sta_tei=0):
    global apl_sta_upg_id
    global apl_upg_start_err

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    ul_upg_start_ack_pkt = tb_inst._load_data_file(data_file='apl_upgrade_start_ul.yaml')
    ul_upg_start_ack_pkt['body']['upg_id'] = apl_sta_upg_id
    ul_upg_start_ack_pkt['body']['upg_start_result'] = apl_upg_start_err
    plc_tb_ctrl._debug("apl_upg_start_ack: apl_sta_upg_id = {}, apl_upg_start_err = {}".format(apl_sta_upg_id,apl_upg_start_err))
    msdu = plc_packet_helper.build_apm(dict_content=ul_upg_start_ack_pkt, is_dl=False)
#    plc_tb_ctrl._debug("upg_start_ack msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb_inst.mac_head.org_dst_tei = 1
    tb_inst.mac_head.org_src_tei = sta_tei
    tb_inst.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=0, dst_tei=1)

    #tc_common.wait_for_tx_complete_ind(tb_inst)

    return True

# 发送'查询升级状态'上行应答报文
def apl_upg_state_query_ack(tb_inst, apm, sta_tei=0):
    global apl_sta_upg_id
    global apl_upg_state
    global apl_upg_bitmap

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"
    query_blk_num = apm.body.dl.blk_num
    start_blk_id  = apm.body.dl.start_blk_id
    upg_id        = apm.body.dl.upg_id
    bit_map       = apl_upg_blk_bmp_copy(apl_upg_bitmap, start_blk_id, query_blk_num)

    ul_upg_state_query_pkt = tb_inst._load_data_file(data_file='apl_upgrade_state_query_ul_blank.yaml')
    ul_upg_state_query_pkt['body']['upg_id']         = apl_sta_upg_id
    ul_upg_state_query_pkt['body']['upg_st']         = apl_upg_state
    ul_upg_state_query_pkt['body']['valid_data_blk'] = query_blk_num
    ul_upg_state_query_pkt['body']['start_blk_id']   = start_blk_id
    ul_upg_state_query_pkt['body']['bit_map'].extend(bit_map)

    plc_tb_ctrl._debug("ul_upg_state_query_pkt: upg_id = {}, upg_st = {}, valid_data_blk={}, start_blk_id={}, bit_map={}".format(apl_sta_upg_id, apl_upg_state, query_blk_num, start_blk_id, bit_map))
    msdu = plc_packet_helper.build_apm(dict_content=ul_upg_state_query_pkt, is_dl=False)
#    plc_tb_ctrl._debug("upg_start_ack msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb_inst.mac_head.org_dst_tei = 1
    tb_inst.mac_head.org_src_tei = sta_tei
    tb_inst.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=0, dst_tei=1)

    #tc_common.wait_for_tx_complete_ind(tb_inst)

    return True


# 发送'查询站点信息'上行应答报文
def apl_upg_state_info_query_ack(tb_inst, apm, sta_tei=0):
    global apl_upg_dev_info_type_num
    global apl_upg_dev_info

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    ds_info_type_bmp = 0                               # 用于避免送下来的信息元素ID有重复。
    ds_info_num      = apm.body.dl.info_num
    info_list        = apm.body.dl.info_list
    us_info_num      = 0

    for i in range(ds_info_num):
        if info_list[i] < apl_upg_dev_info_type_num:   # 基本信息元素总数
            tmp_bit = 1 << info_list[i]
            if (ds_info_type_bmp & tmp_bit) == 0:
                ds_info_type_bmp |= tmp_bit            # 设置相应bit， 以免出现信息元素类型重复
                us_info_num      += 1

    ul_upg_state_info_query_ack_pkt = tb_inst._load_data_file(data_file='apl_state_info_query_ul_blank.yaml')
    # 填写升级ID
    ul_upg_state_info_query_ack_pkt['body']['upg_id']   = apl_sta_upg_id
    # 填写信息元素个数
    ul_upg_state_info_query_ack_pkt['body']['info_num'] = us_info_num
    # 填写信息数据列表
    us_info_list = ul_upg_state_info_query_ack_pkt['body']['info_list']

    for i in range(apl_upg_dev_info_type_num):
        tmp_bit = 1 << i
        if (ds_info_type_bmp & tmp_bit) > 0:
           us_info_list.append(apl_upg_dev_info[i])

    plc_tb_ctrl._debug("apl_upg_start_ack: apl_sta_upg_id = {}, apl_upg_start_err = {}".format(apl_sta_upg_id,apl_upg_start_err))
    msdu = plc_packet_helper.build_apm(dict_content=ul_upg_state_info_query_ack_pkt, is_dl=False)
#    plc_tb_ctrl._debug("upg_start_ack msdu = {}".format([hex(ord(d)) for d in msdu]))

    tb_inst.mac_head.org_dst_tei = 1
    tb_inst.mac_head.org_src_tei = sta_tei
    tb_inst.mac_head.msdu_type   = "PLC_MSDU_TYPE_APP"
    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=0, dst_tei=1)

    #tc_common.wait_for_tx_complete_ind(tb_inst)

    return True

########################################################
# APL 模拟STA - 升级报文交互的入口相关控制函数

# 模拟STA 对下行APL升级报文的解析及相关应答(单次交互)
def apl_upg_sta_single_rx_tx(tb_inst, sta_tei = 2, loss_start=0, loss_end=0, exp_pkt_id=None):
    global msdu_sn
    global upg_pkt_interval
    global upg_pkt_rx_timeout
    bc_mac_addr = 'FF-FF-FF-FF-FF-FF'
    #msg_id='APL_UPGRADE_START',
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"
    [fc, mac_frame_head, apm] = tb_inst._wait_for_plc_apm(timeout = upg_pkt_rx_timeout*2.5)
#    dst_mac = mac_frame_head.dst_mac_addr
#    src_mac = mac_frame_head.src_mac_addr
    assert mac_frame_head is not None,             "mac frame head is none"
    rx_msdu_sn = mac_frame_head.msdu_sn
    if rx_msdu_sn == msdu_sn :
        plc_tb_ctrl._debug("apl_upg_sta_single_rx_tx: received repeated pkt, drop")
        return 0
    msdu_sn = rx_msdu_sn
    assert apm is not None,                        "APL packet is not received"
    # 报文控制字是否为0
    assert apm.header.ctrl_word  == 0,             "pkt header ctrl word err"
    # 报文端口号是否为0x12, 升级业务
    assert apm.header.port       == 0x12,          "pkt header port id err"
    # 协议版本号是否为1
    assert apm.body.dl.proto_ver == 'PROTO_VER1',  "pkt body proto ver err"

    # clear the rx buf, every APL pkt received
#    tb_inst.tb_uart.clear_tb_port_rx_buf()


    pkt_id = apm.header.id

    if (exp_pkt_id is not None) and (exp_pkt_id == "APL_STATE_INFO_QUERY") and (pkt_id != exp_pkt_id):

        return 0

    if   pkt_id == 'APL_UPGRADE_START':        # '开始升级'下行报文的解析 (需应答)
        if apl_upg_start_parse(tb_inst, apm):
            time.sleep(upg_pkt_interval)
            apl_upg_start_ack(tb_inst, apm, sta_tei)

    elif pkt_id == 'APL_UPGRADE_STOP':         # '停止升级'下行报文的解析
        apl_upg_stop_parse(tb_inst, apm)

    elif pkt_id == 'APL_DATA_TRANSFER':        # '传输文件数据'下行报文的解析
        apl_upg_data_tx_parse(tb_inst, apm, loss_start, loss_end, sta_tei)

    elif pkt_id == 'APL_DATA_TRANSFER_BC':     # '传输文件数据（单播转本地广播）'下行报文的解析
        apl_upg_data_tx_bc_parse(tb_inst, apm)

    elif pkt_id == 'APL_UPGRADE_STATE_QUERY':  # '查询站点升级状态'下行报文的解析 (需应答)
        if apl_upg_state_query_parse(tb_inst, apm):
            time.sleep(upg_pkt_interval)
            apl_upg_state_query_ack(tb_inst, apm, sta_tei)

    elif pkt_id == 'APL_UPGRADE_EXEC':         # '执行升级'下行报文的解析
        apl_upg_exec_parse(tb_inst, apm)

    elif pkt_id == 'APL_STATE_INFO_QUERY':     # '查询站点信息'下行报文的解析 (需应答)
        if apl_upg_state_info_query_parse(tb_inst, apm):
            time.sleep(upg_pkt_interval)
            apl_upg_state_info_query_ack(tb_inst, apm, sta_tei)

    else:
        assert False, "pkt header packet id err"      # 报文ID 错误

    return pkt_id

# 接收指定pkt_id的APL报文，并应答
def apl_upg_sta_expect_pkt_id_rx_tx(tb_inst, sta_tei, pkt_id):
    global upg_pkt_rx_timeout
    stop_time = time.time() + upg_pkt_rx_timeout
    rx_pkt_id = '0'
    while rx_pkt_id != pkt_id:
        rx_pkt_id = apl_upg_sta_single_rx_tx(tb_inst=tb_inst, sta_tei=sta_tei, exp_pkt_id=pkt_id)

        if (stop_time is not None) and time.time() > stop_time:
            plc_tb_ctrl._debug("{} seconds time out".format(upg_pkt_rx_timeout))
            break
    err_str = "Expected to receive {}, but actually not, is {}".format(pkt_id,rx_pkt_id)
    assert rx_pkt_id == pkt_id,  err_str
    return

# 模拟STA处理升级过程从空闲态到接收完成态, 可以模拟[loss_start, loss_end]下行数据丢失
def apl_upg_sta_run_to_rx_complete(tb_inst, sta_tei = 2, simu_loss=False, loss_start=0, loss_end=0):
    global apl_upg_state
    global apl_upg_loss_flag
    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    apl_upg_record_clear()
    i       = 0
    apl_upg_loss_flag = simu_loss
    while 2 != apl_upg_state:    # 2 - 接收完成态
        apl_upg_sta_single_rx_tx(tb_inst, sta_tei, loss_start, loss_end)

    return

########################################################################
#   模拟CCO向STA发送APL下行升级报文

#  判定STA升级后运行的固件是否为CCO下载的固件
def apl_upg_is_new_image_ok():
    global apl_upg_file_size       # 本次升级的文件大小
    global apl_upg_file_crc        # 本次升级的文件crc
    global apl_upg_dev_info

    ret_val      = True
    rx_file_crc  = 0
    rx_file_size = 0

    for i in range(4):
        rx_file_crc  |= (apl_upg_dev_info[3]['value'][i] << (i << 3))
        rx_file_size |= (apl_upg_dev_info[4]['value'][i] << (i << 3))

    if (rx_file_crc != apl_upg_file_crc) or (rx_file_size != apl_upg_file_size):
        ret_val = False

    return ret_val

def apl_upg_cco_load_firmware():
    global image_file_name
    global firmware_img_file
    global apl_upg_file_size
    global apl_upg_file_crc
    global apl_upg_blk_size_str
    global apl_upg_blk_size
    global apl_upg_blk_num

    global apl_upg_img_buf

    if apl_upg_file_size == 0:
#        apl_upg_record_clear()
#

        firmware_img_file = os.path.join(plc_tb_ctrl.curr_tc_dir, image_file_name)
        firmware  = open(firmware_img_file, "rb")
        err_str   = "open {} failed".format(firmware)
        assert firmware is not None, err_str

        file_org_data     = firmware.read()
        apl_upg_file_size = len(file_org_data)
        for i in range (apl_upg_file_size):
            apl_upg_img_buf[i] = ord(file_org_data[i])

        apl_upg_file_crc  = apl_upg_calc_crc(apl_upg_img_buf, apl_upg_file_size)
        apl_upg_blk_size  = apl_upg_blk_size_convert(apl_upg_blk_size_str)
        apl_upg_blk_num   = (apl_upg_file_size + apl_upg_blk_size - 1)/apl_upg_blk_size

        plc_tb_ctrl._debug("open file {} ok - size={}, crc={}, blk_size={}, blk_num={}".format(firmware, apl_upg_file_size, apl_upg_file_crc, apl_upg_blk_size, apl_upg_blk_num))

        firmware.close()
    return

# 发送'开始升级'下行报文
def apl_upg_start_send(tb_inst, sta_tei=0):
    global apl_cco_upg_id
    global apl_upg_time_slot         # '升级时间窗', 单位: 分钟
    global apl_upg_file_size         # 本次升级的文件大小
    global apl_upg_file_crc          # 本次升级的文件crc
    global apl_upg_blk_size_str      # APL 升级块大小

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    apl_upg_cco_load_firmware()

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_upgrade_start_dl.yaml')
    dl_upg_pkt['body']['upg_id']         = apl_cco_upg_id
    dl_upg_pkt['body']['upg_time_slot']  = apl_upg_time_slot
    dl_upg_pkt['body']['upg_block_size'] = apl_upg_blk_size_str
    dl_upg_pkt['body']['upg_file_size']  = apl_upg_file_size
    dl_upg_pkt['body']['upg_file_crc']   = apl_upg_file_crc

    plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

    tb_inst.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    return True

# 发送'停止升级'下行报文
def apl_upg_stop_send(tb_inst, sta_tei=0, upg_id=None):
    global apl_cco_upg_id
    global apl_bc_tei

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    if upg_id is None:
        upg_id = apl_cco_upg_id

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_upgrade_stop_dl.yaml')
    dl_upg_pkt['body']['upg_id']         = upg_id

    plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

#    tb_inst.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_dst_tei         = apl_bc_tei
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    #tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.tx_type             = 'PLC_MAC_PROXY_BROADCAST'

    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0,auto_retrans=False)

    return True

# 发送'文件传输'下行报文
def apl_upg_file_tx_send(tb_inst, sta_tei=0, blk_id=0, uc2bc_flag = 0):
    global apl_cco_upg_id
    global apl_upg_file_size
    global apl_upg_blk_size
    global apl_upg_blk_num
    global apl_upg_img_buf
    global apl_upg_bitmap

    uc2bc_body = None

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_data_transfer_dl_blank.yaml')
    if blk_id == (apl_upg_blk_num - 1):
        blk_size = apl_upg_file_size - apl_upg_blk_size * blk_id
    else:
        blk_size = apl_upg_blk_size

    if uc2bc_flag == 1:
        dl_upg_pkt['header']['id']       = 'APL_DATA_TRANSFER_BC'

    dl_upg_pkt['body']['upg_id']         = apl_cco_upg_id
    dl_upg_pkt['body']['data_blk_size']  = blk_size
    dl_upg_pkt['body']['data_blk_id']    = blk_id
    dl_upg_pkt['body']['data'].extend(apl_upg_img_buf[(apl_upg_blk_size * blk_id) : (apl_upg_blk_size * blk_id + blk_size)])

    # plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

    tb_inst.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    if uc2bc_flag == 1:
        uc2bc_body = copy.deepcopy(dl_upg_pkt['body'])
    else:
        # 以便后续查询时使用
        apl_upg_bitmap[blk_id >> 3] |= 1 << (blk_id & 7)

    return uc2bc_body

# 发送'查询站点升级状态'下行报文
def apl_upg_state_query_send(tb_inst, sta_tei=0, sent_blk_num=None):
    global apl_cco_upg_id
    global apl_upg_sent_blk_num
    global apl_upg_blk_num

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_upgrade_state_query_dl.yaml')
    if (sent_blk_num is None) or (sent_blk_num == 0):
        sent_blk_num = 0xFFFF       # all blocks
        apl_upg_sent_blk_num = apl_upg_blk_num
    else:
        apl_upg_sent_blk_num = sent_blk_num

    dl_upg_pkt['body']['blk_num']        = sent_blk_num
    dl_upg_pkt['body']['start_blk_id']   = 0       # 简单起见，直接起始块号用0填充
    dl_upg_pkt['body']['upg_id']         = apl_cco_upg_id

    plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

    tb_inst.mac_head.org_dst_tei         = sta_tei  # DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 # downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    return True

# 发送'执行升级'下行报文
def apl_upg_exec_send(tb_inst, sta_tei=0):
    global apl_cco_upg_id
    global apl_upg_time_to_rst          # '等待复位时间' 单位: 秒
    global apl_upg_try_running_time     # '试运行时间' 单位: 秒

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_upgrade_exec_dl.yaml')

    dl_upg_pkt['body']['time_2_rst']        = apl_upg_time_to_rst
    dl_upg_pkt['body']['upg_id']            = apl_cco_upg_id
    dl_upg_pkt['body']['try_running_time']  = apl_upg_try_running_time

    plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

    tb_inst.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    return True

# 发送'查询站点信息'下行报文
def apl_upg_sta_info_query_send(tb_inst, sta_tei=0, out_order_flag = 0):
    global apl_cco_upg_id
    global apl_upg_dev_info_type_num
    global apl_upg_dev_info_bmp
    global apl_upg_dev_info

    # dev_info_type_list = ['UPG_DEV_TYPE', 'UPG_FILE_SIZE', 'UPG_CRC32', 'UPG_BOOT_INFO', 'UPG_VERSION_INFO', 'UPG_VENDOR_ID']

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    dl_upg_pkt = tb_inst._load_data_file(data_file='apl_state_info_query_dl_blank.yaml')

    dl_upg_pkt['body']['info_num']       = apl_upg_dev_info_type_num
    dl_upg_info = dl_upg_pkt['body']['info_list']

    apl_upg_dev_info_bmp = 0

    for i in range(apl_upg_dev_info_type_num):
        if out_order_flag == 1:
            dev_type = random.randint(0, apl_upg_dev_info_type_num - 1)
        else:
            dev_type = i

        dl_upg_info.append(apl_upg_dev_info[dev_type]['type'])

        # record the info item, for later ACK pkt validation check;
        apl_upg_dev_info_bmp |= 1 << dev_type

    plc_tb_ctrl._debug(dl_upg_pkt)
    msdu = plc_packet_helper.build_apm(dict_content=dl_upg_pkt, is_dl=True)

    tb_inst.mac_head.org_dst_tei         = sta_tei  #DUT tei is 2, here, we need DUT to relay the packet
    tb_inst.mac_head.org_src_tei         = 1
    tb_inst.mac_head.msdu_type           = "PLC_MSDU_TYPE_APP"
    tb_inst.mac_head.tx_type             = 'PLC_MAC_UNICAST'
    tb_inst.mac_head.mac_addr_flag       = 0
    tb_inst.mac_head.hop_limit           = 15
    tb_inst.mac_head.remaining_hop_count = 15
    tb_inst.mac_head.broadcast_dir       = 1 #downlink broadcast

    tb_inst._send_msdu(msdu=msdu, mac_head=tb_inst.mac_head, src_tei=1, dst_tei=sta_tei, broadcast_flag = 0)

    return True

########################################################################
#   模拟CCO解析来自STA发送APL升级应答/转发报文的解析

# '开始升级'应答报文解析
def apl_upg_start_ack_parse(tb_inst, apm):
    global apl_cco_upg_id

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 检查'开始升级结果码'
    assert apm.body.ul.upg_start_result      == 0,                 'apl body upg start result not 0 err'
    # 检查'升级ID'
    assert apm.body.ul.upg_id                == apl_cco_upg_id,    'apl body upg id err'

    return True

# '查询站点升级状态'应答报文解析
def apl_upg_state_query_ack_parse(tb_inst, apm):
    global apl_cco_upg_id
    global apl_upg_blk_num
    global apl_upg_sent_blk_num
    global apl_upg_bitmap

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 检查'升级ID'
    assert apm.body.ul.upg_id            == apl_cco_upg_id,        'apl body upg id err'

    # 升级状态无需检查，接收时已经解析过了
    # assert apm.body.ul.upg_st          ==,     'upg state err'

    # 起始块号检查
    start_blk_id = apm.body.ul.start_blk_id

    if apl_upg_sent_blk_num == 0:     # 已发送块数为0的话，则不做bitmap检查
        assert start_blk_id               == 0,   'apl body start block id err'
        return True

    assert   start_blk_id                  < apl_upg_blk_num,      'apl body start block id err'

    # 有效块数检查
    valid_blk_num = apm.body.ul.valid_data_blk
    assert (valid_blk_num + start_blk_id) <= apl_upg_blk_num,      'apl body valid data block err'

    # bitmap 处理

    plc_tb_ctrl._debug("apl_upg_state_query_ack_parse - apl_upg_sent_blk_num={}, start_blk_id={}, valid_blk_num={}".format(apl_upg_sent_blk_num, start_blk_id, valid_blk_num))

    blk_bmp_size = (apl_upg_sent_blk_num + 7) >> 3
    bit_map = apm.body.ul.bit_map

    # 当前起始块号都用0填充，此处简单处理
    plc_tb_ctrl._debug("state_query_ack_parse - expected bitmap={}".format(apl_upg_bitmap[:blk_bmp_size]))
    plc_tb_ctrl._debug("state_query_ack_parse - received bitmap={}".format(bit_map))
    assert 0 == cmp(bit_map, apl_upg_bitmap[:blk_bmp_size]),       'apl body bitmap err'

    return True

# '查询站点信息'应答报文解析
def apl_upg_sta_info_query_ack_parse(tb_inst, apm):
    global apl_cco_upg_id
    global apl_upg_dev_info_type_num
    global apl_upg_dev_info_bmp
    global apl_upg_dev_info

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    # 检查'升级ID'
    if apm.body.ul.upg_id != 0:
        assert apm.body.ul.upg_id  == apl_cco_upg_id,               'apl body upg id err'

    # 检查信息元素列表元素个数
    info_num = apm.body.ul.info_num
    assert info_num                <= apl_upg_dev_info_type_num,    'apl body info num err'

    # 检查信息元素
    info_list    = apm.body.ul.info_list
    info_type    = 0
    dev_info_bmp = 0

    for i in range(4):
        # clear file crc,  will record the value in ack
        apl_upg_dev_info[3]['value'][i] = 0
        # clear file size, will record the value in ack
        apl_upg_dev_info[4]['value'][i] = 0

    for i in range(info_num):

        err_str = 'apl body info list dev type {} - dev length err'.format(info_list[i].type)

        if   info_list[i].type == 'UPG_VENDOR_ID':
            info_type = 0
            assert info_list[i].length == 2,                     err_str

        elif info_list[i].type == 'UPG_VERSION_INFO':
            info_type = 1
            assert info_list[i].length == 2,                     err_str

        elif info_list[i].type == 'UPG_BOOT_INFO':
            info_type = 2
            assert info_list[i].length == 1,                     err_str

        elif info_list[i].type == 'UPG_CRC32':
            info_type = 3
            assert info_list[i].length == 4,                     err_str

            for j in range(info_list[i].length):
                # record the value from ack pkt
                apl_upg_dev_info[info_type]['value'][j] = info_list[i].value[j]

        elif info_list[i].type == 'UPG_FILE_SIZE':
            info_type = 4
            assert info_list[i].length == 4,                     err_str

            for j in range(info_list[i].length):
                # record the value from ack pkt
                apl_upg_dev_info[info_type]['value'][j] = info_list[i].value[j]

        elif info_list[i].type == 'UPG_DEV_TYPE':
            info_type = 5
            assert info_list[i].length == 1,                     err_str

        else:
            assert False,        'apl body info list dev type err'

        dev_info_bmp |= (1 << info_type)

    assert apl_upg_dev_info_bmp == dev_info_bmp,      'apl body dev type list not match err'

    return True

########################################################
# APL 模拟CCO - 升级报文交互的入口相关控制函数

class ge_param_st:
    def __init__(self):
        self.tb_inst = None     # tb instance
        self.sta_tei = 0        # STA Tei
        self.cco_mac = None     # CCO MAC
        self.sta_mac = None     # STA MAC

class sp_param_st:
    def __init__(self):
        self.upg_id         = None
        self.pkt_id         = None
        self.blk_id         = 0
        self.sent_blk_num   = None
        self.out_order_flag = 0

# 模拟CCO 发送下行APL升级报文的及对相关应答的接收和解析(单次交互)
# def apl_upg_cco_single_tx_rx(tb_inst, sta_tei = 0, pkt_id=None, blk_id = 0, sent_blk_num = None, out_order_flag=0, cco_mac=None, sta_mac=None):
def apl_upg_cco_single_tx_rx(ge_param = None, sp_param = None):
    global msdu_sn
    global upg_pkt_interval
    global upg_pkt_rx_timeout

    assert isinstance(ge_param, ge_param_st), "ge_param type is not ge_param_st"
    assert isinstance(sp_param, sp_param_st), "sp_param type is not sp_param_st"

    tb_inst = ge_param.tb_inst
    sta_tei = ge_param.sta_tei
    cco_mac = ge_param.cco_mac
    sta_mac = ge_param.sta_mac

    upg_id  = sp_param.upg_id
    pkt_id  = sp_param.pkt_id
    blk_id  = sp_param.blk_id

    sent_blk_num   = sp_param.sent_blk_num
    out_order_flag = sp_param.out_order_flag

    assert isinstance(tb_inst, plc_tb_ctrl.PlcSystemTestbench),"tb_inst type is not plc_tb_ctrl.PlcSystemTestbench"

    wait_ack    = False

    bc_mac_addr = 'FF-FF-FF-FF-FF-FF'
    dst_mac     = cco_mac.upper()
    src_mac     = sta_mac.upper()
    uc2bc_body  = None

    # 先清空一遍缓存
    tb_inst.tb_uart.clear_tb_port_rx_buf()

    # 发送指定报文
    if  pkt_id == 'APL_UPGRADE_START':        # '开始升级'下行报文的发送 (需应答)
        apl_upg_start_send(tb_inst, sta_tei)
        wait_ack = True

    elif pkt_id == 'APL_UPGRADE_STOP':         # '停止升级'下行报文的发送
        apl_upg_stop_send(tb_inst, sta_tei, upg_id)

    elif pkt_id == 'APL_DATA_TRANSFER':        # '传输文件数据'下行报文的发送
        apl_upg_file_tx_send(tb_inst, sta_tei, blk_id, uc2bc_flag=0)

    elif pkt_id == 'APL_DATA_TRANSFER_BC':     # '传输文件数据（单播转本地广播）'下行报文的发送
        uc2bc_body = apl_upg_file_tx_send(tb_inst, sta_tei, blk_id, uc2bc_flag=1)
        dst_mac    = bc_mac_addr
        pkt_id     = 'APL_DATA_TRANSFER'
        wait_ack   = True

    elif pkt_id == 'APL_UPGRADE_STATE_QUERY':  # '查询站点升级状态'下行报文发送 (需应答)
        apl_upg_state_query_send(tb_inst, sta_tei, sent_blk_num)
        wait_ack = True

    elif pkt_id == 'APL_UPGRADE_EXEC':         # '执行升级'下行报文的发送
        apl_upg_exec_send(tb_inst, sta_tei)

    elif pkt_id == 'APL_STATE_INFO_QUERY':     # '查询站点信息'下行报文的发送 (需应答)
        apl_upg_sta_info_query_send(tb_inst, sta_tei, out_order_flag)
        wait_ack = True

    else:
        assert False, "pkt header packet id err"      # 报文ID 错误

    #tc_common.wait_for_tx_complete_ind(tb_inst)

    time.sleep(upg_pkt_interval)

    # 处理相关应答
    if wait_ack is False:
        return

    time_stop = time.time() + 10*config.CLOCK_RATE
    while True:
        if time_stop <= time.time():
            break

#        if pkt_id == 'APL_DATA_TRANSFER':         # '传输文件数据'单播转本地广播的转发后的报文还是下行报文
#            [timestamp, fc, mac_frame_head, apm] = tb_inst._wait_for_plc_apm_dl(pkt_id, 10)
#        else:
#            [timestamp, fc, mac_frame_head, apm] = tb_inst._wait_for_plc_apm_ul(pkt_id, 10)

        [fc, mac_frame_head, apm] = tb_inst._wait_for_plc_apm(pkt_id, 10)

    #    plc_tb_ctrl._debug("mac_frame_head = {}".format(mac_frame_head))

        if mac_frame_head is None:
            continue

        rx_msdu_sn = mac_frame_head.msdu_sn
        if rx_msdu_sn == msdu_sn :
            plc_tb_ctrl._debug("apl_upg_cco_single_tx_rx: duplicated pkt, drop")
            continue
        msdu_sn = rx_msdu_sn
        if apm.header.id  == pkt_id:
            break

    assert mac_frame_head is not None,             "mac frame head is none err"
    assert apm is not None,                        "APL packet is not received err"

    if mac_frame_head.mac_addr_flag == 1:
        ack_dst_mac = mac_frame_head.dst_mac_addr.upper()
        ack_src_mac = mac_frame_head.src_mac_addr.upper()

        assert ack_dst_mac                == dst_mac,       "mac frame head dst mac err"
        assert ack_src_mac                == src_mac,       "mac frame head src mac err"
    else:
        assert mac_frame_head.org_src_tei == sta_tei,       "mac frame head src tei err"
        assert (mac_frame_head.org_dst_tei == 1) or (mac_frame_head.org_dst_tei == 0xFFF), "mac frame head dst tei err"

    # 报文控制字是否为0
    assert apm.header.ctrl_word           == 0,             "pkt header ctrl word err"
    # 报文端口号是否为0x12, 升级业务
    assert apm.header.port                == 0x12,          "pkt header port id err"
    # 应答报文的报文ID是否下发报文的报文ID
    assert apm.header.id                  == pkt_id,        "pkt header id err"
    # 协议版本号是否为1
    if pkt_id == 'APL_DATA_TRANSFER':         # '传输文件数据'单播转本地广播的转发后的报文还是下行报文
        assert apm.body.dl.proto_ver      == 'PROTO_VER1',  "pkt body proto ver err"
    else:
        assert apm.body.ul.proto_ver      == 'PROTO_VER1',  "pkt body proto ver err"

    if   pkt_id == 'APL_UPGRADE_START':         # '开始升级'上行报文解析
        apl_upg_start_ack_parse(tb_inst, apm)

    elif pkt_id == 'APL_UPGRADE_STATE_QUERY':   # '查询站点升级状态'上行报文解析
        apl_upg_state_query_ack_parse(tb_inst, apm)

    elif pkt_id == 'APL_STATE_INFO_QUERY':      # '查询站点信息'上行报文解析
        apl_upg_sta_info_query_ack_parse(tb_inst, apm)

    elif pkt_id == 'APL_DATA_TRANSFER':         # '传输文件数据'单播转本地广播的结果检查
        assert uc2bc_body['upg_id']        == apm.body.dl.upg_id,         "pkt body upg id err"
        assert uc2bc_body['data_blk_size'] == apm.body.dl.data_blk_size,  "pkt body data blk size err"
        assert uc2bc_body['data_blk_id']   == apm.body.dl.data_blk_id,    "pkt body upg id err"
        assert cmp(uc2bc_body['data'], apm.body.dl.data) == 0,            "pkt body upg id err"
        plc_tb_ctrl._debug("apl_upg_cco_single_tx_rx: UC to BC check ok")

    else:
        assert False, "pkt header packet id err"      # 报文ID 错误

    return pkt_id
