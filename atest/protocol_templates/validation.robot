*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      regression
Resource          template_resources.robot

*** Test Cases ***
UDP Server uses protocol and receives with pattern validation
    Client Sends hex    0x 01 00 dddd 000c 0000 00000005
    ${msg} =    Server Receives simple request    value:(4|5)
    Should be equal    ${msg.value.hex}    0x00000005

TCP server uses protocol and receives with pattern validation
    [Setup]    Setup protocol, TCP server, and client
    Client Sends simple request    header:flags:0xffff
    Server Receives simple request    header:flags:0xffff

TCP server receives from two clients with pattern validation
    [Setup]    Define protocol, start tcp server and two clients    Example
    Named client sends simple request    ExampleClient1    value:0xcafebabe
    Named client sends simple request    ExampleClient2    value:0xdeadbeef
    Server Receives simple request from named connection    Connection2    value:0xdeadbeef
    Server Receives simple request from named connection    Connection1    value:0xcafebabe

Server uses protocol and receives with pattern validation failing
    Client Sends hex    0x 01 00 dddd 000c 0000 00000005
    Run keyword and expect error    Value of field 'value' does not match *    Server Receives simple request    value:(4|6)

Server uses protocol and value validation fails
    Client Sends hex    0x 01 00 dddd 000c 0000 cafebabe
    Run keyword and expect error    Value of field value does not match *    Server Receives simple request    value:0xffffff

Char field validation passes
    Client sends charred request
    ${msg} =    Server receives charred request    string_value:foo
    Should be equal    ${msg.string_value.ascii}    foo

Char field validation fails
    Client sends charred request
    Run keyword and expect error    Value of field string_value does not match *    Server receives charred request    string_value:bar

Char field validation passes with pattern
    Client sends charred request
    ${msg} =    Server receives charred request    string_value:(bar|foo)
    Should be equal    ${msg.string_value.ascii}    foo

Server receive and validate separately
    Client Sends simple request
    ${msg}=    Server receives without validation
    Validate message    ${msg}

Client receive and validate separately
    Client sends request and server receives it
    Server Sends simple request
    ${msg}=    Client receives without validation
    Validate message    ${msg}

Client receive and validate fails
    Client sends request and server receives it
    Server Sends simple request
    ${msg}=    Client receives without validation
    Validation fails    ${msg}    Value of field value does not match*    value:0xfeedd00d

Server receive and validate fails
    Client sends simple request
    ${msg}=    Server receives without validation
    Validation fails    ${msg}    Value of field value does not match*    value:0xfeedd00d

Validate fails when trying to validate nonexistent field
    Client sends simple request
    ${msg}=    Server receives without validation
    Validation fails    ${msg}    Unknown fields in 'ValueRequest': foo:0xfeedd00d    foo:0xfeedd00d

Validate fails when values set as integers instead of strings
    Client sends simple request
    Value     value    ${1}
    ${msg}=    Server receives without validation
    Validation fails    ${msg}    AttributeError: Validating value:1 failed. 'int' object has no attribute 'startswith'.\n \ \ \ \ Did you set default value as numeric object instead of string?

Receiving should fail if message too long
    Client sends long request
    Server expects shorter request
    Receiving message fails because there is extra data

Validating header field fails
    Client Sends hex    0x 01 00 dddd 000c cafe 00000005
    Run keyword and expect error    Value of field Example.flags does not match 0xcafe!=0x0000    Server Receives simple request

Validating header fields
    Client Sends hex    0x 02 03 eeee 000c cafe 00000005
    Server Receives simple request
    ...    header:version:0x02
    ...    header:reserved:0x03
    ...    header:messageType:0xeeee
    ...    header:length:0x000c
    ...    header:flags:0xcafe

Validating header field by applying mask to value
    Client Sends hex    0x 02 03 eeee 000c cafe 00000005
    Server Receives simple request
    ...    header:version:0x02
    ...    header:reserved:0x03
    ...    header:messageType:0xeeee
    ...    header:length:0x000c
    ...    header:flags:(0xfafa&0x0ff0)

Validating pdu field by applying mask to value
    Client Sends hex    0x 01 00 dddd 000c 0000 12345678
    ${msg} =    Server Receives simple request    value:(0x12645678 & 0xff0fffff)
    Should be equal    ${msg.value.hex}    0x12345678

Validating pdu field by applying mask to value fails
    Client Sends hex    0x 01 00 dddd 000c 0000 12345678
    Run keyword and expect error    Value of field 'value' does not match pattern '0x12345678!=(0x12645678 & 0xffff0fff)'    Server Receives simple request    value:(0x12645678 & 0xffff0fff)


*** Keywords ***
Named client sends simple request
    [Arguments]    ${client}=    @{params}
    New message    ValueRequest    Example    header:messageType:0xdddd
    u32    value    0xdeadbeef
    Client Sends message    name=${client}    @{params}

Server Receives simple request from named connection
    [Arguments]    ${connection}=    @{params}
    New message    ValueRequest    Example
    u32    value
    ${msg} =    Server receives message    alias=${connection}    @{params}
    [Return]    ${msg}

Validation fails
    [Arguments]    ${msg}    ${error}    @{parameters}
    Run keyword and expect error    ${error}    Validate message    ${msg}    @{parameters}

Server expects shorter request
    New message    shorter message    Example
    u32    value    0xdeadbeef

Receiving message fails because there is extra data
    Run keyword and expect error    Received 'shorter message', message too long. Expected 4 but got 8
    ...    Server receives message

