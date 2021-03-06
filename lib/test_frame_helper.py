from formats import *
from construct import *


def build_activate_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "ACTIVATE_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.activate_req.build, "fail to build activate req", dict_content, data_file, data_str)
    return result

def parse_activate_req(d):
    return plc_test_frame.activate_req.parse(d)


def build_evt_trig_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "EVT_TRIG_REQ_CMD")
    result['body'] = ''
    return result


def build_deactivate_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "DEACTIVATE_REQ_CMD")
    result['body'] = ''
    return result

def build_sta_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "STA_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.sta_config_req.build, "fail to build sta config req", dict_content, data_file, data_str)
    return result

def build_freq_offset_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "FREQ_OFFSET_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.freq_offset_config_req.build, "fail to build freq offset config req", dict_content, data_file, data_str)
    return result

def parse_sta_config_req(d):
    return plc_test_frame.sta_config_req.parse(d)

def build_fc_pl_data(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "FC_PL_DATA")
    result['body'] = binary_helper.build(plc_test_frame.fc_pl_data.build, "fail to build fc pl data", dict_content, data_file, data_str)
    return result

def build_periodic_fc_pl_data(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "PERIODIC_FC_PL_DATA")
    result['body'] = binary_helper.build(plc_test_frame.periodic_fc_pl_data.build,
                                         "fail to build periodic fc pl data",
                                         dict_content, data_file, data_str)
    return result

def build_pl_data(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "PL_DATA")
    result['body'] = binary_helper.build(plc_test_frame.pl_data.build, "fail to build pl data", dict_content, data_file, data_str)
    return result

def build_beacon_data(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "BEACON_DATA")
    result['body'] = binary_helper.build(plc_test_frame.beacon_data.build, "fail to build beacon data", dict_content, data_file, data_str)
    if result['body'] is not None:
        beacon_data = plc_test_frame.beacon_data.parse(result['body'])
        padding_len = beacon_data.pb_size - beacon_data.payload.length
        beacon_data.payload.data = beacon_data.payload.data + '\x00' * padding_len
        result['body'] = plc_test_frame.beacon_data.build(beacon_data)
    return result

def build_time_read_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "TIME_READ_REQ_CMD")
    result['body'] = ''
    return result


def build_time_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "TIME_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.time_config_req.build, "fail to build time config req", dict_content, data_file, data_str)
    return result


def build_band_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "BAND_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.band_config_req.build, "fail to build band config req", dict_content, data_file, data_str)
    return result


def build_phase_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "PHASE_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.phase_config_req.build, "fail to build phase config req", dict_content, data_file, data_str)
    return result

def build_sack_config_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "SACK_CONFIG_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.sack_config_req.build, "fail to build sack config req", dict_content, data_file, data_str)
    return result

def build_sack_config_ex_req(dict_content = None, data_str = None, data_file = None):
    result = dict(cf = "SACK_CONFIG_EX_REQ_CMD")
    result['body'] = binary_helper.build(plc_test_frame.sack_config_ex_req.build, "fail to build sack config ex req", dict_content, data_file, data_str)
    return result

def build_head(total_len, cf, sn=0):
    frame_head = {"len": total_len - 4, "cf": cf, "sn": sn&0xFFFF}
    return plc_test_frame.plc_test_frame_head.build(frame_head)

def build_tail(cs):
    frame_tail = {"cs": cs}
    return plc_test_frame.plc_test_frame_tail.build(frame_tail)

def parse_test_frame(raw_data):
    return binary_helper.parse(plc_test_frame.plc_test_frame.parse, "fail to parse test frame", raw_data)

def parse_test_frame_head(raw_data):
    return binary_helper.parse(plc_test_frame.plc_test_frame_head.parse, "fail to parse test frame head", raw_data)

def get_test_frame_head_size():
    return plc_test_frame.plc_test_frame_head.sizeof()

def get_test_frame_tail_size():
    return plc_test_frame.plc_test_frame_tail.sizeof()


import binary_helper

if __name__ == '__main__':
    pass
