*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      regression
Resource          template_resources.robot

*** Test Cases ***
Define And Use A Message Template
    [Setup]    Define Simple Protocol
    Start TCP Client  protocol=Example

Undefined protocol cannot be used
    [Setup]    Define Simple Protocol
    Should fail    Start TCP Client    protocol=Invalid

Access header
    Client Sends hex    0x 01 00 dddd 000c 0000 000000ff
    ${msg} =    Server Receives simple request
    Should be equal    ${msg._header.version.hex}    0x01
    Should be equal as integers    ${msg._header.length.int}    12

Starting new protocol in middle of old protocol definition fails
    New Protocol    foo
    Should fail    new protocol    bar

Redifining protocol fails
    New Protocol    foo
    uint    1    length
    pdu    length
    end protocol
    Should fail    new protocol   foo

Defining message while defining protocol fails
    New Protocol    foo
    Should fail    new message    foo

Overriding header parameters in send
    Client sends simple request    header:flags:0xcafe
    ${msg}=    Server receives simple request    header:flags:0xcafe
    Should be equal    0xcafe    ${msg._header.flags.hex}

Getting protocol name from client
    ${protocol}     get client protocol
    Should be equal    ${protocol}     Example

Protocol with fixed pdu length
    [Setup]         Define simple protocol
    New Message     Ploo    Example
    u16  first     0xcafe
    u16  second    0xd00d
    ${msg}   Get message
    Should be equal    ${msg.first.hex}   0xcafe

Protocol without PDU
    New Protocol   NoPDU
    u8  field  16
    End Protocol
    New message    message   protocol=NoPDU
    ${msg}  Get message     field:4
    Should be equal as integers     ${msg.field}    4

Protocol without PDU and dynamic length
    New protocol   noPDUDymagic
    u16  length
    u16  id     16
    Chars  length - 4   text
    End protocol
    New message    message   protocol=noPDUDymagic
    ${msg}    Get message    text:hello
    Should be equal as integers     ${msg.length}        9
    Should be equal as integers     ${msg.text.len}      5

Send and receive protocol without PDU
    [Setup]  New Protocol   NoPDU
    u8  field  16
    End Protocol
    New message    message   protocol=NoPDU
    Setup TCP server and client     NoPDU
    Client sends message    field:42
    ${msg}  Server receives message     field:42
    Should be equal as integers     ${msg.field}    42

Send and receive protocol with fixed PDU on TCP
    [Setup]  Define simple protocol
    Setup TCP server and client     Example
    New message   message   protocol=Example
    u32    field     42
    Client sends message
    ${msg}  Server receives message
    Should be equal as integers     ${msg.field}    42

Protocol with fields after PDU fail
    New Protocol   Failing
    u8  field  16
    pdu   1
    Should fail  u8   second_field   16

Protocol with several PDU fields fails
    New Protocol   Failing
    u8  field  16
    pdu   1
    Should fail   pdu    1

Node protocol and template protocol must be equal
    Define example protocol     FirstProtocol
    Define example protocol     SecondProtocol
    Setup TCP server and client  FirstProtocol
    Simple Request with 'SecondProtocol'
    Client sends message
    Run keyword and expect error    Template protocol *    Server receives message

Structured field in protocol header
    new protocol    example
    new Struct   Type   name
    u8    field    16
    end struct
    end protocol
    new message    message    protocol=example
    ${msg}=    get message
    should be equal as integers    16    ${msg.name.field.int}


*** Keywords ***
Simple Request with '${protocol}'
    New message    ValueRequest    ${protocol}    header:messageType:0xdddd    header:flags:0xffff
    u32    value    0xdeadbeef
