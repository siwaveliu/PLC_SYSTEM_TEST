*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem    #Test Setup    Run Keywords    Open tb test port    #Test Teardown    Run Keywords    Close test port
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.2.10.1
    [Tags]    CCO
    run test    tc_3_2_10_1

case 3.2.10.2
    [Tags]    CCO
    run test    tc_3_2_10_2

case 3.2.10.3
    [Tags]    CCO
    run test    tc_3_2_10_3

case 3.2.10.4
    [Tags]    CCO
    run test    tc_3_2_10_4

case 3.2.10.5
    [Tags]    CCO
    run test    tc_3_2_10_5

case 3.2.10.6
    [Tags]    STA
    run test    tc_3_2_10_6

case 3.2.10.7
    [Tags]    STA
    run test    tc_3_2_10_7

case 3.2.10.8
    [Tags]    STA
    run test    tc_3_2_10_8

case 3.2.10.9
    [Tags]    STA
    run test    tc_3_2_10_9

case 3.2.10.10
    [Tags]    STA
    run test    tc_3_2_10_10

