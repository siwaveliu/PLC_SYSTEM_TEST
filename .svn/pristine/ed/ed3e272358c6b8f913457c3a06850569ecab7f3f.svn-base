*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_3.2.3.1
    [Tags]    CCO
    run test    tc_3_2_3_1
tc_3.2.3.2
    [Tags]    CCO
    run test    tc_3_2_3_2
tc_3.2.3.3
    [Tags]    STA
    run test    tc_3_2_3_3
tc_3.2.3.4
    [Tags]    STA
    run test    tc_3_2_3_4


