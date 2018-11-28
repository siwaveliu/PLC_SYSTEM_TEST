*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_2.1
    run test    tc_2_1

tc_2.1.b0
    run test    tc_2_1_1

tc_2.1.b1
    run test    tc_2_1_2

tc_2.1.b2
    run test    tc_2_1_3

tc_2.1.b3
    run test    tc_2_1_4

tc_2.2
    run test    tc_2_2

tc_2.2.b0
    run test    tc_2_2_band0

tc_2.2.b1
    run test    tc_2_2_band1

tc_2.2.b2
    run test    tc_2_2_band2

tc_2.2.b3
    run test    tc_2_2_band3

tc_2.3
    run test    tc_2_3

tc_2.3_b0
    run test    tc_2_3_b0

tc_2.3_b1
    run test    tc_2_3_b1

tc_2.3_b2
    run test    tc_2_3_b2

tc_2.3_b3
    run test    tc_2_3_b3

tc_2.4
    run test    tc_2_4

tc_2.4.b0
    run test    tc_2_4_0

tc_2.4.b1
    run test    tc_2_4_1

tc_2.4.b2
    run test    tc_2_4_2

tc_2.4.b3
    run test    tc_2_4_3

tc_2.4.loopback
    run test    tc_2_4_loopback

tc_2.5.b0_1mhz
    run test    tc_2_5_band0_1mhz

tc_2.5.b0_8mhz
    run test    tc_2_5_band0_8mhz

tc_2.5.b0_15mhz
    run test    tc_2_5_band0_15mhz

tc_2.5.b1_1mhz
    run test    tc_2_5_band1_1mhz

tc_2.5.b1_3mhz
    run test    tc_2_5_band1_3mhz

tc_2.5.b1_6mhz
    run test    tc_2_5_band1_6mhz

tc_2.5.b2_0p5mhz
    run test    tc_2_5_band2_0p5mhz

tc_2.5.b2_2mhz
    run test    tc_2_5_band2_2mhz

tc_2.5.b2_5mhz
    run test    tc_2_5_band2_5mhz

tc_2.5.b3_1mhz
    run test    tc_2_5_band3_0p5mhz

tc_2.5.b3_3mhz
    run test    tc_2_5_band3_2mhz

tc_2.5.b3_6mhz
    run test    tc_2_5_band3_5mhz

tc_2.6.b0_imp_fs50_1s_iq
    run test    tc_2_6_b0_imp_fs50_1s_iq

tc_2.6.b0_imp_fs50_150ms_iq
    run test    tc_2_6_b0_imp_fs50_150ms_iq

tc_2.6.b1_imp_fs50_1s_iq
    run test    tc_2_6_b1_imp_fs50_1s_iq

tc_2.6.b1_imp_fs50_150ms_iq
    run test    tc_2_6_b1_imp_fs50_150ms_iq

tc_2.6.b2_imp_fs50_1s_iq
    run test    tc_2_6_b2_imp_fs50_1s_iq

tc_2.6.b2_imp_fs50_150ms_iq
    run test    tc_2_6_b2_imp_fs50_150ms_iq

tc_2.6.b3_imp_fs50_1s_iq
    run test    tc_2_6_b3_imp_fs50_1s_iq

tc_2.6.b3_imp_fs50_150ms_iq
    run test    tc_2_6_b3_imp_fs50_150ms_iq

tc_2.100
    [Tags]    STA
    run test    tc_2_100

tc_2.7
    run test    tc_2_7

tc_2.7.b0
    run test    tc_2_7_1

tc_2.7.b1
    run test    tc_2_7_2

tc_2.7.b2
    run test    tc_2_7_3

tc_2.7.b3
    run test    tc_2_7_4
