*** Settings ***
Resource    ../Protocols.robot
Test teardown    Teardown rammbock and increment port numbers
Default tags    regression


*** Test cases ***
encode signed integer
    Define example protocol
    Start TCP client    ${SERVER}    ${SERVER PORT}    name=ExampleServer   protocol=Example
    Create message with signed integer fields
    ${msg}=    Get Message    foo:-72
    should be equal as integers    -72     ${msg.foo.sint}
    should be equal as integers    -128    ${msg.bar.sint}
    should be equal as integers     127    ${msg.zig.sint}
    should be equal as integers    -43     ${msg.baz.sint}
    should be equal as integers     43     ${msg.dar.sint}
    should be equal as integers     0      ${msg.wad.sint}

Signed integer fields should give warning when encoding if integer over range
    Define example protocol
    Start TCP client    ${SERVER}    ${SERVER PORT}    name=ExampleServer   protocol=Example
    Create message with signed integer fields
    run keyword and expect error    Value -129 out of range (-128..127)    get message    foo:-129
    Create message with signed integer fields
    run keyword and expect error    Value 128 out of range (-128..127)    get message    foo:128
    Create message with signed integer fields
    run keyword and expect error    Value 289 out of range (-128..127)    get message    foo:289
    Create message with signed integer fields
    run keyword and expect error    Value -258 out of range (-128..127)    get message    foo:-258

encode signed integer with alignment
    Define example protocol
    Start TCP client    ${SERVER}    ${SERVER PORT}    name=ExampleServer   protocol=Example
    Create message with aligned signed integer fields
    ${msg}=    Get Message
    should be equal as integers    -46    ${msg.baz.int}
    should be equal as integers     32    ${msg.dar.int}

send and receive message with signed integer
    Setup protocol, TCP server, and client
    Create message with signed integer fields
    client sends message    foo:-21
    ${msg}=    server receives message    foo:-21
    should be equal as integers    -21    ${msg.foo.int}

*** Keywords ***
Create message with signed integer fields
    new message    ExampleMessage    Example    header:messageType:0x00
    int    1    foo
    int    1    bar     -128
    int    1    zig    127
    int    1    baz    -43
    int    1    dar    43
    int    1    qiz    -43
    int    1    wad    0

Create message with aligned signed integer fields
    new message    ExampleMessage    Example    header:messageType:0x00
    int    2    baz    -46    align=4
    int    2    dar     32    align=4

