*** Settings ***
Test Setup        Init Test
Test Teardown     Record Test Status
Library           OperatingSystem
Library           Process
Library           plc_tb_ctrl.py
Library           plc_tb_ctrl.PlcSystemTestbench

*** Test Cases ***
tc_4.1
    run iot test    tc_4_1

tc_4.2
    run iot test    tc_4_2

tc_4.3
    run iot test    tc_4_3

tc_4.4
    run iot test    tc_4_4

tc_4.5
    run iot test    tc_4_5

tc_4.6
    run iot test    tc_4_6

tc_4.7
    run iot test    tc_4_7

tc_4.8
    run iot test    tc_4_8

tc_4.9
    run iot test    tc_4_9

tc_4.10
    run iot test    tc_4_10
