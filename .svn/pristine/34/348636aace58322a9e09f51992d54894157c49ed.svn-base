*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_3.2.2.1
    [Tags]    CCO
    run test    tc_3_2_2_1

tc_3.2.2.2
    [Tags]    STA
    run test    tc_3_2_2_2


