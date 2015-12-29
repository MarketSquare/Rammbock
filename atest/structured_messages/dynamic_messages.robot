*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Resource          ../Protocols.robot
Default Tags      Regression

*** Variables ***
${HEADER} =    0x0100aaaa000f0000

*** Test Cases ***
Receive dynamic message with structural length
    Client Sends hex    ${HEADER} 03 cafe babe d00d
    ${msg} =    Server Receives dynamic request with structural length
    Should be equal    ${msg.pairList[0].first.hex}     0xca
    Should be equal    ${msg.pairList[0].second.hex}    0xfe
    Should be equal    ${msg.pairList[2].first.hex}     0xd0

Encode dynamic message with structural length
    Populate dynamic message with structural length    2  0x01  0x02  0x11  0x22
    ${msg} =    Get message
    Should be equal    ${msg.pairList[0].first.hex}     0x01
    Should be equal    ${msg.pairList[0].second.hex}    0x02
    Should be equal    ${msg.pairList[1].first.hex}     0x11

Encoding dynamic list with structural length without defining fails
    Populate dynamic message with structural length    ${EMPTY}  0x01  0x02  0x11  0x22
    Run keyword and expect error   Value of numberOfPairs.value not set    Get message

Receive dynamic message
    Client Sends hex    ${HEADER} 03 cafe babe d00d
    ${msg} =    Server Receives dynamic request
    Should be equal    ${msg.pairList[0].first.hex}     0xca
    Should be equal    ${msg.pairList[0].second.hex}    0xfe
    Should be equal    ${msg.pairList[2].first.hex}     0xd0

Encode dynamic message
    Populate dynamic message  2  0x01  0x02  0x11  0x22
    ${msg} =    Get message
    Should be equal    ${msg.pairList[0].first.hex}     0x01
    Should be equal    ${msg.pairList[0].second.hex}    0x02
    Should be equal    ${msg.pairList[1].first.hex}     0x11

Encoding dynamic list without defined length fails
    # TODO: This should perhaps work?
    Populate dynamic message  ${EMPTY}  0x01  0x02  0x11  0x22
    Run keyword and expect error   Value of numberOfPairs not set    Get message

Encoding dynamic message with extra list entries fails
    Populate dynamic message  1  0x01  0x02  0x11  0x22
    Run keyword and expect error   Unknown fields in 'DynamicRequest.pairList': *   Get message

Encoding length in 2byte struct matches
    [Template]       2byte struct with given length
    #struct length    #length field value
    length_field
    length_field      2
    2                 2
    length_field-10   12

Encoding length in 2byte struct does not match
    [Template]       2byte struct with given length should fail
    #struct length   #length field value
    length_field     5
    length_field     1
    3                2
    1                2
    length_field-10  2
    length_field-10  13

Decoding length in 2byte struct matches
    [Template]       Decode 2byte struct with given length
    #struct length    #length field value
    length_field
    length_field      2
    2                 2
    length_field+1    1
    length_field-10   12

Decoding length in 2byte struct does not match
    [Template]       Decode 2byte struct with given length should fail
    #struct length   #length field value
    length_field     5
    length_field     1
    3                2
    1                2
    length_field-10  2
    length_field-10  13
    length_field+1   0
    length_field+50  0

Encoding dynamic length from value
    [Template]    Dynamic length fields with different parameters
    #static length field value     kw for dynamic content creation    kw to validate outcome and params
    ${none}                        static named chars field           get message and validate length field      ilmari        6
    8                              static named chars field           get message and validate length field      ilmari        8
    1                              static named chars field           get message and validate length field      ilmari        8    length_field:8
    1                              static named chars field           get message and validate length field      ilmari        6    length_field:6
    6                              static named chars field           get message and validate length field      ilmari        6

Encoding too short dynamic length fails
    [Template]    Dynamic length fields with different parameters
    #static length field value     kw for dynamic content creation    kw to validate outcome and params
    1                              static named chars field           should fail    get message        name:ilmari
    0                              static named chars field           should fail    get message        name:ilmari
    1                              static named chars field           should fail    get message        name:ilmari  length_field:2
    6                              static named chars field           should fail    get message        name:ilmari  length_field:2

Encoding variable length container with multiple fields
    Define variable length container    multiple fields
    ${msg}=    get message
    should be equal as integers    ${msg.length_field.int}    10

#TO-DO should make below testcases work
Encoding variable length container with structural length and multiple fields
    Define structural variable length container    multiple fields
    ${msg}=    get message
    should be equal as integers    ${msg.length_field.value.int}    10

Encoding variable length container with dynamic length content and structural length
    Define structural variable length container    Dynamic string
    ${msg}=    get message    container.name:fobbabobba
    should be equal as integers    ${msg.length_field.value.int}    11
    should be equal as integers    ${msg.container.stringLen.int}   10

Encoding variable length container with dynamic length content
    Define variable length container    Dynamic string
    ${msg}=    get message    container.name:fobbabobba
    should be equal as integers    ${msg.length_field.int}    11
    should be equal as integers    ${msg.container.stringLen.int}   10

Decoding variable length container with dynamic length content
    Define variable length container    Dynamic string
    Client sends message    container.name:fobbabobba
    ${msg} =       Server receives message
    should be equal as integers    ${msg.length_field.int}    11
    should be equal as integers    ${msg.container.stringLen.int}   10

Encode dynamic length string
    New message     DynString   Example    header:messageType:0xaaaa
    Dynamic string
    ${msg} =     Get message    name:test
    Should be equal as integers    ${msg.stringLen.int}    4

Encoding multiplied length string
    New message     DynString   Example    header:messageType:0xaaaa
    u8      length      2
    Chars   length*2    string  a
    ${msg} =    Get message
    Should be equal     ${msg.string.hex}   0x61000000

Encoding free length
    New message    FreeLength   Example    header:messageType:0xaaaa
    Chars    *     foo
    ${msg} =     Get message    foo:test
    Should be equal    ${msg.foo.ascii}    test

Decoding free length
    New message    FreeLength   Example    header:messageType:0xaaaa
    Chars    *     foo
    Client sends message         foo:test
    ${msg} =     Server receives message
    Should be equal    ${msg.foo.ascii}    test

Free length in struct
    New message    FreeLength   Example    header:messageType:0xaaaa
    u8      length
    New struct   WithLength    struct    length=length
    Chars    *     foo
    End struct
    u8      last    42
    Client sends message         struct.foo:test
    ${msg} =     Server receives message
    Should be equal as integers   ${msg.length.int}    4
    Should be equal    ${msg.struct.foo.ascii}    test
    Should be equal as integers   ${msg.last.int}    42

Free length in tbcd
    New message   FreeLength   Example     header:messageType:0xaaaa
    new tbcd container    tbcd_cont
    tbcd   4    first     1234
    tbcd   *    second    5678
    end tbcd container
    Client sends message
    ${msg} =     Server receives message
    Should be equal as integers   ${msg.tbcd_cont.second.tbcd}    5678

Filling array of free length dynamic message in send
    Dynamic message
    Client sends message  numberOfPairs:4
    ...  pairList[*].first:4
    ...  pairList[*].second:5
    ${msg} =     Server receives message
    Should be equal as integers    ${msg.pairList[3].second.int}    5

Filling array of free length complicated dynamic message in send
    Complicated dynamic message
    Client sends message  length:4
    ...  list[*].name:hello
    ...  list[*].pair.first:4
    ...  list[*].pair.second:5
    ${msg} =     Server receives message
    Should be equal as integers    ${msg.list[3].pair.second.int}    5

Reuse struct value from another message
    Populate dynamic message  2  0x01  0x02  0x11  0x22
    ${list msg} =    Get message
    Message with struct
    Value    pair    ${list msg.pairList[0]}
    ${pair msg} =    Get message
    Should be equal    ${pair msg.pair.first.hex}   0x01

Overriding array fields which have value set with [*]
    Populate dynamic message with value [*] all set to '0xff'
    ${dynamic message}=    Get message    pairList[3].first:0x00        numberOfPairs:4
    Should be equal    ${dynamic message.pairList[3].first.hex}   0x00

Reuse dynamic array in another message
    [Tags]
    ${msg1}=    Get dynamic message with list
    Dynamic message
    Value    numberOfPairs    ${msg1.numberOfPairs}
    Value    pairList         ${msg1.pairList}
    ${msg2}=    Get message
    Should be equal as integers     ${msg1.pairList[0].first}
    ...                             ${msg2.pairList[0].first}

*** Keywords ***
Named Pair
    [arguments]     ${name}=     ${value}=
    New Struct    Named Pair    ${name}
    Chars   10     name
    Pair   pair
    End struct

Pair
    [arguments]     ${name}=     ${value}=
    New Struct    Pair    ${name}
    u8    first       ${value}
    u8    second      ${value}
    End struct

length struct
    [arguments]     ${name}=     ${value}=
    New Struct    Length    ${name}
    u8    value    ${value}
    End Struct

Server Receives dynamic request
    [Arguments]    @{params}
    Dynamic message
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Server Receives dynamic request with structural length
    [Arguments]    @{params}
    Dynamic message with structural length
    ${msg} =    Server Receives message    @{params}
    [return]    ${msg}

Populate dynamic message
    [Arguments]   ${len}  ${0 first}  ${0 second}  ${1 first}  ${1 second}
    Dynamic Message
    value   numberOfPairs   ${len}
    value   pairList[0].first   ${0 first}
    value   pairList[0].second   ${0 second}
    value   pairList[1].first   ${1 first}
    value   pairList[1].second   ${1 second}

Populate dynamic message with value [*] all set to '${value}'
    Dynamic Message
    value   pairList[*].first     ${value}
    value   pairList[*].second    ${value}

Populate dynamic message with structural length
    [Arguments]   ${len}  ${0 first}  ${0 second}  ${1 first}  ${1 second}
    Dynamic Message with structural length
    value   numberOfPairs.value   ${len}
    value   pairList[0].first   ${0 first}
    value   pairList[0].second   ${0 second}
    value   pairList[1].first   ${1 first}
    value   pairList[1].second   ${1 second}

Message with struct
    [arguments]    ${pair values}=
    New Message    StructRequest  Example    header:messageType:0xaaaa
    Pair    pair   ${pair values}

Dynamic message
    New Message    DynamicRequest  Example    header:messageType:0xaaaa
    Dynamic pair array

Dynamic message with structural length
    New Message    DynamicRequest  Example    header:messageType:0xaaaa
    Dynamic array with struct length

Dynamic pair array
    u8      numberOfPairs
    Array   numberOfPairs    Pair    pairList

Complicated Dynamic message
    New Message    DynamicRequest  Example    header:messageType:0xaaaa
    Dynamic named pair array

Dynamic array with struct length
    length struct    numberOfPairs
    Array   numberOfPairs.value    Pair    pairList

Dynamic named pair array
    u8      length
    Array   length    Named Pair    list

Dynamic string
    u8     stringLen
    Chars    stringLen   name

Define variable length container
    [Arguments]    ${content}
    New message   FooExample   Example    header:messageType:0xb0b0
    u8    length_field
    container    container    length_field     ${content}
    u16   field_after_container       0xcafe

Define structural variable length container
    [Arguments]    ${content}
    New message   FooExample   Example    header:messageType:0xb0b0
    length struct    length_field
    container    container    length_field.value     ${content}
    u16   field_after_container       0xcafe

2byte struct with given length
    [Arguments]     ${struct length}    ${length field value}=
    define 2byte struct    ${struct length}
    ${msg}    get message   length_field:${length field value}
    ${length field value}=    Evaluate    '${length field value}' or 2
    Should be equal as integers    ${msg.length_field.int}   ${length field value}

2byte struct with given length should fail
    [Arguments]     ${struct length}    ${length field value}
    define 2byte struct    ${struct length}
    Should fail    get message   length_field:${length field value}

Decode 2byte struct with given length
    [Arguments]     ${struct length}    ${length field value}=
    define 2byte struct    ${struct length}
    Client sends message   length_field:${length field value}
    ${msg}     Server receives message
    ${length field value}=    Evaluate    '${length field value}' or 2
    Should be equal as integers    ${msg.length_field.int}   ${length field value}

Decode 2byte struct with given length should fail
    [Arguments]     ${struct length}    ${length field value}
    define 2byte struct    ${EMPTY}
    Client sends message   length_field:${length field value}
    define 2byte struct    ${struct length}
    Should fail     Server receives message

define 2byte struct
    [Arguments]     ${length}
    New message   FooExample   Example    header:messageType:0xb0b0
    u8    length_field
    container    container    ${length}    u16    field    0x00

multiple fields
    u8    value1    1
    u8    value2    2
    u32   value3    2
    u32   value4    2

Dynamic length fields with different parameters
    [arguments]    ${static length field value}    ${kw for dynamic content creation}    @{kw to validate outcome and params}
    New message   FooExample  Example   header:messageType:0xb0b0
    u8    length_field    ${static length field value}
    Run keyword    ${kw for dynamic content creation}
    run keyword    @{kw to validate outcome and params}

static named chars field
    run keyword    chars    length_field    name

get message and validate length field
    [arguments]       ${value}    ${valid length}    @{args for get msg}
    ${msg}=   get message    name:${value}    @{args for get msg}
    should be equal as integers    ${msg.length_field.int}    ${valid length}

Get dynamic message with list
    Populate dynamic message    2    1   2   3   4
    ${msg}=    Get message
    [Return]    ${msg}

