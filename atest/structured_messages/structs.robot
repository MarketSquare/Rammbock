*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Resource          ../Protocols.robot
Default Tags      Regression

*** Variables ***
${HEADER} =    0x0100aaaa000f0000

*** Test Cases ***
Message with struct
    Client sends request with struct     pair.first:0xba   pair.second:0xbe
    ${msg} =    Server receives request with struct
    Should be equal    ${msg.pair.first.hex}     0xba
    Should be equal    ${msg.pair.second.hex}    0xbe

Validate with struct
    Client sends request with struct     pair.first:0xba   pair.second:0xbe
    Server receives request with struct    pair.first:0xba

Fail validation with struct
    Client sends request with struct     pair.first:0xba   pair.second:0xbe
    Server should fail validation with struct    pair.first:0xff

Reuse struct in another message
    Message with struct     42
    ${struct_msg} =    Get message
    Message with struct     1
    Value       pair     ${struct_msg.pair}
    ${pair_msg} =    Get message
    Should be equal as integers    ${pair msg.pair.first.int}     42

Reuse complex struct in another message
    Message with struct in struct
    value       structstruct.mollyMalones.name      Molly
    value       structstruct.mollyMalones.closesAt  8
    value       structstruct.foo        42
    ${msg} =    Get message
    Message with struct in struct
    value       structstruct.mollyMalones.name      ThisWillBeOverRidden
    value       structstruct    ${msg.structstruct}
    ${new_msg} =    Get message
    Should be equal    ${new_msg.structstruct.mollyMalones.name.ascii}     Molly
    Should be equal as integers    ${new_msg.structstruct.foo.int}     42
    Should be equal as integers    ${new_msg.structstruct.mollyMalones.closesAt.int}     8

Struct containing struct
    Client sends struct with struct   structstruct.mollyMalones.closesAt:4
    ${msg} =    Server Receives struct with struct  structstruct.mollyMalones.closesAt:
    Should be equal as integers   ${msg.structstruct.mollyMalones.closesAt.int}   4

Unfinished struct fails
    New message   ExampleMessage   Example   header:messageType:0xbabe
    New Struct  MyStruct  myStruct
    u8    foo
    Get message fails because 'myStruct' is not completed

Pass value dict to Struct
   New message   FooExample   Example    header:messageType:0xb0b0
   define struct    first:1    second:2
   ${msg}   Get message
   Should be equal     ${msg.fooName.first.hex}    0x01
   Should be equal     ${msg.fooName.second.hex}   0x02
   Should be equal     ${msg.fooName.third.hex}    0xff

Pass value dict to Struct but replace it in Get Message
   New message   FooExample   Example    header:messageType:0xb0b0
   define struct    first:1    second:2
   ${msg}   Get message    fooName.second:0x22
   Should be equal     ${msg.fooName.first.hex}    0x01
   Should be equal     ${msg.fooName.second.hex}   0x22
   Should be equal     ${msg.fooName.third.hex}    0xff

Get full path in missing fields
    Message with struct in struct
    Value        structstruct.mollyMalones.closesAt     ${EMPTY}
    Run keyword and expect error    Value of structstruct.mollyMalones.closesAt not set    Get message

Get full path when validating
    Client sends struct with struct   structstruct.mollyMalones.closesAt:4
    Run keyword and expect error    Value of field structstruct.mollyMalones.closesAt does not match 0x04!=9    Server Receives struct with struct  structstruct.mollyMalones.closesAt:9

Get full path when validating against a pattern
    Client sends struct with struct   structstruct.mollyMalones.closesAt:4
    Run keyword and expect error    Value of field 'structstruct.mollyMalones.closesAt' does not match pattern '0x04!=(0|1|2)'    Server Receives struct with struct  structstruct.mollyMalones.closesAt:(0|1|2)

Reuse struct in header fields vith value
    [Setup]    Setup protocol with struct in header, udp server and client
    Message with struct in header     header:receiver.board:0xcafe    header:receiver.process:0xbabe
    ${msg}=    Get message
    Message with struct in header
    Value    header:receiver    ${msg._header.receiver}
    ${msg reusing receiver}=    Get message
    Should be equal    ${msg reusing receiver._header.receiver.board.hex}    0xcafe
    Should be equal    ${msg reusing receiver._header.receiver.process.hex}    0xbabe

*** Keywords ***
Client sends request with struct
    [Arguments]    @{params}
    Message with struct
    Client sends message   @{params}

Client sends struct with struct
    [Arguments]    @{params}
    Message with struct in struct
    Client sends message   @{params}

Server receives request with struct
    [Arguments]    @{params}
    Message with struct
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Server Receives struct with struct
    [Arguments]    @{params}
    Message with struct in struct
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Server should fail validation with struct
    [Arguments]    @{params}
    Run keyword and expect error     Value of field pair.first does not *    Server receives request with struct    @{params}

Message with struct
    [arguments]    ${pair values}=
    New Message    StructRequest  Example    header:messageType:0xaaaa
    Pair    pair   ${pair values}

Pair
    [arguments]     ${name}=     ${value}=
    New Struct    Pair    ${name}
    u8    first       ${value}
    u8    second      ${value}
    End struct

Message with struct in struct
    New Message   StructStruct   Example    header:messageType:0xaaaa
    StructStruct   structstruct

StructStruct
    [Arguments]    ${name}
    New Struct   StructStruct   ${name}
    u32      foo    6
    Bar      mollyMalones
    End struct

Bar
    [Arguments]    ${name}
    New Struct   Bar   ${name}
    Chars     20        name       Progress Bar
    u8        opensAt    10
    u8        closesAt    2
    End struct

Get message fails because '${name}' is not completed
    Run keyword and expect error   Message definition not complete. ${name} not completed.  Get message

define struct
   [arguments]     @{params}
   New Struct    FooType   fooName    @{params}
   u8    first      0xff
   u8    second     0xff
   u8    third      0xff
   End Struct

Message with struct in header
    [Arguments]    @{params}
    New Message    StructHeaderMessage    StructProtocol    @{params}
    u8             field     10
