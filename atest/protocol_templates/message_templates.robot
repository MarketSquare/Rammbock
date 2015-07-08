*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      regression
Resource          template_resources.robot


*** Test Cases ***
Using same field name twice fails
    [Setup]    Define Simple Protocol
    New message   Foo    Example
    u8     foo
    u8     bar
    Run keyword and expect error    *     u8    foo

Client uses protocol and sends
    Client Sends simple request    value:0xcafebabe
    Verify server gets hex    0x 01 00 dddd 000c ffff cafebabe

Client uses protocol and receives
    Client sends request and server receives it
    Server Sends simple request    value:0xcafebabe    header:flags:0xffff
    ${msg} =    Client Receives simple request    header:flags:0xffff
    Should be equal    ${msg.value.hex}    0xcafebabe

Server uses protocol and sends
    Client sends request and server receives it
    Server Sends simple request    value:0xcafebabe
    Verify client gets hex    0x 01 00 dddd 000c ffff cafebabe

Server uses protocol and receives
    Client Sends hex    0x 01 00 dddd 000c 0000 cafebabe
    ${msg} =    Server Receives simple request
    Should be equal    ${msg.value.hex}    0xcafebabe

Server uses protocol with header field values and receives
    Client Sends hex    0x 01 00 dddd 000c 0000 cafebabe
    ${msg} =    Server Receives simple request with header    header:messageType:0xdddd
    Should be equal    ${msg.value.hex}    0xcafebabe

Server uses protocol and messages arrive out of order
    Client Sends hex    0x 01 00 aaaa 000c 0000 deadbeef
    Client Sends hex    0x 01 00 dddd 000c 0000 cafebabe
    ${msg_dddd} =    Server Receives simple request with header    header:messageType:0xdddd
    Should be equal    ${msg_dddd._header.messageType.hex}    0xdddd

Message field type conversions
    Client Sends hex    0x 01 00 dddd 000c 0000 000000ff
    ${msg} =    Server Receives simple request    value:0x000000ff
    Should be equal    ${msg.value.hex}    0x000000ff
    Should be equal as integers    ${msg.value.int}    255

Char fields
    Client sends charred request
    ${msg} =    Server receives charred request
    Should be equal    ${msg.string_value.ascii}    foo

Field alignment
    Client sends aligned request    aligned_8bit_field:0xff
    ${msg}=    Server receives aligned request
    Should be equal    ${msg.aligned_8bit_field.hex}    0xff
    Binary should equal hex    ${msg.aligned_8bit_field._raw}    0xff000000

Error when giving non-ascii parameters in header
    Run keyword and expect error    Only ascii characters are supported in parameters.    New message    ValueRequest    Example    header:messägeType:0xdddd

Error when giving non-ascii parameters in pdu fields
    Run keyword and expect error    Only ascii characters are supported in parameters.    Client sends simple request    välyy:0xbebabeba

Resetting message stream cache
    Client sends simple request
    Clear message streams
    Server receive for simple request will timeout

Empty PDU
    New message    ValueRequest    Example    header:messageType:0xdddd
    Client sends message
    ${msg}=    Server receives message
    Should be equal     ${msg._header.messageType.hex}    0xdddd

Non ascii values in chars
    New message    ValueRequest    Example    header:messageType:0xdddd    header:flags:0xffff
    Chars   *      foo
    ${binary} =    Hex to Bin       0xff00feef11616200ffee
    Value          foo          ${binary}
    Client sends message
    ${msg}      Server receives message
    Should be equal     ${msg.foo.ascii}    ab
    Should be equal     ${msg.foo.chars}    ab
    Should be equal     ${msg.foo.bytes}    ${binary}
    Should be equal     ${msg.foo.hex}      0xff00feef11616200ffee

No unread messages should be in client buffer
    ${count}=    Get client unread messages count    client_name=ExampleClient
    Should be equal as integers    ${count}    0

One unread messages should be in client buffer
    Client sends request and server receives it
    Server Sends simple request    value:0xcafebabe    header:flags:0xffff
    Client Sends simple request
    ${count}=    Get client unread messages count    client_name=ExampleClient
    Should be equal as integers    ${count}    1

One unread message should be in server buffer
    Client Sends simple request
    ${count}=    Get server unread messages count    server_name=ExampleServer
    Should be equal as integers    ${count}    1

Two unread message should be in server buffer
    Client Sends simple request
    Client Sends simple request
    ${count}=    Get server unread messages count    server_name=ExampleServer
    Should be equal as integers    ${count}    2

Receive latest
    Client sends request and server receives it
    Server Sends simple request    value:0xf0f0f0f0
    Server Sends simple request    value:0xb0b0b0b0
    Server Sends simple request    value:0xcafebabe
    ${msg}=    Client Receives Message    latest=True
    Should be equal   ${msg.value.hex}     0xcafebabe
    ${count}=    Get client unread messages count    client_name=ExampleClient
    Should be equal as integers    ${count}    2

Receive latest when only one message
    Client Sends simple request
    Server receives message   latest=True

*** Keywords ***
Server receive for simple request will timeout
    Run keyword and expect error    timeout: timed out    Server Receives simple request    timeout=0.1

Server Receives simple request with header
    [Arguments]    @{header params}
    New message    ValueRequest    Example    @{header params}
    u32    value
    ${msg} =    Server receives message    header_filter=messageType
    [Return]    ${msg}

AlignedRequest
    New message    AlignedRequest    Example    header:messageType:0xf000
    u8    aligned_8bit_field    align=4

Client sends aligned request
    [Arguments]    @{params}
    AlignedRequest
    Client sends message    @{params}

Server receives aligned request
    [Arguments]    @{params}
    AlignedRequest
    ${msg}=    Server receives message    @{params}
    [Return]    ${msg}


