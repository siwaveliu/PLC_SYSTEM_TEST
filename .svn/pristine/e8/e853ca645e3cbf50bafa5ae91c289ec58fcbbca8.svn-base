import os.path
import subprocess
import string
import struct
import sys
import time
import numpy as np
import math
import robot
from multiprocessing import Process, Queue
from robot.api import logger
from ctypes import *
import visa
import config

#SCOPE_IP = '192.168.55.246'
#SCOPE_ADDR = 'TCPIP0::{0}::inst0::INSTR'.format(config.SCOPE_IP)
debug = 0
class Scope_Keysight(object):
    # =========================================================
    # Initialize:
    # =========================================================
    def __init__(self,SCOPE_ADDR):
        #SCOPE_ADDR = 'TCPIP0::{0}::inst0::INSTR'.format(TCPIP_ADDR)
        self.rm = visa.ResourceManager()
        # print rm.list_resources()
        self.Infiniium = self.rm.open_resource(SCOPE_ADDR)
        self.Infiniium.timeout = 20000
        self.Infiniium.clear()
        print("Infiniium Scope Initialization is done")
        logger.info("Infiniium Scope Initialization is done", also_console=True)
	# =========================================================
    # De-Initialize:
    # =========================================================	
    def __del__(self):
        self.Infiniium.close()
        del self.Infiniium
        self.rm.close()
        del self.rm
        logger.info("Infiniium Scope closed", also_console=True)
    # =========================================================
    # reset
    # =========================================================
    def reset(self):
        # Clear status.
        self.do_command("*CLS")
        # Get and display the device's *IDN? string.
        idn_string = self.do_query_string("*IDN?")
        print "Identification string: %s" % idn_string
        # Load the default setup.
        self.do_command("*RST")
        #logger.info("Infiniium Scope is reset", also_console=True)
        print "Infiniium Scope is reset"

    # =========================================================
    # clear
    # =========================================================
    def clear_status(self):
        # Clear status.
        self.do_command("*CLS")
        logger.info("Infiniium Scope's status is  cleared", also_console=True)

    # =========================================================
    # Send a command and check for errors:
    # =========================================================
    def do_command(self, command, hide_params=False):
        if hide_params:
            (header, data) = string.split(command, " ", 1)
            if debug:
                print "\nCmd = '%s'" % header
        else:
            if debug:
                print "\nCmd = '%s'" % command
        self.Infiniium.write("%s" % command)
        if hide_params:
            self.check_instrument_errors(header)
        else:
            self.check_instrument_errors(command)
    # =========================================================
    # Send a command and binary values and check for errors:
    # =========================================================
    def do_command_ieee_block(self,command, values):
        if debug:
            print "Cmb = '%s'" % command
        self.Infiniium.write_binary_values("%s " % command, values, datatype='c')
        self.check_instrument_errors(command)
    # # =========================================================
    # # Send a query, check for errors, return string:
    # # =========================================================
    def do_query_string(self, query):
        if debug:
            print "Qys = '%s'" % query
        result = self.Infiniium.query("%s" % query)
        self.check_instrument_errors(query)
        return result
    # =========================================================
    # Send a query, check for errors, return floating-point value:
    # =========================================================
    def do_query_number(self, query):
        if debug:
            print "Qyn = '%s'" % query
        results = self.Infiniium.query("%s" % query)
        self.check_instrument_errors(query)
        return float(results)
    # =========================================================
    # Send a query, check for errors, return binary values:
    # =========================================================
    def do_query_ieee_block(self, query):
        if debug:
            print "Qyb = '%s'" % query
        result = self.Infiniium.query_binary_values("%s" % query, datatype='s')
        self.check_instrument_errors(query)
        return result[0]

    # =========================================================
    # save scope setup
    # =========================================================
    def save_scope_setup(self):
        sSetup = self.do_query_ieee_block(":SYSTem:SETup?")
        f = open("setup.stp", "wb")
        f.write(sSetup)
        f.close()
        print "Infiniium Setup bytes saved: %d" % len(sSetup)

    # =========================================================
    # save scope setup
    # =========================================================
    def restore_scope_setup(self):
        sSetup = ""
        f = open("setup.stp", "rb")
        sSetup = f.read()
        f.close()
        self.do_command_ieee_block(":SYSTem:SETup", sSetup)
        print "Infiniium Setup bytes restored: %d" % len(sSetup)
    # =========================================================
    # Check for instrument errors:
    # =========================================================
    def check_instrument_errors(self, command):
        while True:
            error_string = self.Infiniium.query(":SYSTem:ERRor? STRing")
            if error_string: # If there is an error string value.
                if error_string.find("0,", 0, 2) == -1: # Not "No error".
                    print "ERROR: %s" % error_string
                    print "Exited because of error."
                    sys.exit(1)
                else: # "No error"
                    break
            else: # :SYSTem:ERRor? STRing should always return string.
                print "ERROR: :SYSTem:ERRor? STRing returned nothing, command: '%s'" % command
                print "Exited because of error."
                sys.exit(1)

    # =========================================================
    # Capture time-domain waveform
    # =========================================================
    def capture_timedomain_waveform(self, sampling_freq, sampling_point, voltage_range, voltage_offset, time_range, trigger_level, diff_on = 1, time_pos = 500E-6, channel=1):
        self.do_command(":AUToscale:CHANnels DISPlayed")
        self.do_command(":ACQuire:SRATe:ANALog {0}".format(sampling_freq))
        self.do_command(":ACQuire:POINts:ANALog {0}".format(sampling_point))
        if diff_on:
            self.do_command(":CHANnel{}:DIFFerential ON".format(channel))
        else:
            self.do_command(":CHANnel{}:DIFFerential OFF".format(channel))
        self.do_command(":CHANnel{}:DISPlay:AUTO ON".format(channel))
        self.do_command(":CHANnel{}:INPut AC".format(channel))
        self.do_command(":CHANnel{0}:RANGe {1}".format(channel,voltage_range))
        self.do_command(":CHANnel{0}:OFFSet {1}".format(channel,voltage_offset))
        self.do_command(":TIMebase:RANGe {0}".format(time_range))
        self.do_command(":TIMebase:POSition {}".format(time_pos))
        # Set trigger mode.
        self.do_command(":TRIGger:MODE EDGE")
        # Set EDGE trigger parameters.
        self.do_command(":TRIGger:EDGE:SOURCe CHANnel{}".format(channel))
        self.do_command(":TRIGger:LEVel CHANnel{0},{1}".format(channel,trigger_level))
        self.do_command(":TRIGger:EDGE:SLOPe POSitive")
        self.do_command(":TRIGger:SWEep TRIGgered")
        # Set the acquisition mode.
        self.do_command(":ACQuire:MODE RTIMe")
        if debug:
            qresult = self.do_query_string(":TRIGger:MODE?")
            print "Trigger mode: %s" % qresult
            qresult = self.do_query_string(":TRIGger:EDGE:SOURce?")
            print "Trigger edge source: %s" % qresult
            qresult = self.do_query_string(":TRIGger:LEVel? CHANnel{}".format(channel))
            print "Trigger level: %s" % qresult
            qresult = self.do_query_string(":TRIGger:EDGE:SLOPe?")
            print "Trigger edge slope: %s" % qresult
        time.sleep(1)
    # =========================================================
    # Function: FFT
    # =========================================================
    def function_fft(self, freq_start,freq_stop, vertical_scale, reference_level, channel=1,detect_type=1):
        #freq_center = (freq_stop - freq_start)/2
        self.do_command(":FUNCtion1:DISPlay ON")
        self.do_command(":FUNCtion1:FFTMagnitude CHANnel{}".format(channel))
        self.do_command(":FUNCtion1:FFT:FREQuency {0}".format(freq_start))
        #do_command(":FUNCtion1:FFT:SPAN {0}".format(freq_stop-freq_start))
        self.do_command(":FUNCtion1:FFT:STOP {0}".format(freq_stop))
        #do_command(":FUNCtion1:FFT:RESolution 100000")
        self.do_command(":FUNCtion1:FFT:VUNits DB")
        if detect_type==1:
            self.do_command(":FUNCtion1:FFT:DETector:TYPE AVERage")
        else:
            self.do_command(":FUNCtion1:FFT:DETector:TYPE PPOSitive")
        self.do_command(":FUNCtion1:FFT:DETector:POINts 1000")
        self.do_command(":FUNCtion1:VERTical MANual")
        self.do_command(":FUNCtion1:VERTical:RANGe {0}".format(vertical_scale*10))
        self.do_command(":FUNCtion1:VERTical:OFFSet {0}".format(reference_level))
        time.sleep(1)
    # =========================================================
    # Measure: FFT
    # =========================================================
    def query_fft_meas_result(self,freq_center, bandwidth, occupied_percent):
        result = [None, None, None, None]
        result[0] = self.do_query_number(":MEASure:FFT:CPOWer? FUNCtion1,{0}, {1}".format(freq_center, bandwidth))
        result[1] = self.do_query_number(":MEASure:FFT:PSD? FUNCtion1,{0}, {1}".format(freq_center, bandwidth))
        result[2] = (self.do_query_number(":MEASure:FFT:OBW? FUNCtion1,{0}".format(occupied_percent))) / 1000000
        result[3] = self.do_query_number(""
                                         ":FUNCtion1:FFT:RESolution?")
        return result

    def measure_fft(self, freq_center, bandwidth, occupied_percent):
        self.do_command(":MEASure:FFT:CPOWer FUNCtion1,{0}, {1}".format(freq_center, bandwidth))
        self.do_command(":MEASure:FFT:OBW FUNCtion1,{0}".format(occupied_percent))
        self.do_command(":MEASure:FFT:PSD FUNCtion1,{0}, {1}".format(freq_center, bandwidth))
        time.sleep(2)
        result = self.query_fft_meas_result(freq_center, bandwidth, occupied_percent)
        return result
    # =========================================================
    # Analyse fft measurement results.
    # =========================================================
    def analyse_fft_waveform(self, pwr_th):
        # Set the waveform source.
        self.do_command(":WAVeform:SOURce FUNCtion1")
        # Choose the format of the data returned:
        self.do_command(":WAVeform:FORMat ASCII")
        # Get the number of waveform points.
        wave_len = int(self.do_query_number(":WAVeform:POINts?"))
        # Get X-axis
        freq_start = self.do_query_number(":WAVeform:XORigin?")
        freq_step = self.do_query_number(":WAVeform:XINCrement?")
        if debug:
            # Get the waveform type.
            print "Waveform type: %s" % self.do_query_string(":WAVeform:TYPE?")
            print "waveform length:", wave_len
        # read raw waveform data
        self.Infiniium.write(":WAVeform:DATA?")
        data = self.Infiniium.read_raw()
        data1 = data.split(",")
        data2 = np.array(map(eval,data1[0:wave_len-1]))
        #print data2
        idx = np.nonzero(data2>pwr_th)
        idx_rng = np.arange(wave_len)
        #print "valid subcarrier index:", mat(idx)
        #valid_len = len(idx)
        idx1 = idx_rng[idx]
        valid_psd = data2[idx]
        valid_len = len(idx1);
        delete_idx = [0, 1, 2, 3, 4, 5, valid_len-5, valid_len-4, valid_len-3, valid_len-2, valid_len-1]
        valid_psd_cut = np.delete(valid_psd, delete_idx)
        psd_max = np.max(valid_psd_cut)
        psd_min = np.min(valid_psd_cut)
        psd_ripple = psd_max - psd_min
        if (valid_len>0):
            freq_valid_left = (freq_start + freq_step * idx1[0])/1000000
            freq_valid_right = (freq_start + freq_step * idx1[-1])/1000000
            bandwidth_valid = freq_valid_right - freq_valid_left # + freq_step/1000000
        else:
            freq_valid_left = 0
            freq_valid_right = 0
            bandwidth_valid = 0
        if debug:
            print data1
            print "waveform length:", len(data1)
            print "valid length after delete:", len(valid_psd)
            print "freq start:", freq_start, "freq step:", freq_step, "valid_len:", valid_len, "psd_max:", psd_max, "psd_min:", psd_min, "psd_ripple:", psd_ripple
            # print idx1
            print "idx[0]:", idx1[0], "idx[end]:", idx1[-1]
            print "freq_valid_left: ", freq_valid_left, "; freq_valid_right: ", freq_valid_right, "; bandwidth_valid: ", bandwidth_valid
            print "Waveform source: %s" % self.do_query_string(":WAVeform:SOURce?")
            print "Waveform format: %s" % self.do_query_string(":WAVeform:FORMat?")
        result = [0,0,0,0,0,0]
        result[0] = freq_valid_left
        result[1] = freq_valid_right
        result[2] = bandwidth_valid
        result[3] = psd_max
        result[4] = psd_min
        result[5] = psd_ripple
        return result

    # =========================================================
    # Measure: Vmax
    # =========================================================
    def measure_Vmax(self, channel=1):
        self.do_command(":MEASure:VMAX CHANnel{}".format(channel))
        time.sleep(1)
        vmax = self.do_query_number(":MEASure:VMAX? CHANnel{}".format(channel))
        return float(vmax)