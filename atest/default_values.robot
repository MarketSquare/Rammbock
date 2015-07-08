*** Settings ***
Resource          Protocols.robot
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Default Tags        Regression


*** Test cases ***
Client sends server receives
    Client sends     Value ExampleMessage    faa:200
    ${msg}=     Server receives     Value ExampleMessage   faa:200
    Verify message fields    ${msg}

Server sends client receives
    Send first message to server to identify client   #TODO: Implement send to
    Server sends     Value ExampleMessage    faa:200
    ${msg}=     Client receives    Value ExampleMessage   faa:200
    Verify message fields    ${msg}

Default values in get message
     Value ExampleMessage
     ${msg}=      Get message    faa:200
     Verify message fields   ${msg}

Setting a default value for all unset msg fields
    ExampleMessage
    Value      *         0
    ${msg}=    Get message
    Should be equal as integers   0   ${msg.faa.int}
    Should be equal as integers   2   ${msg.bar.int}

Setting a default value for all fields of a subelement
    ComplexMessage
    Value      wonker.id    10
    Value      bonker.id    222
    Value      wonker.*     0
    Value      bonker.*     999
    ${msg}=    Get message
    Should be equal as integers   10   ${msg.wonker.id.int}
    Should be equal as integers   0    ${msg.wonker.price.int}
    Should be equal as integers   222  ${msg.bonker.id.int}
    Should be equal as integers   999  ${msg.bonker.price.int}

Validate with wild cards
    ComplexMessage
    Value      wonker.*     0
    Value      bonker.*     999
    ${msg}=    Get message
    Validate message   ${msg}

Validate with wild cards fails
    ComplexMessage
    Value      wonker.*     0
    Value      bonker.*     999
    ${msg}=    Get message
    Value      bonker.*     1
    Validation of field fails     bonker.id    ${msg}

Default values for header fields
    Client sends     Header value ExampleMessage
    ${msg}=     Server receives     Header value ExampleMessage
    Should be equal    ${msg._header.reserved.hex}    0xff

*** Keywords ***
Validation of field fails
    [Arguments]   ${field}    ${msg}
    Run keyword and expect error   Value of field ${field} does not match *   Validate message   ${msg}

Verify message fields
    [Arguments]   ${msg}
    Should be equal as integers    1    ${msg.foo.int}
    Should be equal as integers    10   ${msg.bar.int}
    Should be equal as integers    200    ${msg.faa.int}

ExampleMessage
    New Message     ExampleMessage    Example    header:messageType:0xbabe
    u16             foo       1
    u8              bar       2
    u8              faa

Value ExampleMessage
    ExampleMessage
    Value           bar      10
    Value           faa      20

Header value ExampleMessage
    Value ExampleMessage
    Value           header:reserved    0xff

ComplexMessage
    New Message     ComplexMessage    Example    header:messageType:0xbabe
    Product        wonker
    Product        bonker

Product
    [Arguments]    ${name}
    New Struct   Product   ${name}
    u32          id
    u32          price
    u32          category
    End struct

Client sends
    [Arguments]    ${message type}   @{params}
    Run keyword    ${message type}
    Client sends message    @{params}

Server sends
    [Arguments]    ${message type}   @{params}
    Run keyword    ${message type}
    Server sends message    @{params}

Server receives
    [Arguments]    ${message type}   @{params}
    Run keyword    ${message type}
    ${msg}=      Server receives message    @{params}
    [Return]     ${msg}

Client receives
    [Arguments]    ${message type}   @{params}
    Run keyword    ${message type}
    ${msg}=      Client receives message    @{params}
    [Return]     ${msg}

Send first message to server to identify client
    Client sends     Value ExampleMessage
    ${msg}=     Server receives     Value ExampleMessage
