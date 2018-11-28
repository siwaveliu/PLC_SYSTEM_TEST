*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem    #Test Setup    Run Keywords    Open tb test port    #Test Teardown    Run Keywords    Close test port
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.2.11.1
    [Tags]    CCO
    run test    tc_3_2_11_1

case 3.2.11.2
    [Tags]    CCO
    run test    tc_3_2_11_2

case 3.2.11.3
    [Tags]    CCO
    run test    tc_3_2_11_3

case 3.2.11.4
    [Tags]    STA
    run test    tc_3_2_11_4

case 3.2.11.5
    [Tags]    STA
    run test    tc_3_2_11_5

case 3.2.11.6
    [Tags]    STA
    run test    tc_3_2_11_6

case 3.2.11.7
    [Tags]    STA
    run test    tc_3_2_11_7

case 3.2.11.8
    [Tags]    STA
    run test    tc_3_2_11_8

case 3.2.11.9
    [Tags]    STA
    run test    tc_3_2_11_9

case 3.2.11.10
    [Tags]    STA
    run test    tc_3_2_11_10

case 3.2.11.11
    [Tags]    STA
    run test    tc_3_2_11_11

case 3.2.11.12
    [Tags]    STA
    run test    tc_3_2_11_12

case 3.2.11.13
    [Tags]    STA
    run test    tc_3_2_11_13

case 3.2.11.14
    [Tags]    STA
    run test    tc_3_2_11_14

case 3.2.11.15
    [Tags]    STA
    run test    tc_3_2_11_15

case 3.2.11.16
    [Tags]    STA
    run test    tc_3_2_11_16
