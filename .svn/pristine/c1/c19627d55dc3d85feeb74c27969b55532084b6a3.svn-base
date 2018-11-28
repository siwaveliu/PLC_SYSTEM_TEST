*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem    #Test Setup    Run Keywords    Open tb test port    #Test Teardown    Run Keywords    Close test port
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.2.6.1
    [Tags]    CCO
    run test    tc_3_2_6_1

case 3.2.6.2
    [Tags]    CCO
    run test    tc_3_2_6_2

case 3.2.6.3
    [Tags]    STA
    run test    tc_3_2_6_3

case 3.2.6.4
    [Tags]    STA
    run test    tc_3_2_6_4

case 3.2.6.5
    [Tags]    STA
    run test    tc_3_2_6_5

case 3.2.6.6
    [Tags]    STA
    run test    tc_3_2_6_6

case 3.2.6.7
    [Tags]    STA
    run test    tc_3_2_6_7

case 3.2.6.50
    [Tags]    CCO
    run test    tc_3_2_6_50
  

