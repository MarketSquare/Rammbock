*** Settings ***
Library           Rammbock
Suite setup       Define protocol
Suite teardown    Reset Rammbock
Resource    Protocols.robot
Default tags    Regression

*** Test Cases ***
Get message with chars and end byte
    Message with chars and end byte    0x00
    ${msg}    get message    arbitrary_length:foo.bar.zig
    Should be equal    foo.bar.zig    ${msg.arbitrary_length.ascii}
    should be equal as integers   12    ${msg.arbitrary_length.len}

Get message with chars and end byte long termination
    Message with chars and end byte    0x0d0a
    ${msg}    get message    arbitrary_length:foo.bar.zig
    Should be equal    foo.bar.zig    ${msg.arbitrary_length.ascii}
    Should be equal as strings    foo.bar.zig\r\n    ${msg.arbitrary_length._raw}
    should be equal as integers   13    ${msg.arbitrary_length.len}

Send and receive message with chars with end byte
    [tags]
    Setup TCP server and client     Test
    Message with chars and end byte      0x0d0a
    Client sends message    arbitrary_length:foo.bar.zig
    ${msg}=    Server receives message
    Should be equal    foo.bar.zig    ${msg.arbitrary_length.ascii}
    should be equal as integers   13    ${msg.arbitrary_length.len}

*** Keywords ***
Define protocol
    new protocol    Test
    u8    length
    pdu   length-1
    end protocol

Message with chars and end byte
    [Arguments]    ${terminator}
    new message    ExampleMessage    Test
    chars    *    arbitrary_length    ${none}    terminator=${terminator}
    uint    8     some_integer    0x00
