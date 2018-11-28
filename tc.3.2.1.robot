*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_3.2.1.1
    [Tags]    CCO
    run test    tc_3_2_1_1

tc_3.2.1.2
    [Tags]    CCO
    run test    tc_3_2_1_2

tc_3.2.1.3
    [Tags]    CCO
    run test    tc_3_2_1_3

tc_3.2.1.4
    [Tags]    CCO
    run test    tc_3_2_1_4

tc_3.2.1.5
    [Tags]    STA
    run test    tc_3_2_1_5

tc_3.2.1.6
    [Tags]    STA
    run test    tc_3_2_1_6
