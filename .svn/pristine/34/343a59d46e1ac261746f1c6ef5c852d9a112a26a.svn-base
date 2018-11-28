import serial
from struct import *
import collections
import time
import math

SITRACE_PORT = 'COM13'
SITRACE_BAUDRATE = 921600/2
band = 1
add_A000_static_para=[]
add_5007_static_para = []
def int2bin(n, count=24):
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])
    
def send_cli_cmd(ser, cmd):
    cmd_len = len(cmd) + 1;
    data = pack('HHBBHL', 0xFACE, 0x10, 0, 0xFF, cmd_len, 0) + cmd + '\x00';
    ser.write(data)

def write_reg_tonemask(tone_mask_file):
    add_5007 = []
    add_base = 0x500710C0
    add_cur = add_base - 4
    strc = ''
    fp_obj = open(tone_mask_file)
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
    return add_5007

def phy_static_para(ValidCarrierNum):
    global add_A000_static_para
    global add_5007_static_para
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

    add_A000_static_para = add_A000
    add_5007_static_para = add_5007
    #logger.info('static para OK')


#######################################################

dut_ser = serial.Serial()
dut_ser.port = SITRACE_PORT
dut_ser.baudrate = SITRACE_BAUDRATE
dut_ser.open()

if band==0:
    ValidCarrierNum = 411;
elif band==1:
    ValidCarrierNum = 131;
elif band==2:
    ValidCarrierNum = 89;
elif band==3:
    ValidCarrierNum = 49;

cmd_write = collections.OrderedDict()
#cmd_write['1'] ='1240 0x83906826'
cmd_write['1'] ='1240 0x83fc6a76'
# 1240: [31] notch_zero_check enable, [30:25]: notch zero thres; [12:4]: fdmeanpwr_start_idx; [3:0]: fdmeanpwr_len
#       [24:18]: fdpwr_start_idx
#       0x83fc6a76: [31]:1, [30:25]:1, [12:4]:167, [3:0]:6, [24:18]: 127
#cmd_write['2'] ='11ac 0x60000854'
cmd_write['2'] ='11ac 0x20080852'
# 11ac, [19]:par check,[18:16]:par; [30]: power saving mode enable; [2:0]: fd_notch_ratio
#       [23]:max2sub check, [22:20]: thres:1.5/2/2.5/3/3.5/4
#cmd_write['3'] ='0040 0x73190100'
cmd_write['3'] ='0040 0x73191100'
# 0040: [12]: sync&ce tone mask mode enable
#cmd_write['4'] ='1110 0x10010333'
cmd_write['4'] ='1110 0x08008333'
# 1110: [31:22]: 1st coarse sync thres; [21:10]: 2nd coarse sync thres
#cmd_write['5'] ='1100 0x000024E5'
cmd_write['5'] ='1100 0x000036E5'
# 1100: [15:8]: agc ref pwr, default 0x24; [7:0]: aft min gain
#cmd_write['6'] ='111c 0x20C05233'
cmd_write['6'] ='111c 0x60C05233'
# 111c: [30]: iir bypass; [29]: 1st fine-sync symbol re-tuned peak position 1024+/-1; [27:20]: convex thres; [19:8]: fine-sync thres; [
#       [7:0]: iir alpha coef
narrow_mask_file = "E:\\lichao\\reg_write\\tonemask_narrow_b1_3m.txt"
tonemask = write_reg_tonemask(narrow_mask_file)
phy_static_para(ValidCarrierNum)

for key in cmd_write:
    send_cli_cmd(dut_ser,'memwrite 32 0x5007'+cmd_write[key]+'\r\n')
    print('memwrite 32 0x5007'+cmd_write[key]+'\r\n')
time.sleep(1)
for cmd in tonemask:
    send_cli_cmd(dut_ser,cmd)
    print(cmd)
time.sleep(2)

for cmd in add_A000_static_para:
    send_cli_cmd(dut_ser,cmd)
    print(cmd)
time.sleep(2)
for cmd in add_5007_static_para:
    send_cli_cmd(dut_ser,cmd)
    print(cmd)
time.sleep(2)

dut_ser.close()