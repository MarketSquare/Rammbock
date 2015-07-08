*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Library           ../message_tools.py
Resource          ../Protocols.robot
Default Tags      Regression


*** Test Cases ***
Simple union
    Client sends simple union request     simpleU:fooMiddle   simpleU.fooMiddle:0xf00d
    ${msg} =    Server receives simple union request
    Should be equal    ${msg.simpleU.fooBig.hex}        0xf00d0000
    Should be equal    ${msg.simpleU.fooMiddle.hex}     0xf00d
    Should be equal    ${msg.simpleU.fooShort.hex}      0xf0

Union in struct
    Client sends simple union in struct
    ...  structField.structBeginField:0xbeba
    ...  structField.onion:fooMiddle
    ...  structField.onion.fooMiddle:0xf00d
    ...  structField.structEndField:0xabba
    ${msg} =    Server receives union in struct
    Should be equal as integers   ${msg.structField.structBeginField.hex}  0xbeba
    Should be equal as integers   ${msg.structField.onion.fooMiddle.hex}   0xf00d
    Should be equal as integers   ${msg.structField.structEndField.hex}    0xabba

Complex union
    Client sends complex union request     complexU:complexType  complexU.complexType.first:1    complexU.complexType.second:2
    ${msg} =    Server receives complex union request
    Should be equal as integers    ${msg.complexU.complexType.first.int}     1
    Should be equal as integers    ${msg.complexU.complexType.second.int}     2
    Should be equal as integers    ${msg.complexU.basicType.int}     0

Hyper complex union
    Client sends hyper complex union request    hyperU:user
    ${msg} =    Server receives hyper complex union request
    Should be equal    ${msg.hyperU.user.name.ascii}     johnsson

Choosing union when receiving
    [Tags]
    Client sends hyper complex union request    hyperU:machine
    ${msg} =    Server receives hyper complex union request    hyperU:machine
    Field should exist        ${msg.hyperU}     machine
    Field should not exist    ${msg.hyperU}     user

Proper error message when union not chosen
    Simple union in struct
    Run keyword and expect error   Value not chosen for union 'UnionInStruct.structField.onion'    get message
    ...  structField.structBeginField:0xbeba
    ...  structField.structEndField:0xabba

Proper error message when union field not set
    Simple union in struct
    Run keyword and expect error   Value of structField.onion.fooMiddle not set    get message
    ...  structField.structBeginField:0xbeba
    ...  structField.onion:fooMiddle
    ...  structField.structEndField:0xabba

Proper error message when Unknown union field
    Simple union in struct
    Run keyword and expect error   Unknown union field 'fooMiddlexxxx' in 'UnionInStruct.structField.onion'     get message
    ...  structField.structBeginField:0xbeba
    ...  structField.onion:fooMiddlexxxx
    ...  structField.structEndField:0xabba


*** Keywords ***
Client sends simple union request
    [Arguments]    @{params}
    Simple union message
    Client sends message   @{params}

Client sends simple union in struct
    [Arguments]     @{params}
    Simple union in struct
    Client sends message   @{params}

Server receives simple union request
    [Arguments]    @{params}
    Simple union message
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Server receives union in struct
    [Arguments]    @{params}
    Simple union in struct
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Client sends complex union request
    [Arguments]    @{params}
    Complex union message
    Client sends message   @{params}

Server receives complex union request
    [Arguments]    @{params}
    Complex union message
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Client sends hyper complex union request
    [Arguments]    @{params}
    Hyper complex union message
    value   hyperU.user.name    johnsson
    value   hyperU.user.age    47
    value   hyperU.machine.id    1337
    value   hyperU.machine.price    9500
    Client sends message   @{params}

Server receives hyper complex union request
    [Arguments]    @{params}
    Hyper complex union message
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Simple union message
   New message    UnionMessage   Example  header:messageType:0xb00b
   Simple union   simpleU

Simple union in struct
   New message    UnionInStruct   Example  header:messageType:0xbabe
   SStructField   structField

SStructField
    [Arguments]    ${name}
    New struct     SStructField    ${name}
    u32            structBeginField
    Simple union   onion
    u32            structEndField
    End struct

Complex union message
   New message   ComplexUnion    Example  header:messageType:0xb00b
   ComplexUnion  complexU

Simple union
   [arguments]    ${name}
   New Union      Simple   ${name}
   u32            fooBig
   u16            fooMiddle
   u8             fooShort
   End union

Complex union
   [arguments]   ${name}
   New Union         Complex   ${name}
   u8            basicType
   Tuple         complexType
   End union

Tuple
    [arguments]     ${name}
    New Struct    Tuple    ${name}
    u16    first
    u16    second
    End struct

Hyper Complex union message
   New message   HyperUnion    Example  header:messageType:0xb00b
   HyperUnion  hyperU

HyperUnion
   [arguments]   ${name}
   New Union         Hyper   ${name}
   Machine       machine
   User          user
   End union

Machine
    [arguments]     ${name}
    New Struct    Machine    ${name}
    u32       id
    u16       price
    End struct

User
    [arguments]     ${name}
    New Struct    User    ${name}
    chars   10       name
    u32            age
    End struct
