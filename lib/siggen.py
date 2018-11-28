import os.path
import subprocess
import sys
from struct import *
import time
import robot
from multiprocessing import Process, Queue
from robot.api import logger
from ctypes import *
import visa
from ftplib import FTP
import config

# 4438C: 192.168.66.247
# N5182B: 192.168.66.245
SG_IP = 'config.SIGGEN_ADDR'
SG_ADDR = 'TCPIP0::{0}::inst0::INSTR'.format(config.SIGGEN_ADDR)
#WV_FILE_READ_BLOCK_SIZE = 64*1024*1024

# waveform file directory
DATA_DIR = 'data'

class SigGen_Keysight(object):

    def __init__(self, SG_ADDR):
        self.rm = visa.ResourceManager()
        self.inst = self.rm.open_resource(SG_ADDR)
        logger.info("n5182b opened", also_console=True)
        print("init")

    def __del__(self):
        self.inst.close()
        del self.inst       
        self.rm.close()
        del self.rm
        logger.info("n5182b closed", also_console=True)

    def reset(self):
        logger.info("n5182b: reset")
        self.inst.write('*RST')
        self._wait_op_complete()
        
    def test_test(self):
        logger.info("test test")
    
    def load_waveform(self, wv_name):
        logger.info("Load waveform {0}".format(wv_name))
        result = self.inst.query(':MMEMory:CATalog? "NVWFM:{0}"'.format(wv_name))
        print(result)
        item_num = len(result.split(','))
        if (item_num > 2):
            # waveform file exists in NV
            self.inst.write(':MEMory:COPY:NAME "NVWFM:{0}","WFM1:{0}"'.format(wv_name))
        else:
            logger.info('The waveform file {0} is not found in SG'.format(wv_name))
            logger.info('Upload waveform file {0} from PC to SG'.format(wv_name))
            wv_file = open(os.path.join(DATA_DIR, wv_name), 'rb')
            try:
                sg_ftp = FTP(SG_IP)
                result = sg_ftp.login()
                result.index('230')
                logger.info(result)
                result = sg_ftp.cwd('/USER/BBG1/WAVEFORM')
                result.index('250')
                logger.info(result)
                result = sg_ftp.storbinary('STOR {0}'.format(wv_name), wv_file)
                result.index('226')
                logger.info(result)
            finally:
                wv_file.close()
                sg_ftp.quit()

            # we don't use this method because the transmission speed is slow
            #try:
            #    # disable EOF send
            #    self.inst.set_visa_attribute(visa.constants.VI_ATTR_SEND_END_EN, False)
            #    
            #    # get file size
            #    wv_file.seek(0, os.SEEK_END)
            #    file_size = str(wv_file.tell())
            #    
            #    # go back to file start
            #    wv_file.seek(0, os.SEEK_SET)
            #    
            #    # send command
            #    self.inst.write_raw(':MMEM:DATA "WFM1:{0}",#{1}{2}'.format(wv_name, len(file_size), file_size))
            #    # send data
            #    while (True):
            #        buffer = wv_file.read(WV_FILE_READ_BLOCK_SIZE)
            #        print("read len {0}".format(len(buffer)))
            #        if (len(buffer) > 0):
            #            self.inst.write_raw(buffer)
            #        if (len(buffer) < WV_FILE_READ_BLOCK_SIZE):
            #            break;
            #    # enable EOF send        
            #    self.inst.set_visa_attribute(visa.constants.VI_ATTR_SEND_END_EN, True)
            #    # send termination and EOF
            #    self.inst.write('')
            #finally:
            #    wv_file.close()
        self.inst.write(':SOURce:RADio:ARB:WAVeform "WFM1:{0}"'.format(wv_name))
        # wait waveform loading to complete
        self._wait_op_complete()
        

        
    def delete_waveform(self, wv_name):
        logger.info("n5182b: delete all waveforms in memory")
        self.inst.write(':MMEMory:DELete:NAME "WFM1:{0}";*OPC?'.format(wv_name))
        
    def delete_all_waveform(self):
        self.inst.write(':MMEMory:DELete:WFM')
        self._wait_op_complete()

                
    def set_freq(self, freq):
        logger.info("N5182B: Set freq {0}MHz".format(freq))
        self.inst.write(':FREQuency:CW {0}MHz'.format(freq))
    
    def set_alc(self, action):
        logger.info("N5182B: Set ALC {0}".format(action))
        self.inst.write(':POWer:ALC {0}'.format(action))
        
    def set_amplitude(self, amplitude):
        self.inst.write(':POWer:LEVel {0}DBM'.format(amplitude))
    
    # Sample clock rate in MHz
    def set_arb_sample_rate(self, sample_rate):
        logger.info("N5182B: ARB Sample Rate {0}Mhz".format(sample_rate))
        self.inst.write(':RADio:ARB:SCLock:RATE {0}MHz'.format(sample_rate))
        
    def enable_awgn(self, NBW, CBW, inital_snr):
        logger.info("N5182B: set ARB AWGN BW {0}MHz".format(CBW))
        self.inst.write(':RADio:ARB:NOISe:BANDwidth {0}MHz'.format(CBW))
        self.inst.write(':RADio:ARB:NOISe:CBWidth {0}MHz'.format(NBW))
        self.inst.write(':RADio:ARB:NOISe:CNFormat CN')
        self.inst.write(':RADio:ARB:NOISe:CN {0}DB'.format(inital_snr))
        self.inst.write(':RADio:ARB:NOISe ON')
        self.inst.query('*OPC?')
        
    def change_awgn_snr(self, snr):
        logger.info("N5182B: set ARB AWGN SNR {0}dB".format(snr))
        self.inst.write(':RADio:ARB:NOISe:CN {0}DB'.format(snr))
        #self.inst.query('*OPC?')
        self._wait_op_complete()
        
    def arb_on(self, delay):
        time.sleep(float(delay))
        self.inst.write(':SOURce:RADio:ARB:STATe ON')
    
    def awgn_on(self,NBW,CBW):
        self.inst.write(':SOURce:RADio:AWGN:RT:STATe ON')
        self.inst.write(':SOURce:RADio:AWGN:RT:BWIDth {0}MHz'.format(NBW))
        self.inst.write(':SOURce:RADio:AWGN:RT:CBWidth {0}MHz'.format(CBW))
        self.inst.query('*OPC?')

    def noise_power(self,pwr_dbm):
        self.inst.write(':SOURce:RADio:AWGN:RT:POWer:CONTrol:MODE TOTal')
        self.inst.write(':SOURce:RADio:AWGN:RT:POWer:NOISe:CHANnel {0}'.format(pwr_dbm))
        self.inst.query('*OPC?')

    def noise_atten(self,attn_db):
        self.inst.write(':SOURce:RADio:AWGN:RT:IQ:MODulation:ATTen:AUTO OFF')
        self.inst.write(':SOURce:RADio:AWGN:RT:IQ:MODulation:ATTen {0}'.format(attn_db))
        self.inst.query('*OPC?')
    
    def arb_off(self):
        self.inst.write(':SOURce:RADio:ARB:STATe OFF')
        
    def awgn_off(self):
        self.inst.write(':SOURce:RADio:AWGN:RT:STATe OFF')
    
    def play_waveform(self):
        #self.inst.write(':SOURce:RADio:ARB:STATe ON')
        # I/Q ON
        self.inst.write(':DM:STATe ON')
        # Modulation ON
        self.inst.write(':OUTPut:MODulation:STATe ON')
        # no need to turnon RF for digital output
        # RF ON
        # self.inst.write(':OUTPut:STATe ON;*OPC?')
    def play_waveform_rf(self):
        self.inst.write(':SOURce:RADio:ARB:STATe ON')
        # I/Q ON
        #self.inst.write(':DM:STATe ON')
        # Modulation ON
        self.inst.write(':OUTPut:MODulation:STATe ON')
        # no need to turnon RF for digital output
        # RF ON
        self.inst.write(':OUTPut:STATe ON;*OPC?')    
    def _wait_op_complete(self):
        while (True):
            try:
                logger.info("wait opc") 
                v = self.inst.query_ascii_values('*OPC?')
                result = int(v[0]);
                logger.info("OPC:{0}".format(result))
                if (v[0] == 1):
                    break
            except:
                logger.info("except") 
                pass
                
            time.sleep(2)

    def enable_modu_attn(self,attn_db):
        logger.info("N5182B: set IQ MODULATOR ATTENUATION TO MANUAL {0}dB".format(attn_db))
        self.inst.write(':RADio:ARB:IQ:MODulation:ATTen:AUTO OFF')
        self.inst.write(':RADio:ARB:IQ:MODulation:ATTen {0}'.format(attn_db))        
        self.inst.query('*OPC?')
        
    def enable_iq_attn(self,iq_attn_db):
        logger.info("E4438C: set IQ MODULATOR ATTENUATION TO MANUAL {0}dB".format(iq_attn_db))
        self.inst.write(':SOURce:DM:IQAD:STATe ON')    
        self.inst.write(':SOURce:DM:IQAD:EXT:IQAT {0}'.format(iq_attn_db))        
        self.inst.query('*OPC?')    
            
    def rf_on(self):
        self.inst.write(':SOURce:RADio:ARB:STATe OFF')
        # I/Q ON
        #self.inst.write(':DM:STATe ON')
        # Modulation ON
        self.inst.write(':OUTPut:MODulation:STATe OFF')
        # no need to turnon RF for digital output
        # RF ON
        self.inst.write(':OUTPut:STATe ON;*OPC?')  
    