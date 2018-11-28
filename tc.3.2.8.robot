*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem    #Test Setup    Run Keywords    Open tb test port    #Test Teardown    Run Keywords    Close test port
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.2.8.1
    [Tags]    CCO
    run test    tc_3_2_8_1

case 3.2.8.2
    [Tags]    STA
    run test    tc_3_2_8_2

case 3.2.8.3
    [Tags]    STA
    run test    tc_3_2_8_3
case 3.2.8.4
    [Tags]    STA
    run test    tc_3_2_8_4    
