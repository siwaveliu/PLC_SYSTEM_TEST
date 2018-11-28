from struct import *
import collections
import time
import math


def int2bin(n, count=24):
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])
    
class ToneMaskConfig():

    def __init__(self,tone_mask_file,ValidCarrierNum,band,narrow_f,afe_type):
        self.add_A000_static_para=[]
        self.add_5007_static_para=[]
        self.add_5007_tonemask=[]
        self.cmd_write = []
        self.reg_narrow = []
        self.band = band
        self.narrow_f = narrow_f
        self.afe_type = afe_type
        self.tone_mask_file = tone_mask_file
        self.ValidCarrierNum = ValidCarrierNum

    def write_reg_tonemask(self):
        add_5007 = []
        add_base = 0x500710C0
        add_cur = add_base - 4
        strc = ''
        fp_obj = open(self.tone_mask_file)
        for line in fp_obj.readlines():
            strc += str(int(line.strip(), 2) ^ 1)
    
        ss = ''
        ss1 = []
        for i in range(0, int(512 / 32)):
            for j in range(0, 32):
                ss += strc[j + i * 32]
            ss = ss[::-1]
            add_cur += 4
            add_str = hex(add_cur)
            s = '{:x}'.format(int(ss, 2))
            cmd_str_tone = 'memwrite 32 ' + add_str + ' 0x' + s
            add_5007.append(cmd_str_tone + '\r\n')
            ss1.append(s)
            ss = ''
        
        self.add_5007_tonemask=add_5007
        
    def phy_static_para(self):
        ValidCarrierNum = self.ValidCarrierNum
        add_A000 = []
        add_5007 = []
        tmi_dict = collections.OrderedDict()
        tmi_dict['B_tmi0']=[520,4,'qpsk',1./2]
        tmi_dict['B_tmi1']=[520,2,'qpsk',1./2]
        tmi_dict['B_tmi2']=[136,5,'qpsk',1./2]
        tmi_dict['B_tmi3']=[136,11,'bpsk',1./2]
        tmi_dict['B_tmi4']=[136,7,'bpsk',1./2]
        tmi_dict['B_tmi5']=[136,11,'qpsk',1./2]
        tmi_dict['B_tmi6']=[136,7,'qpsk',1./2]
        tmi_dict['B_tmi7']=[520,7,'bpsk',1./2]
        tmi_dict['B_tmi8']=[520,4,'bpsk',1./2]
        tmi_dict['B_tmi9']=[520,7,'qpsk',1./2]
        tmi_dict['B_tmi10']=[520,2,'bpsk',1./2]
        tmi_dict['B_tmi11']=[264,7,'qpsk',1./2]
        tmi_dict['B_tmi12']=[264,7,'bpsk',1./2]
        tmi_dict['B_tmi13']=[72,7,'qpsk',1./2]
        tmi_dict['B_tmi14']=[72,7,'bpsk',1./2]
        tmi_dict['E_tmi1']=[520,1,'16qam',16./18]
        tmi_dict['E_tmi2']=[520,2,'16qam',16./18]
        tmi_dict['E_tmi3']=[520,1,'16qam',1./2]
        tmi_dict['E_tmi4']=[520,2,'16qam',1./2]
        tmi_dict['E_tmi5']=[520,4,'16qam',1./2]
        tmi_dict['E_tmi6']=[520,1,'qpsk',1./2]
        tmi_dict['E_tmi10']=[136,5,'16qam',1./2]
        tmi_dict['E_tmi11']=[136,2,'qpsk',1./2]
        tmi_dict['E_tmi12']=[136,2,'16qam',1./2]
        tmi_dict['E_tmi13']=[136,1,'qpsk',1./2]
        tmi_dict['E_tmi14']=[136,1,'16qam',1./2]
        InterNumVec = [0,1,8,0,8,10,0,14,0,0,0,11]
        InterNumGVec =[0,1,4,0,2, 2,0, 2,0,0,0, 1]
        cmd_list=[]
        add_list=[]
        add_base=0xA0003080
        add_cur=add_base-4
        add_cur_140 = 0x50071140
        add_cur_ofdm = 0x5007120c
        ofdm_print_flag = 0
        for key in tmi_dict:
            #print(key)
            #fp_log.write(key+'\n')
            DataBitsLen = int(tmi_dict[key][0]*8/tmi_dict[key][3])
            CopyNum = tmi_dict[key][1]
            InterNum = InterNumVec[tmi_dict[key][1]]
            UsedCarrierNum = InterNum*math.floor(ValidCarrierNum/InterNum)
            CarrierNumPerGroup = math.floor(UsedCarrierNum/tmi_dict[key][1])
            CarrierNumPerInter = math.floor(ValidCarrierNum/InterNum)
            if tmi_dict[key][2]=='bpsk':
                BPC = 1
            elif tmi_dict[key][2]=='qpsk':
                BPC = 2
            elif tmi_dict[key][2]=='16qam':
                BPC = 4
            BitsPerOFDM = BPC*UsedCarrierNum
            BitsPerGroup = BPC*CarrierNumPerGroup
            BitsInLastOFDM = DataBitsLen-BitsPerOFDM*math.floor(DataBitsLen/BitsPerOFDM)
            if BitsInLastOFDM==0:
                BitsInLastOFDM = BitsPerOFDM
                BitsInLastGroup = BitsPerGroup
            else:
                BitsInLastGroup = BitsInLastOFDM-BitsPerGroup*math.floor((BitsInLastOFDM-1)/BitsPerGroup)
            PadBitsNum = int(BitsPerGroup-BitsInLastGroup)
            InterNumPerCopy = int((PadBitsNum+DataBitsLen)/(BPC*CarrierNumPerInter))
            OFDMSymPerPB = int((PadBitsNum+DataBitsLen)/(BitsPerOFDM)*CopyNum)
            SamplePiontNum=(OFDMSymPerPB-2)*(264+1024)+2*(458+1024)
    
    
            if CopyNum==1:
                InterNumPerCopy=1
            ""
            tmi_dict[key].append(DataBitsLen)
            tmi_dict[key].append(InterNum)
            tmi_dict[key].append(UsedCarrierNum)
            tmi_dict[key].append(CarrierNumPerGroup)
            tmi_dict[key].append(CarrierNumPerInter)
            tmi_dict[key].append(BPC)
            tmi_dict[key].append(BitsPerOFDM)
            tmi_dict[key].append(BitsPerGroup)
            tmi_dict[key].append(BitsInLastOFDM)
            tmi_dict[key].append(BitsInLastGroup)
            tmi_dict[key].append(PadBitsNum)
            tmi_dict[key].append(InterNumPerCopy)
            tmi_dict[key].append(OFDMSymPerPB)
            tmi_dict[key].append(SamplePiontNum)
            ""
            if CopyNum==1:
                GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
            elif CopyNum==2:
                if BitsInLastOFDM<=BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                else:
                    GroupShiftNum = [1,0,0,0,0,0,0,0,0,0]
            elif CopyNum==4:
                if BitsInLastOFDM<=BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                elif BitsInLastOFDM<=2*BitsPerGroup:
                    GroupShiftNum = [0,1,1,0,0,0,0,0,0,0]
                elif BitsInLastOFDM<=3*BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                else:
                    GroupShiftNum = [1,2,3,0,0,0,0,0,0,0]
            elif CopyNum==5:
                if BitsInLastOFDM<=4*BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                else:
                    GroupShiftNum = [1,2,3,4,0,0,0,0,0,0]
            elif CopyNum==7:
                if BitsInLastOFDM<=6*BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                else:
                    GroupShiftNum = [1,2,3,4,5,6,0,0,0,0]
            elif CopyNum==11:
                if BitsInLastOFDM<=10*BitsPerGroup:
                    GroupShiftNum = [0,0,0,0,0,0,0,0,0,0]
                else:
                    GroupShiftNum = [1,2,3,4,5,6,7,8,9,10]
            ""
            GroupShiftNum_L = GroupShiftNum[0:2]
            GroupShiftNum_H = GroupShiftNum[2:11]
            tmi_dict[key].append(GroupShiftNum)
            InterShiftStep = math.floor(CarrierNumPerInter/(2*InterNum))
            if InterShiftStep<1:
                InterShiftStep=0
            elif InterShiftStep<2:
                InterShiftStep=1
            elif InterShiftStep<4:
                InterShiftStep=2
            elif InterShiftStep<8:
                InterShiftStep=4
            elif InterShiftStep<16:
                InterShiftStep=8
            if CopyNum==1:
                InterShiftStep=1
            tmi_dict[key].append(InterShiftStep)
            ""
            PARA1=''
            PARA1+=int2bin(GroupShiftNum_L[1],4)
            PARA1+=int2bin(GroupShiftNum_L[0],4)
            PARA1+=int2bin(InterShiftStep,4)
            PARA1+=int2bin(int(PadBitsNum),11)
            PARA1+=int2bin(int(UsedCarrierNum),9)
            cmd_list.append(PARA1)
            add_cur = add_cur+4
            add_list.append(add_cur)
            add_str = hex(add_cur)
            cmd_str = 'memwrite 32 '+add_str[:-1]+' 0x'+'{:x}'.format(int(PARA1,2))
            #print(cmd_str)
            #fp_log.write(cmd_str+'\n')
            add_A000.append(cmd_str+'\r\n')
    
            PARA2=''
            PARA2+=int2bin(GroupShiftNum_H[7],4)
            PARA2+=int2bin(GroupShiftNum_H[6],4)
            PARA2+=int2bin(GroupShiftNum_H[5],4)
            PARA2+=int2bin(GroupShiftNum_H[4],4)
            PARA2+=int2bin(GroupShiftNum_H[3],4)
            PARA2+=int2bin(GroupShiftNum_H[2],4)
            PARA2+=int2bin(GroupShiftNum_H[1],4)
            PARA2+=int2bin(GroupShiftNum_H[0],4)
            cmd_list.append(PARA2)
            add_cur = add_cur+4
            add_list.append(add_cur)
            add_str = hex(add_cur)
            cmd_str = 'memwrite 32 '+add_str[:-1]+' 0x'+'{:x}'.format(int(PARA2,2))
            #print(cmd_str)
            #fp_log.write(cmd_str+'\n')
            add_A000.append(cmd_str+'\r\n')
    
            PARA3=''
            PARA3+=int2bin(int(CarrierNumPerInter),6)
            PARA3+='0'
            PARA3+=int2bin(int(BitsPerGroup),11)
            PARA3+=int2bin(InterNumPerCopy,14)
            cmd_list.append(PARA3)
            add_cur = add_cur+4
            add_list.append(add_cur)
            add_str = hex(add_cur)
            cmd_str = 'memwrite 32 '+add_str[:-1]+' 0x'+'{:x}'.format(int(PARA3,2))
            #print(cmd_str)
            #fp_log.write(cmd_str+'\n')
            add_A000.append(cmd_str+'\r\n')
    
            add_cur_140+=4
            add_cur_140_str = hex(add_cur_140)
            cmd_str1 = 'memwrite 32 ' +add_cur_140_str + ' 0x'+'{:x}'.format(int(int2bin(SamplePiontNum,23),2))
            #print(cmd_str1)
            #fp_log.write(cmd_str1+'\n')
            add_5007.append(cmd_str1+'\r\n')
    
            if ofdm_print_flag==0:
                ofdm_print_flag = 1
                last_ofdm_num = OFDMSymPerPB
            else:
                ofdm_print_flag = 0
                ofdm_para = ''
                ofdm_para+=int2bin(int(OFDMSymPerPB),13)
                ofdm_para+=int2bin(int(last_ofdm_num),13)
                add_cur_ofdm_str = hex(add_cur_ofdm)
                cmd_str2 = 'memwrite 32 ' +add_cur_ofdm_str + ' 0x'+'{:x}'.format(int(ofdm_para,2))
                #print(cmd_str2)
                #fp_log.write(cmd_str2+'\n')
                add_5007.append(cmd_str2+'\r\n')
                add_cur_ofdm+=4
    
        val_rp = int(round((1./ValidCarrierNum)*2**15))
        if val_rp>=255:
            val_rp=255
        cmd_140 = '0000'+int2bin(val_rp,8)+'00000000000'+int2bin(int(ValidCarrierNum),9)
        #cmd_140 = '0000'+int2bin(int(round((1/UsedCarrierNum)*2**15)),8)+'00000000000'+int2bin(int(UsedCarrierNum),9)
        cmd_str2 = 'memwrite 32 ' + '0x50071140' + ' 0x'+'{:x}'.format(int(cmd_140,2))
        add_5007.append(cmd_str2+'\r\n')
    
        self.add_A000_static_para = add_A000
        self.add_5007_static_para = add_5007
        #logger.info('static para OK')  

    def sync_ce_tm_reg_new(self):
    
        band=self.band
        narrow_freq_Mhz=self.narrow_f
        afe_type=self.afe_type
    
        reg_narrow = []
    
        agc_ref_pwr = 54;
        coarse_sync_iir_coef = 51
        peakpos_finetune = 1
        LP_Block_scale = 1;
        lowpwr_extract_mode = 1;
        adc_cut_bitwidth = 0;
        max2submax_check_win = 20
        coarse_sync_confnbr = 2;
        notch_alpha = 0.875
        fine_sync_td_dagc_ref = int(1.0*2048)
    
        if (afe_type == 0):
            afe_min_gain = 238;
            afe_max_gain = 48;
        else:
            afe_min_gain = 229;
            afe_max_gain = 76;
    
        convex_thres = 12
        fine_sync_thres = 82
    
        if band == 0:
            ValidCarrierNum = 411;
            band_startidx = 80;
            band_endidx = 490;
            g_scale = 0;
            VdivN = 1;
            M_fxp = 0;
            Nfft = 1;
            lpf_sel = 0;
            dwn_sample = 2;
            if narrow_freq_Mhz is '1m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 80;
                fdmeanpwr_startidx = 150;
                fdmeanpwr_len = 8;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 29;
                coarse_sync_thres2 = 29;
            elif narrow_freq_Mhz is '8m':
                sync_ce_tm_enable = 1;
                fdpwr_startidx = 127;
                fdmeanpwr_startidx = 80;
                fdmeanpwr_len = 7;
                powersaving_enable = 1;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 1;
                max2submax_check_thres = 2;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 4;
                coarse_sync_thres2 = 4;
            elif narrow_freq_Mhz is '15m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 80;
                fdmeanpwr_startidx = 150;
                fdmeanpwr_len = 8;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 60;
                coarse_sync_thres2 = 60;
            else:
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 80;
                fdmeanpwr_startidx = 150;
                fdmeanpwr_len = 8;
                powersaving_enable = 1;  #
                fd_notch_ratio = 4;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 29;
                coarse_sync_thres2 = 29;
    
        elif band == 1:
            ValidCarrierNum = 131;
            band_startidx = 100;
            band_endidx = 230;
            g_scale = 0;
            VdivN = 3;
            M_fxp = 0;
            Nfft = 0;
            lpf_sel = 1;
            dwn_sample = 4;
            if narrow_freq_Mhz is '1m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 100;
                fdmeanpwr_startidx = 130;
                fdmeanpwr_len = 6;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 1;
                par_check_enable = 0;
                par_check_thres = 0;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 0;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 64;
                coarse_sync_thres2 = 64;
            elif narrow_freq_Mhz is '3m':
                sync_ce_tm_enable = 1;
                fdpwr_startidx = 127;
                fdmeanpwr_startidx = 167;
                fdmeanpwr_len = 6;
                powersaving_enable = 1;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 1;
                par_check_thres = 4;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 8;
                coarse_sync_thres2 = 8;
            elif narrow_freq_Mhz is '6m':
                sync_ce_tm_enable = 1;
                fdpwr_startidx = 100;
                fdmeanpwr_startidx = 100;
                fdmeanpwr_len = 6;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 1;
                par_check_thres = 4;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 8;
                coarse_sync_thres2 = 8;
            else:
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 100;
                fdmeanpwr_startidx = 130;
                fdmeanpwr_len = 6;
                powersaving_enable = 1;  #
                fd_notch_ratio = 4;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 64;
                coarse_sync_thres2 = 64;
    
        elif band == 2:
            ValidCarrierNum = 89;
            band_startidx = 32;
            band_endidx = 120;
            g_scale = 1;
            VdivN = 3;
            M_fxp = 1;
            Nfft = 0;
            lpf_sel = 2;
            dwn_sample = 4;
            if narrow_freq_Mhz is '0p5m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 32;
                fdmeanpwr_startidx = 53;
                fdmeanpwr_len = 6;
                powersaving_enable = 1;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 3;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 150*2;
                coarse_sync_thres2 = 150*2;
            elif narrow_freq_Mhz is '2m':
                sync_ce_tm_enable = 1;
                fdpwr_startidx = 32;
                fdmeanpwr_startidx = 32;
                fdmeanpwr_len = 5;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 1;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 5;
                coarse_sync_thres2 = 5;
            elif narrow_freq_Mhz is '5m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 32;
                fdmeanpwr_startidx = 53;
                fdmeanpwr_len = 6;
                powersaving_enable = 1;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 200;
                coarse_sync_thres2 = 200;
            else:
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 32;
                fdmeanpwr_startidx = 53;
                fdmeanpwr_len = 6;
                powersaving_enable = 1;  #
                fd_notch_ratio = 4;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 150;
                coarse_sync_thres2 = 150;
        elif band == 3:
            ValidCarrierNum = 49;
            band_startidx = 72;
            band_endidx = 120;
            g_scale = 1;
            VdivN = 4;
            M_fxp = 1;
            Nfft = 0;
            lpf_sel = 2;
            dwn_sample = 4;
            if narrow_freq_Mhz is '0p5m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 72;
                fdmeanpwr_startidx = 85;
                fdmeanpwr_len = 5;
                powersaving_enable = 1;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 150;
                coarse_sync_thres2 = 150;
                notch_alpha = 0.875
            elif narrow_freq_Mhz is '2m':
                sync_ce_tm_enable = 1;
                fdpwr_startidx = 100;
                fdmeanpwr_startidx = 105;
                fdmeanpwr_len = 4;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 1;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 1;
                par_check_thres = 4;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 5;
                coarse_sync_thres2 = 5;
            elif narrow_freq_Mhz is '5m':
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 72;
                fdmeanpwr_startidx = 85;
                fdmeanpwr_len = 5;
                powersaving_enable = 0;  #
                fd_notch_ratio = 2;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 150;
                coarse_sync_thres2 = 150;
            else:
                sync_ce_tm_enable = 0;
                fdpwr_startidx = 72;
                fdmeanpwr_startidx = 85;
                fdmeanpwr_len = 5;
                powersaving_enable = 1;  #
                fd_notch_ratio = 4;  #
                coarse_sync_iir_bypass = 0;
                notch_zero_check_enable = 1;
                notch_zero_check_thres = 0;
                par_check_enable = 0;
                par_check_thres = 5;  # 4/6/8/10/12/14/16
                max2submax_check_enable = 0;
                max2submax_check_thres = 3;  # 1.5/2/2.5/3/3.5/4
                coarse_sync_thres1 = 128;
                coarse_sync_thres2 = 128;
        
        notch_alpha_big = int(notch_alpha * 64 + 0.5)
        notch_alpha_small = int(notch_alpha / dwn_sample * 64 + 0.5)
    
        cmd_val = int2bin(notch_zero_check_enable, 1) + int2bin(notch_zero_check_thres, 6) + int2bin(fdpwr_startidx,7) + \
                int2bin(g_scale,2) + int2bin(VdivN, 3) + int2bin(fdmeanpwr_startidx, 9) + int2bin(fdmeanpwr_len, 4)
        cmd_str = 'memwrite 32 ' + '0x50071240' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = '0' + int2bin(powersaving_enable, 1) + '10' + int2bin(max2submax_check_win, 4) + \
                int2bin(max2submax_check_enable, 1) + int2bin(max2submax_check_thres, 3) + int2bin(par_check_enable, 1) + \
                int2bin(par_check_thres, 3) + int2bin(M_fxp, 2) + int2bin(Nfft, 1) + int2bin(LP_Block_scale, 2) + \
                int2bin(adc_cut_bitwidth, 3) + int2bin(lowpwr_extract_mode, 2) + int2bin(lpf_sel, 2) + int2bin(fd_notch_ratio, 4)
        cmd_str = 'memwrite 32 ' + '0x500711ac' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = int2bin(band_endidx, 9) + int2bin(band_startidx, 9) + '0' + int2bin(sync_ce_tm_enable,1) + \
                '00' + int2bin(self.band,2) + '00000000'
        cmd_str = 'memwrite 32 ' + '0x50070040' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = int2bin(coarse_sync_thres1, 10) + int2bin(coarse_sync_thres2, 12) + '1100110011'
        cmd_str = 'memwrite 32 ' + '0x50071110' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = '0000000000000000' + int2bin(agc_ref_pwr, 8) + int2bin(afe_min_gain, 8)
        cmd_str = 'memwrite 32 ' + '0x50071100' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = '0' + int2bin(coarse_sync_iir_bypass, 1) + int2bin(peakpos_finetune, 1) + '0' + \
                int2bin(convex_thres,8) + int2bin(fine_sync_thres, 12) + int2bin(coarse_sync_iir_coef, 8)
        cmd_str = 'memwrite 32 ' + '0x5007111c' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = int2bin(afe_max_gain, 8) + '000000' + int2bin(fine_sync_td_dagc_ref, 18)
        cmd_str = 'memwrite 32 ' + '0x500711e0' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        cmd_val = int2bin(coarse_sync_confnbr, 3) + '00000' + int2bin(notch_alpha_big, 6) + int2bin(notch_alpha_small,6) + int2bin(0, 12)
        cmd_str = 'memwrite 32 ' + '0x50071114' + ' 0x' + '{:x}'.format(int(cmd_val, 2))
        reg_narrow.append(cmd_str + '\r\n')
        
        self.reg_narrow = reg_narrow
        self.sync_ce_tm_enable = sync_ce_tm_enable
        

        
    def cmd_register(self):
        cmd_write = collections.OrderedDict()
        cmd_write['1'] ='1240 0x83fc6a76'
        cmd_write['2'] ='11ac 0x200b0852'
        cmd_write['3'] ='0040 0x73191100'
        cmd_write['4'] ='1110 0x08008333'
        cmd_write['5'] ='1100 0x000036E5'
        cmd_write['6'] ='111c 0x60C05233'
        self.cmd_write = cmd_write
        
    def run(self):
        self.sync_ce_tm_reg_new()#reg_narrow
        if (self.sync_ce_tm_enable==1):
            self.phy_static_para()#add_A000_static_para add_5007_static_para
            self.write_reg_tonemask()#tonemask
        
    