*** Settings ***
Resource          ../Protocols.robot

*** Keywords ***
Client Sends simple request
    [Arguments]    @{params}
    Simple request
    Client Sends message    @{params}

Client Sends long request
    [Arguments]    @{params}
    Long request
    Client Sends message    @{params}

Server Sends simple request
    [Arguments]    @{params}
    Simple request
    Server Sends message    @{params}

Client Receives simple request
    [Arguments]    @{params}
    New message    ValueRequest    Example
    u32    value
    ${msg} =    Client receives message    @{params}
    [Return]    ${msg}

Server Receives simple request
    [Arguments]    @{params}
    New message    ValueRequest    Example
    u32    value
    ${msg} =    Server receives message    @{params}
    [Return]    ${msg}

Client sends charred request
    [Arguments]    @{params}
    Charred request    foo
    Client sends message    @{params}

Server receives charred request
    [Arguments]    @{params}
    Charred request
    ${msg} =    Server receives message    @{params}
    [Return]    ${msg}

Client sends request and server receives it
    Client Sends simple request
    Verify server gets hex    0x 01 00 dddd 000c ffff deadbeef

Simple request
    New message    ValueRequest    Example    header:messageType:0xdddd    header:flags:0xffff
    u32    value    0xdeadbeef

Long request
    New message    ValueRequest    Example    header:messageType:0xdddd    header:flags:0xffff
    u32    value    0xdeadbeef
    u32    value2    0xdeadbeeb

Charred request
    [Arguments]    ${string_value}=
    New message    CharredRequest    Example    header:messageType:0xf000
    chars    16    string_value      ${string_value}
