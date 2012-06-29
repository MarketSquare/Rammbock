*** Settings ***
Library    Rammbock
Library    ../message_tools.py
Suite teardown    reset rammbock


*** Variables ***
${SYMMETRIC ACTIVE}=      1
${clock synchronized}=    3


*** Test cases ***
Send and receive NTP message
    [tags]
    Define NTP protocol
    New message    NTP    time request
    Datetime value    Origin timestamp    Sep 27, 2004 06:18:04.922896000
    client sends binary
    server receives binary


*** Keywords ***
Define NTP protocol
    New protocol    NTP
    Flags
    u8    Peer clock stratum        0
    u8    Peer polling Interval     10
    i8    Peer clock precision     -20        #signed integer
    i32   Root delay                0.0303    #signed fixed-point number
    i32   Root dispersion           0.1855    #signed fixed-point number
    IP    Reference id              192.168.0.1
    Datetime   Reference timestamp       Sep 27, 2004 05:29:41.259040000
    Datetime   Origin timestamp          Sep 27, 2004 06:18:04.922896000
    Datetime   Receive timestamp         Sep 27, 2004 06:18:03.821123000
    Datetime   Transmit timestamp        Sep 27, 2004 06:18:03.821133000
    end protocol

Flags
    new binary container    Flags
    bin    2    Leap indicator    ${clock synchronized}
    bin    3    Version number    3
    bin    3    Mode              ${SYMMETRIC ACTIVE}
    end binary container

Datetime
    [arguments]    ${name}    ${datetime}
    ${converted}=    Convert datetime to NTP integer    ${datetime}
    u64    ${name}    ${converted}

Datetime value
    [arguments]    ${name}    ${datetime}
    ${converted}=    Convert datetime to 8 byte NTP integer    ${datetime}
    Value     ${name}    ${converted}

IP
    [arguments]    ${name}    ${value}
    ${converted}=    Convert to IP    ${value}
    u32    ${name}    ${converted}
