*** Settings ***
Resource        ../Protocols.robot
Library    Rammbock
Library     my_handler.py
Library   OperatingSystem

*** Variables ***
${SIGNAL FILE}=   ${TEMPDIR}${/}.rammbock_background_signal

*** Keywords ***
Define Templates
    Define sample template
    Define another template
    Define sample response template
Define sample template
    New Message     sample  Example     header:messageType:0x0042
    u16     foo     1
    Save Template   sample
Define another template
    New Message     another  Example     header:messageType:0x00ab
    u16     foo     100
    u16     eoo      500
    Save Template   another
Define sample response template
    New Message     sample_response  Example     header:messageType:0x0011
    u16     bar     100
    Save Template   sample response
Handler should have been called with '${count}' sample messages
    ${rcvd msgs}   Get rcvd msg
    Length should be   ${rcvd_msgs}     ${count}
    ${msg}=    Set variable   ${rcvd msgs[0]}
    Should be equal   ${msg._header.messageType.hex}     0x0042
Handler should have been called with '${count}' another messages
    ${rcvd msgs}   Get rcvd msg
    Length should be   ${rcvd_msgs}     ${count}
    ${msg}=    Set variable   ${rcvd msgs[0]}
    Should be equal   ${msg._header.messageType.hex}     0x00ab
Handler should have been called with '${count}' times with logging
    Log handler messages
    Reset handler messages
    Handler should have been called with '${count}' times
Handler should have been called with '${count}' times
    ${rcvd msgs}   Get rcvd msg
    Length should be   ${rcvd_msgs}     ${count}

