*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test Teardown     Teardown rammbock and increment port numbers
Resource          Protocols.robot
Library           OperatingSystem

*** Test Cases ***
Seqdiag diagram
    [tags]    seqdiag
    New message    ValueRequest    Example    header:messageType:0
    u32    value    0
    Client sends message
    Server receives message
    Embed seqdiag sequence
    Sequence diagram should exist

*** Keywords ***
Sequence diagram should exist
    File Should exist    ${OUTPUT DIR}${/}${TEST NAME}.seqdiag.png
    [Teardown]    Remove sequence diagram

Remove Sequence diagram
    Remove file     ${OUTPUT DIR}${/}${TEST NAME}.seqdiag.png
