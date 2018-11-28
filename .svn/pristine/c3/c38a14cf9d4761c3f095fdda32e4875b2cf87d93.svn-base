import os
import json
import yaml
import plc_tb_ctrl

# builder: construct build method
def build(builder, err_msg, dict_content = None, data_file = None, data_str = None):
    body = None
    try:
        msg = None
        if dict_content is not None:
            msg = dict_content
        elif data_file is not None:
            data_file_full_path = os.path.join(plc_tb_ctrl.curr_tc_dir, data_file)
            if not os.path.exists(data_file_full_path):
                data_file_full_path = os.path.join(plc_tb_ctrl.COMMON_DATA_PATH, data_file)
            assert os.path.exists(data_file_full_path), '{} not found'.format(data_file_full_path)
            plc_tb_ctrl._debug('Load file {}'.format(data_file_full_path))
            f = open(data_file_full_path)
            data = f.read()
            f.close()
            msg = yaml.load(data)
        elif data_str is not None:
            msg = yaml.load(data_str)
        else:
            assert False, 'Incorrect arguments for build'

        if msg is not None:
            body = builder(msg)
    except Exception as e:
        plc_tb_ctrl._debug(e.message)
        plc_tb_ctrl._debug(err_msg)

    return body


def parse(parser, err_msg, raw_data):
    data = None

    try:
        data = parser(raw_data)
    except Exception as e:
        plc_tb_ctrl._debug(e.message)
        plc_tb_ctrl._debug(err_msg)

    return data


if __name__ == '__main__':
    pass
