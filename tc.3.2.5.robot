*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_3.2.5.1
    [Tags]    CCO
    run test    tc_3_2_5_1
tc_3.2.5.2
    [Tags]    CCO
    run test    tc_3_2_5_2
tc_3.2.5.3
    [Tags]    CCO
    run test    tc_3_2_5_3

tc_3.2.5.4
    [Tags]    CCO
    run test    tc_3_2_5_4

tc_3.2.5.5
    [Tags]    CCO
    run test    tc_3_2_5_5

tc_3.2.5.6
    [Tags]    STA
    run test    tc_3_2_5_6

tc_3.2.5.7
    [Tags]    STA
    run test    tc_3_2_5_7

tc_3.2.5.8
    [Tags]    STA
    run test    tc_3_2_5_8

tc_3.2.5.9
    [Tags]    STA
    run test    tc_3_2_5_9

tc_3.2.5.10
    [Tags]    STA
    run test    tc_3_2_5_10
