# -- coding: utf-8 --

import config

MAC_MPDU_LONG_GI = 458
MAC_MPDU_SHORT_GI = 264
MAC_MPDU_IFFT_LEN = 1024

MAC_BPSK = 1
MAC_QPSK = 2
MAC_16QAM = 4

MAC_CODE_RATE_1_2 = 0
MAC_CODE_RATE_16_18 = 1

MAX_TMI_BASIC = 14
MAX_TMI_EXT = 14

MAC_MPDU_BEACON = 0
MAC_MPDU_SOF = 1
MAC_MPDU_SACK = 2
MAC_MPDU_NCF = 3
MAC_MPDU_DM = 7

# NTB frequency, MHz
if config.DEVICE == 'STM32F103ZE':
    NTB_FREQ = 24
else:
    NTB_FREQ = 25

MAX_NTB = 0xFFFFFFFF
HALF_MAX_NTB = (MAX_NTB + 1) / 2

WORK_BAND0 = 0
WORK_BAND1 = 1
WORK_BAND2 = 2
WORK_BAND3 = 3
WORK_BAND_NUM = 4

TONEMASK0 = 0
TONEMASK1 = 1
TONEMASK2 = 2
TONEMASK3 = 3
TONEMASK_NUM = 4
TONEMASK_INVALID = 0xFF


from formats import *
import binary_helper
import binascii
import plc_tb_ctrl
import crcmod


def ms_to_ntb(ms):
    return ms * NTB_FREQ * 1000

def us_to_ntb(us):
    return us * NTB_FREQ

def ntb_to_ms(ntb):
    return ntb / (NTB_FREQ * 1000)

def ntb_to_us(ntb):
    return ntb / NTB_FREQ


def ntb_diff(early, late):
    diff = late - early
    if (diff >= HALF_MAX_NTB):
        diff = diff - MAX_NTB - 1
    elif (diff <= -HALF_MAX_NTB):
        diff = MAX_NTB + 1 + diff

    return diff

def ntb_add(value, delta):
    return (value + delta) & MAX_NTB


# True: value >= low_bound and value < high_bound
def ntb_inside_range(value, low_bound, high_bound):
    if ((ntb_diff(low_bound, value) >= 0)
           and (ntb_diff(value, high_bound) > 0)):
        return True
    else:
        return False


MAC_RIFS = us_to_ntb(1000)
MAC_CIFS = us_to_ntb(400)

MAC_PREAMBLE_DURATION = 13312

mac_tmi_basic_mode_tbl = [
    dict(
        mode = 0,
        div_num = 4,
        pb_size = 520,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 1,
        div_num = 2,
        pb_size = 520,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 2,
        div_num = 5,
        pb_size = 136,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 10
    ),
    dict(
        mode = 3,
        div_num = 11,
        pb_size = 136,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 11
    ),
    dict(
        mode = 4,
        div_num = 7,
        pb_size = 136,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 5,
        div_num = 11,
        pb_size = 136,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 11
    ),
    dict(
        mode = 6,
        div_num = 7,
        pb_size = 136,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 7,
        div_num = 7,
        pb_size = 520,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 3,
        inter_num = 14
    ),
    dict(
        mode = 8,
        div_num = 4,
        pb_size = 520,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 9,
        div_num = 7,
        pb_size = 520,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 10,
        div_num = 2,
        pb_size = 520,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 11,
        div_num = 7,
        pb_size = 264,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 12,
        div_num = 7,
        pb_size = 264,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 13,
        div_num = 7,
        pb_size = 72,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    ),
    dict(
        mode = 14,
        div_num = 7,
        pb_size = 72,
        modulation_type = MAC_BPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 14
    )
]

mac_tmi_ext_mode_tbl = [
    dict( #0
        mode = MAX_TMI_EXT + 1,
        div_num = 1,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_16_18,
        max_pb_num = 4,
        inter_num = 1
    ),
    dict(
        mode = 1,
        div_num = 1,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_16_18,
        max_pb_num = 4,
        inter_num = 1
    ),
    dict(
        mode = 2,
        div_num = 2,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_16_18,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 3,
        div_num = 1,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 1
    ),
    dict(
        mode = 4,
        div_num = 2,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 5,
        div_num = 4,
        pb_size = 520,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 6,
        div_num = 1,
        pb_size = 520,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 1
    ),
    dict( #7
        mode = MAX_TMI_EXT + 1,
        div_num = 5,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 10
    ),
    dict( #8
        mode = MAX_TMI_EXT + 1,
        div_num = 5,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 10
    ),
    dict( #9
        mode = MAX_TMI_EXT + 1,
        div_num = 5,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 10
    ),
    dict(
        mode = 10,
        div_num = 5,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 10
    ),
    dict(
        mode = 11,
        div_num = 2,
        pb_size = 136,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 12,
        div_num = 2,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 8
    ),
    dict(
        mode = 13,
        div_num = 1,
        pb_size = 136,
        modulation_type = MAC_QPSK,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 1
    ),
    dict(
        mode = 14,
        div_num = 1,
        pb_size = 136,
        modulation_type = MAC_16QAM,
        code_rate = MAC_CODE_RATE_1_2,
        max_pb_num = 4,
        inter_num = 1
    )
]

def build_pb_crc(crc):
    return plc_mpdu.plc_pb_crc.build(crc)

def build_nmm(dict_content = None, data_str = None, data_file = None):
    return binary_helper.build(plc_nmm.plc_nmm.build, "fail to build plc nmm", dict_content, data_file, data_str)

def parse_nmm(raw_data):
    return plc_nmm.plc_nmm.parse(raw_data)

def build_apm(dict_content = None, data_str = None, data_file = None, is_dl=True):
    if is_dl:
        return binary_helper.build(plc_apl.plc_apl_dl.build, "fail to build plc apl dl message", dict_content, data_file, data_str)
    else:
        return binary_helper.build(plc_apl.plc_apl_ul.build, "fail to build plc apl ul message", dict_content, data_file, data_str)

def parse_apm(raw_data, is_dl=True):
    if (is_dl):
        return plc_apl.plc_apl_dl.parse(raw_data)
    else:
        return plc_apl.plc_apl_ul.parse(raw_data)

def build_mac_frame_head(dict_content = None, data_str = None, data_file = None):
    return binary_helper.build(plc_mac_frame.plc_mac_frame_head.build, "fail to build plc mac frame head", dict_content, data_file, data_str)

def build_mac_frame_crc(crc):
    return plc_mac_frame.plc_mac_frame_crc.build(crc)

def build_mac_frame(msdu):
    pass

def build_beacon_payload(dict_content = None, data_str = None, data_file = None):
    return binary_helper.build(plc_beacon.plc_beacon.build, "fail to build beacon payload", dict_content, data_file, data_str)

def build_mpdu_fc(dict_content = None, data_str = None, data_file = None):
    return binary_helper.build(plc_mpdu.plc_mpdu_fc.build, "fail to build MPDU FC", dict_content, data_file, data_str)

def parse_mpdu_fc(raw_data):
    return binary_helper.parse(plc_mpdu.plc_mpdu_fc.parse, "fail to parse MPDU FC", raw_data)

def parse_mac_frame(raw_data):
    return binary_helper.parse(plc_mac_frame.plc_mac_frame.parse, "fail to parse MAC Frame", raw_data)

def parse_beadcon_payload(raw_data):
    return binary_helper.parse(plc_beacon.plc_beacon.parse, "fail to parse Beacon payload", raw_data)

def get_beacon_payload(pb_num, pb_size, pl_data):
    beacon_payload = None
    end_pos = pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_beacon.PLC_BEACON_CRC_SIZE
    raw_data = pl_data[0:end_pos]
    carried_crc = plc_beacon.plc_beacon_crc.parse(pl_data[end_pos:(end_pos+plc_beacon.PLC_BEACON_CRC_SIZE)])
    crc = calc_crc32(raw_data)
    if crc == carried_crc:
        beacon_payload = parse_beadcon_payload(raw_data)
        #plc_tb_ctrl._trace_beacon_dl(raw_data)

    return beacon_payload



def reassemble_mac_frame(pb_num, pb_size, pl_data):
    raw_data = ''
    for i in range(pb_num):
        start_pos = i * pb_size + plc_mpdu.PLC_SOF_PB_HEAD_SIZE
        end_pos = start_pos + pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_mpdu.PLC_SOF_PB_HEAD_SIZE
        raw_data += pl_data[start_pos:end_pos]

    mac_frame = parse_mac_frame(raw_data)

    #if mac_frame is not None:
    #    plc_tb_ctrl._trace_mac_frame_dl(raw_data)

    return mac_frame

def check_mac_frame(pb_num, pb_size, pl_data):
    raw_data = ''
    for i in range(pb_num):
        start_pos = i * pb_size + plc_mpdu.PLC_SOF_PB_HEAD_SIZE
        end_pos = start_pos + pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_mpdu.PLC_SOF_PB_HEAD_SIZE
        raw_data += pl_data[start_pos:end_pos]

    mac_frame = parse_mac_frame(raw_data)

    if mac_frame is None:
        raw_data = None

    return raw_data

def check_mac_frame_crc(mac_frame):
    msdu_len = mac_frame.head.msdu_len
    crc = calc_crc32(mac_frame.msdu.data[0:msdu_len])
    if (crc == mac_frame.crc):
        return True
    else:
        return False

# mac_frame: raw data
def construct_sof(pb_num, pb_size, mac_frame):
    pbb_size = pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_mpdu.PLC_SOF_PB_HEAD_SIZE
    fc_pl_data = ''
    for i in range(pb_num):
        if 0 == i:
            start_flag = 1
        else:
            start_flag = 0

        if i == (pb_num - 1):
            end_flag = 1
        else:
            end_flag = 0

        start_pos = i * pbb_size
        end_pos = start_pos + pbb_size
        pb_body = mac_frame[start_pos:end_pos]
        # fill rest part by \x00
        pb_body = pb_body + ('\x00' * (pbb_size - len(pb_body)))
        head = plc_mpdu.plc_sof_pb_head.build(dict(sn=i,start_flag=start_flag,end_flag=end_flag))
        pb_crc = calc_crc24(head + pb_body)
        fc_pl_data = fc_pl_data + head + pb_body + build_pb_crc(pb_crc)

    return fc_pl_data

def calc_sof_pbb_size(pb_size):
    return pb_size - plc_mpdu.PLC_PB_CRC_SIZE - plc_mpdu.PLC_SOF_PB_HEAD_SIZE

'''
生成SOF帧载荷字节流
'''
def gen_sof_pb(pb_size, pb_num):
    if 520 == pb_size:
        generator = plc_mpdu.plc_sof_pb520.build
    elif 264 == pb_size:
        generator = plc_mpdu.plc_sof_pb264.build
    elif 136 == pb_size:
        generator = plc_mpdu.plc_sof_pb136.build
    elif 72 == pb_size:
        generator = plc_mpdu.plc_sof_pb72.build
    else:
        AssertionError("Wrong pb_size {}".format(pb_size))

    pbb_size = calc_sof_pbb_size(pb_size)
    sof_payload = ''
    for i in range(pb_num):
        payload = [(j+i)&0xFF for j in range(pbb_size)]
        head = dict(sn=i)
        if 0 == i:
            head['start_flag'] = 1
        else:
            head['start_flag'] = 0

        if pb_num == (i + 1):
            head['end_flag'] = 1
        else:
            head['end_flag'] = 0

        pb = generator(dict(head=head, payload=payload, crc=0))
        crc = calc_crc24(pb[0:(pb_size - plc_mpdu.PLC_PB_CRC_SIZE)])
        sof_payload += generator(dict(head=head, payload=payload, crc=crc))
    return sof_payload

'''
生成SOF帧载荷字节流
'''
def build_sof_one_pb(mac_frame, pb_size, pb_sn, total_pb_num):
    if 520 == pb_size:
        generator = plc_mpdu.plc_sof_pb520.build
    elif 264 == pb_size:
        generator = plc_mpdu.plc_sof_pb264.build
    elif 136 == pb_size:
        generator = plc_mpdu.plc_sof_pb136.build
    elif 72 == pb_size:
        generator = plc_mpdu.plc_sof_pb72.build
    else:
        AssertionError("Wrong pb_size {}".format(pb_size))

    pbb_size = calc_sof_pbb_size(pb_size)
    payload = mac_frame[pb_sn*pbb_size:(pb_sn+1)*pbb_size]
    valid_data_size = len(payload)
    # 不足的部分补零
    payload = [ord(c) for c in payload] + [0] * (pbb_size - valid_data_size)
    head = dict(sn=pb_sn)
    if 0 == pb_sn:
        head['start_flag'] = 1
    else:
        head['start_flag'] = 0

    if total_pb_num == (pb_sn + 1):
        head['end_flag'] = 1
    else:
        head['end_flag'] = 0

    sof_pb = generator(dict(head=head, payload=payload, crc=0))
    crc = calc_crc24(sof_pb[0:(pb_size - plc_mpdu.PLC_PB_CRC_SIZE)])
    sof_pb = generator(dict(head=head, payload=payload, crc=crc))

    return sof_pb


def calc_crc32(data):
    crc = binascii.crc32(data)
    crc = crc & 0xFFFFFFFF
    return crc

def calc_crc24(data):
    crc24_func = crcmod.mkCrcFun(0x1800063, initCrc=0)
    crc = crc24_func(data)
    return crc

def init_tonemask_param(work_band, tonemask):
    if WORK_BAND0 == work_band:
        fc_sym_num = 4
    elif ((WORK_BAND1 == work_band)
            or (WORK_BAND2 == work_band)
            or (WORK_BAND3 == work_band)):
        fc_sym_num = 12
    else:
        raise AssertionError('invalid work band {}'.format(work_band))

    if (TONEMASK_NUM <= tonemask):
        if WORK_BAND0 == work_band:
            valid_carr_num = 411
        elif WORK_BAND1 == work_band:
            valid_carr_num = 131
        elif WORK_BAND2 == work_band:
            valid_carr_num = 89
        elif WORK_BAND3 == work_band:
            valid_carr_num = 49
        else:
            raise AssertionError('invalid work band {}'.format(work_band))
    else:
        if TONEMASK0 == work_band:
            valid_carr_num = 371
        elif TONEMASK1 == work_band:
            valid_carr_num = 126
        elif TONEMASK2 == work_band:
            valid_carr_num = 84
        elif TONEMASK3 == work_band:
            valid_carr_num = 45
        else:
            raise AssertionError('invalid tonemask {}'.format(tonemask))

    param = PlcTonemaskParam(work_band, tonemask, valid_carr_num, fc_sym_num)

    return param

def calc_pb_format(tonemask_param, mpdu_type, data_size):
    assert isinstance(tonemask_param, PlcTonemaskParam)

    pb_format = {}
    if MAC_MPDU_BEACON == mpdu_type:
        if ((data_size + plc_mpdu.PLC_PB_CRC_SIZE) > 136):
            # pbsize=520
            pb_size = 520
            pb_format['tmi_basic_mode'] = 9
            pb_format['tmi_ext_mode'] = 0
        else:
            # pbsize=136
            pb_size = 136
            pb_format['tmi_basic_mode'] = 4
            pb_format['tmi_ext_mode'] = 0

        pb_format['pb_num'] = 1

    elif MAC_MPDU_SOF == mpdu_type:
        total_size = data_size + plc_mpdu.PLC_SOF_PB_HEAD_SIZE + plc_mpdu.PLC_PB_CRC_SIZE
        if (total_size > 264):
            # 一个520块相比2个264块填充比特更少
            pb_size = 520
            pb_format['tmi_basic_mode'] = 9
            pb_format['tmi_ext_mode'] = 0
        elif ((total_size <= 264) and (total_size > 136)):
            pb_size = 264
            pb_format['tmi_basic_mode'] = 12
            pb_format['tmi_ext_mode'] = 0
        elif ((total_size <= 136) and (total_size > 72)):
            pb_size = 136
            pb_format['tmi_basic_mode'] = 4
            pb_format['tmi_ext_mode'] = 0
        elif (total_size <= 72):
            pb_size = 72
            pb_format['tmi_basic_mode'] = 14
            pb_format['tmi_ext_mode'] = 0
        else:
            raise AssertionError('invalid total_size {}'.format(total_size))

        pbb_size = pb_size - plc_mpdu.PLC_SOF_PB_HEAD_SIZE - plc_mpdu.PLC_PB_CRC_SIZE
        pb_format['pb_num'] = (data_size + pbb_size - 1) / pbb_size
    else:
        raise AssertionError('invalid MPDU type {}'.format(mpdu_type))

    pb_format['pb_size'] = pb_size
    pb_format['sym_num'] = tonemask_param.calc_payload_sym_num(pb_format['tmi_basic_mode'], pb_format['tmi_ext_mode'],
        pb_format['pb_num'])

    return pb_format

def calc_payload_duration_by_sym_num(sym_num):
    assert sym_num >= 2
    duration = ((MAC_MPDU_IFFT_LEN + MAC_MPDU_LONG_GI) << 1) + (sym_num - 2) * (MAC_MPDU_IFFT_LEN + MAC_MPDU_SHORT_GI)
    return duration


def query_pb_size_by_tmi(tmi_b, tmi_e):
    if (15 == tmi_b):
        assert mac_tmi_ext_mode_tbl[tmi_e]['mode'] <= MAX_TMI_EXT
        pb_size = mac_tmi_ext_mode_tbl[tmi_e]['pb_size']
    else:
        assert mac_tmi_basic_mode_tbl[tmi_b]['mode'] <= MAX_TMI_BASIC
        pb_size = mac_tmi_basic_mode_tbl[tmi_b]['pb_size']

    return pb_size

# 计算10us单位的帧长
def calc_frame_len(sym_num, ack_needed):
    payload_duration = calc_payload_duration_by_sym_num(sym_num)

    if ack_needed:
        frame_len = (payload_duration + MAC_RIFS
                     + MAC_PREAMBLE_DURATION
                     + plc_tb_ctrl.TB_INSTANCE.tonemask_param.fc_duration
                     + MAC_CIFS)
    else:
        frame_len = payload_duration + MAC_CIFS

    #plc_tb_ctrl._debug("pl_duration:{},{},{}".format(payload_duration, sym_num, frame_len))

    return ntb_to_us(frame_len) / 10

def calc_fc_len(work_band):
    if WORK_BAND0 == work_band:
        fc_sym_num = 4
    elif ((WORK_BAND1 == work_band)
          or (WORK_BAND2 == work_band)
          or (WORK_BAND3 == work_band)):
        fc_sym_num = 12
    fc_duration = fc_sym_num * (MAC_MPDU_IFFT_LEN + MAC_MPDU_LONG_GI)
    return fc_duration
def calc_frame_len_ntb(work_band, sym_num):
    payload_duration = calc_payload_duration_by_sym_num(sym_num)
    fc_duration = calc_fc_len(work_band)
    frame_len = MAC_PREAMBLE_DURATION +fc_duration + payload_duration
    return frame_len
def get_beacon_period(beacon_payload):
    beacon_info = beacon_payload.beacon_info
    for item in beacon_info.beacon_item_list:
        if item.head == 'SLOT_ALLOC':
            return item.beacon_item.beacon_period_len

def get_beacon_period_start_time(beacon_payload):
    beacon_info = beacon_payload.beacon_info
    for item in beacon_info.beacon_item_list:
        if item.head == 'SLOT_ALLOC':
            return item.beacon_item.beacon_period_start_time

def get_beacon_slot_alloc(beacon_payload):
    beacon_info = beacon_payload['beacon_info']
    for item in beacon_info['beacon_item_list']:
        if item['head'] == 'SLOT_ALLOC':
            return item['beacon_item']

def get_beacon_sta_capability(beacon_payload):
    beacon_info = beacon_payload['beacon_info']
    for item in beacon_info['beacon_item_list']:
        if item['head'] == 'STATION_CAPABILITY':
            return item['beacon_item']

def get_beacon_routing_parameters(beacon_payload):
    beacon_info = beacon_payload['beacon_info']
    for item in beacon_info['beacon_item_list']:
        if item['head'] == 'ROUTE_PARAM':
            return item['beacon_item']

def check_ntb(exp_ntb, real_ntb, low_bound, high_bound):
    diff = ntb_diff(exp_ntb, real_ntb)
    if (diff >= low_bound) and (diff < high_bound):
        return True
    else:
        return False

def cmp_phase_slot_config(x, y):
    result = cmp(x["slice_num"], y["slice_num"])
    if 0 == result:
        result = cmp(x["phase"], y["phase"])
    return result

'''
计算CSMA时隙分片信息
'''
def calc_csma_slot_config(beacon_payload):
    beacon_slot_alloc = get_beacon_slot_alloc(beacon_payload)
    csma_slot_infos = beacon_slot_alloc['csma_slot_info']
    beacon_slot_len = ms_to_ntb(beacon_slot_alloc['beacon_slot_len'])
    csma_slot_start_time = (beacon_slot_alloc['beacon_period_start_time']
                           + (beacon_slot_alloc['ncb_slot_num'] + beacon_slot_alloc['cb_slot_num']) * beacon_slot_len)
    csma_slot_start_time &= MAX_NTB

    # 计算CSMA时隙信息
    slice_len = ms_to_ntb(beacon_slot_alloc['csma_slot_slice_len'] * 10)
    csma_slot_config = dict(start_time=csma_slot_start_time,
                            slice_len=slice_len,
                            phase_slot_configs_list=[],
                            phase_slot_configs_dict={1: None, 2: None, 3: None})
    total_slice_num = 0
    for slot_info in csma_slot_infos:
        phase_slot_config = dict(phase=slot_info['phase'])
        slot_len = ms_to_ntb(slot_info['slot_len'])
        slice_num = slot_len / slice_len
        phase_slot_config['last_slice_len'] = slot_len % slice_len

        if phase_slot_config['last_slice_len'] > 0:
            if slice_num > 0:
                phase_slot_config['last_slice_len'] += slice_len
            else:
                slice_num += 1
        else:
            phase_slot_config['last_slice_len'] = slice_len

        phase_slot_config['slice_num'] = slice_num
        csma_slot_config['phase_slot_configs_list'].append(phase_slot_config)
        csma_slot_config['phase_slot_configs_dict'][slot_info['phase']] = phase_slot_config

        total_slice_num += slice_num

    # 按照slice_num和相线排序
    csma_slot_config['phase_slot_configs_list'].sort(cmp = cmp_phase_slot_config)

    # 构造slice_list
    csma_slot_config['total_slice_num'] = total_slice_num
    slice_list = [0xFF for i in range(total_slice_num)]
    start_index = 0
    for phase_slot_config in csma_slot_config['phase_slot_configs_list'][:-1]:
        slice_num = phase_slot_config['slice_num']
        if slice_num == 0:
            continue


        for i in range(slice_num):
            slice_index = start_index + i * total_slice_num / slice_num
            # 寻找空闲的分片，标记为被对应相线占用
            while ((slice_index < total_slice_num) and (0xFF != slice_list[slice_index])):
                slice_index += 1

            assert (slice_index < total_slice_num), "no vacant slice"

            slice_list[slice_index] = phase_slot_config['phase']

            if 0 == i:
                phase_slot_config['first_slice_index'] = slice_index

            if slice_num == (i + 1):
                phase_slot_config['last_slice_index'] = slice_index

        start_index += 1

    phase_slot_config = csma_slot_config['phase_slot_configs_list'][-1]

    last_phase_slice_num = 0
    for i in range(len(slice_list)):
        if (0xFF == slice_list[i]):
            slice_list[i] = phase_slot_config["phase"]

            last_phase_slice_num += 1
            if (1 == last_phase_slice_num):
                phase_slot_config['first_slice_index'] = i

            if (phase_slot_config["slice_num"] == last_phase_slice_num):
                phase_slot_config['last_slice_index'] = i

    assert last_phase_slice_num == phase_slot_config["slice_num"]

    csma_slot_config['slice_list'] = slice_list

    return csma_slot_config

'''
检查SOF的起始和结束时间是否落在指定相线的CSMA时隙中
beacon_payload为信标帧载荷
sof_rx_start_time: SOF帧的起始时间
sof_end_time: 以帧长计算的SOF帧的结束时间
phase: 相线, 1: phase_a, 2: phase_b, 3: phase_c
'''
def check_sof_time(sof_rx_start_time, sof_end_time, phase, beacon_payload):
    csma_slot_config = calc_csma_slot_config(beacon_payload)

    plc_tb_ctrl._debug("start time:{}, end_time:{}".format(sof_rx_start_time, sof_end_time))
    plc_tb_ctrl._debug(csma_slot_config)

    plc_tb_ctrl._debug("csma start time:{}".format(csma_slot_config['start_time']))

    # 检查SOF帧是否落在给定相线的CSMA时隙分片中
    slice_end_time = csma_slot_config['start_time']
    total_slice_num = csma_slot_config['total_slice_num']
    slice_list = csma_slot_config['slice_list']
    phase_slot_configs_dict = csma_slot_config['phase_slot_configs_dict']
    slice_index = 0
    correct_time = False
    check_end_time = False
    for slice_index in range(total_slice_num):
        slice_start_time = slice_end_time
        curr_slice = slice_list[slice_index]
        if curr_slice == 0xFF:
            continue

        if (slice_index + 1) < total_slice_num:
            next_slice = slice_list[slice_index + 1]

        phase_slot_config = phase_slot_configs_dict[curr_slice]
        if slice_index == phase_slot_config['last_slice_index']:
            slice_len = phase_slot_config['last_slice_len']
        else:
            slice_len = csma_slot_config['slice_len']

        slice_end_time = ntb_add(slice_start_time, slice_len)

        if curr_slice == phase:
            if not check_end_time:
                # 检查开始时间
                if not ntb_inside_range(sof_rx_start_time, slice_start_time, slice_end_time):
                    continue

            if ntb_inside_range(sof_end_time, slice_start_time, slice_end_time):
                correct_time = True
                break

    return correct_time

def map_phase_str_to_value(phase_str):
    if "PHASE_A" == phase_str:
        value = 1
    elif "PHASE_B" == phase_str:
        value = 2
    elif "PHASE_C" == phase_str:
        value = 3
    else:
        plc_tb_ctrl._debug('invalid phase ' + phase_str)
        value = 1

    return value

def calc_max_msdu_len(pb_size, pb_num, short_mac_head=True):
    if short_mac_head:
        mac_head_len = plc_mac_frame.PLC_SHORT_MAC_HEAD_SIZE
    else:
        mac_head_len = plc_mac_frame.PLC_LONG_MAC_HEAD_SIZE

    max_msdu_len = (calc_sof_pbb_size(pb_size) * pb_num - mac_head_len
                    - plc_mac_frame.PLC_MAC_FRAME_CRC_SIZE)
    return max_msdu_len

class PlcTonemaskParam(object):
    def __init__(self, work_band, tonemask, valid_carr_num, fc_sym_num):
        self.work_band = work_band
        self.tonemask = tonemask
        self.valid_carr_num = valid_carr_num
        self.fc_duration = fc_sym_num * (MAC_MPDU_IFFT_LEN + MAC_MPDU_LONG_GI)
        self.tmi_b_para = []
        self.tmi_e_para = []
        self._calc_tmi_static_para(mac_tmi_basic_mode_tbl, MAX_TMI_BASIC,  self.tmi_b_para)
        self._calc_tmi_static_para(mac_tmi_ext_mode_tbl, MAX_TMI_EXT, self.tmi_e_para)

    def calc_payload_sym_num(self, tmi_b, tmi_e, pb_num):
        if tmi_b <= MAX_TMI_BASIC:
            tmi = tmi_b
            tmi_para = self.tmi_b_para[tmi]
        else:
            tmi = tmi_e
            assert tmi <= MAX_TMI_EXT
            tmi_para = self.tmi_e_para[tmi]

        sym_num = tmi_para['sym_num_per_pb'] * pb_num
        return sym_num

    def _calc_tmi_static_para(self, tmi_table, max_tmi, tmi_para_tbl):
        tmi_para_tbl[:] = []
        for tmi in tmi_table:
            tmi_para = dict(valid=False, used_carr_num=0, data_bits_len=0, carr_num_per_inter=0,
                pad_bits_num=0, bits_per_group=0, sym_num_per_pb=0, sample_num_per_pb=0)
            tmi_para_tbl.append(tmi_para)
            if tmi['mode'] > max_tmi:
                continue

            tmi_para['valid'] = True
            tmi_para['used_carr_num'] = self.valid_carr_num / tmi['inter_num'] * tmi['inter_num']

            # calc data_bits_len
            data_bits_len = tmi['pb_size'] * 8
            if MAC_CODE_RATE_1_2 == tmi['code_rate']:
                data_bits_len *= 2
            elif MAC_CODE_RATE_16_18 == tmi['code_rate']:
                data_bits_len = data_bits_len * 18 / 16
            else:
                raise AssertionError('invalid code rate')
            tmi_para['data_bits_len'] = data_bits_len


            # calc pad_bits_num and bits_per_group
            carr_num_per_group = tmi_para['used_carr_num'] / tmi['div_num']
            carr_num_per_inter = self.valid_carr_num / tmi['inter_num']
            tmi_para['carr_num_per_inter'] = carr_num_per_inter

            bits_per_group = tmi['modulation_type'] * carr_num_per_group
            bits_per_symbol = tmi['modulation_type'] * tmi_para['used_carr_num']
            bits_in_last_symbol = data_bits_len - (data_bits_len / bits_per_symbol * bits_per_symbol)
            if (0 == bits_in_last_symbol):
                bits_in_last_symbol = bits_per_symbol
                bits_in_last_group = bits_per_group
            else:
                bits_in_last_group = bits_in_last_symbol - ((bits_in_last_symbol - 1) / bits_per_group * bits_per_group)

            assert bits_per_group >= bits_in_last_group
            tmi_para['pad_bits_num'] = bits_per_group - bits_in_last_group
            tmi_para['bits_per_group'] = bits_per_group

            # calculate sym_num_per_pb
            total_bits_num = (data_bits_len + tmi_para['pad_bits_num']) * tmi['div_num']
            total_carr_num = total_bits_num / tmi['modulation_type']
            tmi_para['sym_num_per_pb'] = (total_carr_num + tmi_para['used_carr_num'] - 1) / tmi_para['used_carr_num']
            tmi_para['sample_num_per_pb'] = calc_payload_duration_by_sym_num(tmi_para['sym_num_per_pb'])


if __name__ == '__main__':
    pass
