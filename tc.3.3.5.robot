*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
case 3.3.5.1
    [Tags]    CCO
    run test    tc_3_3_5_1

case 3.3.5.2
    [Tags]    STA
    run test    tc_3_3_5_2