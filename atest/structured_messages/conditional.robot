*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Resource          ../Protocols.robot
Default Tags      Regression


*** Test Cases ***
Simple conditional message
    Conditional message
    Client sends message
    ${msg}=    Server receives message
    Should not be true    ${msg.conditional.exists}

Simple conditional message has element
    Conditional message
    Client sends message    condition:1
    ${msg}=    Server receives message   condition:1
    Should be true    ${msg.conditional.exists}
    Should be equal as integers    ${msg.conditional.element}    42

Condition in Struct
    Conditional message
    Client sends message
    ${msg}=    Server receives message
    Should be true    ${msg.conditional2.exists}
    Should be equal as integers    ${msg.conditional2.element}    24

Validating simple conditional message has element fails
    Conditional message
    Client sends message    condition:1
    Run keyword and expect error    Value of field*    Server receives message   condition:1    conditional.element:52



*** Keywords ***
Conditional message
    New message    ConditionalExample    Example    header:messageType:0xb0b0
    u8    condition    0
    New Struct    elem    struct
    u8    cond_in_struct   5
    End Struct
    Conditional    condition == 1    conditional
    u8    element    42
    end conditional
    Conditional    struct.cond_in_struct == 5    conditional2
    u8    element    24
    end conditional
