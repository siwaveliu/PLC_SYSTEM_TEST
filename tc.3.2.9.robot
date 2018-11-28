*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem    #Test Setup    Run Keywords    Open tb test port    #Test Teardown    Run Keywords    Close test port
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.2.9.1
    [Tags]    CCO
    run test    tc_3_2_9_1

case 3.2.9.2
    [Tags]    CCO
    run test    tc_3_2_9_2

case 3.2.9.3
    [Tags]    CCO
    run test    tc_3_2_9_3

case 3.2.9.4
    [Tags]    CCO
    run test    tc_3_2_9_4

case 3.2.9.5
    [Tags]    CCO
    run test    tc_3_2_9_5

case 3.2.9.6
    [Tags]    CCO
    run test    tc_3_2_9_6

case 3.2.9.7
    [Tags]    STA
    run test    tc_3_2_9_7

case 3.2.9.8
    [Tags]    STA
    run test    tc_3_2_9_8
