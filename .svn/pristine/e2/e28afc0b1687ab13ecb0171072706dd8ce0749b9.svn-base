*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.3.2.1
    [Tags]    CCO
    run test    tc_3_3_2_1

case 3.3.2.2
    [Tags]    CCO
    run test    tc_3_3_2_2

case 3.3.2.3
    [Tags]    CCO
    run test    tc_3_3_2_3

case 3.3.2.4
    [Tags]    STA
    run test    tc_3_3_2_4

case 3.3.2.5
    [Tags]    STA
    run test    tc_3_3_2_5