import os
import shutil
import plc_tb_ctrl

ROBOT_LISTENER_API_VERSION = 3

def copyfile_to_output_dir(filepath):
	filename = os.path.basename(filepath)
	shutil.copyfile(filepath, os.path.join(plc_tb_ctrl.output_dir, filename))

def log_file(path):
	copyfile_to_output_dir(path)

def output_file(path):
	copyfile_to_output_dir(path)

def report_file(path):
	copyfile_to_output_dir(path)

