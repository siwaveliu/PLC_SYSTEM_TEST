# coding=utf-8
METER_PORT = 'COM4'
METER_BAUDRATE = 2400

TEST_PORT = 'COM4'
TEST_PORT_BAUDRATE = 115200

CONCENTRATOR_PORT = 'COM5'  # type: str
CONCENTRATOR_BAUDRATE = 9600  # type: int

CONCENTRATOR_OTHER_PORT = 'COM3' # type: str

TB_PORT = 'COM6'
TB_BAUDRATE = 460800

TB_SITRACE_PORT = 'COM27'
TB_SITRACE_BAUDRATE = 921600

DUT_SITRACE_PORT = 'COM26'
DUT_SITRACE_BAUDRATE = 921600

FADDING_PORT = 'COM1'
FADDING = 9600

SIGGEN_ADDR = '192.168.55.245'  #5182B
#SIGGEN_ADDR = '192.168.55.247' #4438C

SCOPE_IP = '192.168.55.246'

DUT_JLINK_SN = '59400978'
TB_JLINK_SN = '269200585'

JLINK_PATH = "D:/jlink/JLink_V612a/JLink.exe"

SITRACE_PATH = r"D:\svn\sources\SIWP9006\plc_system_test\venv\Scripts\SiTrace.exe"

SIMUCCT = u"C:/D/plc_system_test/tc/tc_iot_4/SimulatedConcentrator/"

#SIWP9006
DEVICE="Cortex-M0"
#PZ6806L
#DEVICE="STM32F103ZE"
#SIWP9006F
#DEVICE="Cortex-M3"

# DUT's clock is 1 times slower than the normal
# i.e. It takes PC 2 seconds while it elapses only 1 second by DUT side 
CLOCK_RATE = 1
# DUT's clock is same as the normal
#CLOCK_RATE = 1

SOF_VERSION = 100 
#50M or 100M
RF_SOURCE = 0
#SIG SOURCE from RF or NOT ///only for narrow or burst
AUTO_RESET = False

AUTO_LOG = False

PHY_AUTO_TEST = False
# afe type: 0: atheros  1:weile
TB_AFE_TYPE = 0
DUT_AFE_TYPE = 0

# single device test
TB_STANDALONE = 1

#option:5m 2m 0p5m 6m 3m 15m 8m 1m
NARROW_SOURCE = '6m' 

TB_MPW = 1
DUT_SIWAVE = False

if DUT_SIWAVE==False:
    PHY_AUTO_TEST = False

DEFAULT_BAND = 1

IOT_TOP_LIST_PROXY = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_代理'
IOT_TOP_LIST_DYNATIC = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_动态'
IOT_TOP_LIST_STATIC = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_静态'
IOT_TOP_LIST_ALL = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_所有'
IOT_TOP_LIST_TESTED = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_待测'
IOT_TOP_LIST_ESCORT = u'tc/tc_iot_4/addrlist/互操作性表架拓扑地址_陪测'

# TB can not be Reset, so add win-serial for reset
#TB_RESET_PORT = 'COM22'
#TB_RESET_BAUDRATE = 9600