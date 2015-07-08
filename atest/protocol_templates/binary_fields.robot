*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      regression
Resource          ../Protocols.robot

*** Test Cases ***
Binary field encoding
    [Setup]    Define example protocol
    Binary Message
    ${msg}=   get message
    Should be equal   ${msg.flags.nextFour.bin}    0b1010

Binary field decoding
    Binary Message
    Client sends message
    ${msg}=   Server receives message
    Should be equal   ${msg.flags.firstTwo.hex}                0x03
    Should be equal   ${msg.flags.nextFour.bin}                0b1010
    Should be equal as integers   ${msg.flags.lastTen.int}     0

Binary fields must be aligned
    [Setup]    Define example protocol
    New message   Foo    Example   header:messageType:0xdddd
    New Binary Container    flags
    Bin  2   firstTwo    0b11
    Bin  4   nextFour    0b1010
    Bin  11  lastTen     0
    Run keyword and expect error    *    End Binary Container

*** Keywords ***
Binary Message
    New message   Foo    Example    header:messageType:0xdddd
    New Binary Container    flags
    Bin  2   firstTwo    0b11
    Bin  4   nextFour    0b1010
    Bin  10  lastTen     0b00
    End Binary Container
