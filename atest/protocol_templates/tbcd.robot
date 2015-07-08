*** Settings ***
Test Setup        Define example protocol
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      regression
Resource          ../Protocols.robot

*** Test Cases ***

encoding single value with even amount of numbers
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   4    digits    1234
    end tbcd container
    ${msg}=    Get Message
    should be equal    ${msg.tbcd_cont.digits.tbcd}    1234

encoding single value with odd amount of numbers
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   5    digits    12345
    end tbcd container
    ${msg}=    Get Message
    should be equal    ${msg.tbcd_cont.digits.tbcd}    12345

encoding multiple values with even amount of numbers
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   4    first     1234
    tbcd   4    second    5678
    end tbcd container
    ${msg}=    Get Message
    should be equal    ${msg.tbcd_cont.first.tbcd}     1234
    should be equal    ${msg.tbcd_cont.second.tbcd}    5678

encoding multiple values with odd amount of numbers
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   4    first     1234
    tbcd   5    second    56789
    end tbcd container
    ${msg}=    Get Message
    should be equal    ${msg.tbcd_cont.first.tbcd}     1234
    should be equal    ${msg.tbcd_cont.second.tbcd}    56789

Validation error
    [Setup]    Define protocol, start tcp server and two clients    Example
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   3    digits    123
    end tbcd container
    client sends message
    run keyword and expect error    *123!=124*    server receives message    tbcd_cont.digits:124

Decoding two tbcd values
    [Template]    decoding two value tbcd
    [setup]
    [teardown]
    #first   #second
    123      456
    123      4567
    1234     567
    1234     4567
    1        2

Get recursive name when field not found
    New message    recursive field name    Example    header:messageType:0xdddd
    new struct    struct   struct
    new tbcd container    tbcd_cont
    tbcd    3    value
    end tbcd container
    end struct
    run keyword and expect error    *tbcd_cont.value*    get message

Star length in tbcd field inside struct
    New message    recursive field name    Example    header:messageType:0xdddd
    u8    length
    new struct    struct    struct    length=length
    new tbcd container    tbcd
    tbcd     3    static    358
    tbcd     *    dynamic   6100000000001
    end tbcd container
    end struct
    ${msg}=    get message
    log many    ${msg.length.int}    ${msg.struct.tbcd.static.tbcd}    ${msg.struct.tbcd.dynamic.tbcd}
    should be equal as integers   ${msg.length.int}    8
    should be equal   ${msg.struct.tbcd.static.tbcd}    358
    should be equal   ${msg.struct.tbcd.dynamic.tbcd}    6100000000001

*** Keywords ***
decoding two value tbcd
    [Arguments]    ${val 1}     ${val 2}
    [Teardown]    Teardown rammbock and increment port numbers
    ${len 1}=    Get length    ${val 1}
    ${len 2}=    Get length    ${val 2}
    Define protocol, start tcp server and two clients    Example
    New message    tbcd testing    Example    header:messageType:0xdddd
    new tbcd container    tbcd_cont
    tbcd   ${len 1}    first    ${val 1}
    tbcd   ${len 2}    last     ${val 2}
    end tbcd container
    client sends message
    ${msg}=    server receives message
