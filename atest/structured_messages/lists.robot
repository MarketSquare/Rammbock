*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Resource          ../Protocols.robot
Default Tags      Regression

*** Test Cases ***
Message with list
    Client sends request with list
    ${msg} =    Server receives request with list    someList[2]:3
    Should be equal as integers    ${msg.someList[4].int}     3

Message with list containing structs
    Client sends request with list containing structs   someList[0].first:2
    ${msg}=     Server receives request with list containing structs  someList[0].first:2
    Should be equal as integers   ${msg.someList[1].second.int}    3

Message with list validation fails
    Client sends request with list
    Server should fail validation with list   someList.2    someList[2]:4

Message with list in list
    New message     TwoDimensionalInts  Example    header:messageType:0xaaaa
    List in List
    value   *   0
    ${msg} =    Get message     multiArray[1][0]:42
    Should be equal as integers     ${msg.multiArray[1][0].int}     42
    Should be equal as integers     ${msg.multiArray[1][1].int}     0

Receiving message with unknown length list
    Client sends request containing '4' entries
    ${msg}=    Server receives request containing any number of entries
    Should be equal as integers    ${msg.list.len}    4

Receiving message with not enough entries fails
    Client sends request containing '4' entries
    Run keyword and expect error    Not enough*    Server receives request containing '5' entries


*** Keywords ***
Client sends request with list
    [Arguments]    @{params}
    List message
    Client sends message   @{params}

Client sends request with list containing structs
    [Arguments]    @{params}
    Message with list containing struct
    Client sends message   @{params}

Server receives request with list
    [Arguments]    @{params}
    List message
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Server receives request with list containing structs
    [Arguments]   @{params}
    Message with list containing struct
    ${msg}=       Server Receives message    @{params}
    [return]      ${msg}

Server should fail validation with list
    [Arguments]    ${field}    @{params}
    Run keyword and expect error     Value of field ${field}*    Server receives request with list    @{params}

List message
    New message    ListRequest    Example    header:messageType:0xaaaa
    Array   5    u32    someList    3

Message with list containing struct
    New message    ListRequestWithStruct    Example    header:messageType:0xaaaa
    Array   5    Pair    someList    3

Pair
    [arguments]     ${name}=     ${value}=
    New Struct    Pair    ${name}
    u8    first       ${value}
    u8    second      ${value}
    End struct

List in List
    Array   2   Inner List   multiArray    2   u8

Inner list
    [arguments]     ${name}=    ${size}=    ${type}=
    Array       ${size}    ${type}      ${name}

Client sends request containing '${len}' entries
    New message    fooList    Example     header:messageType:0xaaaa
    Array    ${len}    u32    list
    Value    *     5
    Client sends message

Server receives request containing any number of entries
    New message    fooList    Example     header:messageType:0xaaaa
    Array    *    u32    list
    ${msg}=    Server receives message
    [Return]    ${msg}

Server receives request containing '${number of}' entries
    New message    fooList    Example     header:messageType:0xaaaa
    Array    ${number of}    u32    list
    ${msg}=    Server receives message
    [Return]    ${msg}
