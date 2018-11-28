*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.3.4.1
    [Tags]    CCO
    run test    tc_3_3_4_1

case 3.3.4.2
    [Tags]    CCO
    run test    tc_3_3_4_2

case 3.3.4.3
    [Tags]    STA
    run test    tc_3_3_4_3

case 3.3.4.4
    [Tags]    STA
    run test    tc_3_3_4_4

case 3.3.4.5
    [Tags]    STA
    run test    tc_3_3_4_5