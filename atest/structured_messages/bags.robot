*** Settings ***
Test Setup        Setup protocol, UDP server, and client
Test teardown     Teardown rammbock and increment port numbers
Resource          ../Protocols.robot
Default Tags      Regression


*** Test Cases ***
Simple bag
    Bag message client
    u8    element    42
    Client sends message
    Bag message server
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.foo[0].int}     42

Bag with validation matching
    Bag message client
    u8    element    1
    Client sends message
    Bag message server
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.bar[0].int}      1
    Should be equal as integers   ${msg.intBag.bar.len}         1
    Should be equal as integers   ${msg.intBag.foo.len}         0

Bag with validation matching and longer value
    Bag message client
    u32    element    0
    Client sends message
    Bag message server
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.dar[0].int}      0
    Should be equal as integers   ${msg.intBag.dar.len}         1
    Should be equal as integers   ${msg.intBag.foo.len}         0
    Should be equal as integers   ${msg.intBag.len}             1

Bag with two values
    Bag message client
    u32    element      0
    u8     element2     42
    Client sends message
    Bag message server
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.dar[0].int}      0
    Should be equal as integers   ${msg.intBag.dar.len}         1
    Should be equal as integers   ${msg.intBag.foo[0].int}      42
    Should be equal as integers   ${msg.intBag.len}             2

Bag with same value twice fails
    Bag message client
    u32     element     0
    u32     element2    0
    Client sends message
    Bag message server
    Run keyword and expect error    2 values in bag intBag for dar (size 0-1).    Server receives message

Bag with same value twice is okay
    Bag message client
    u8     element      1
    u8     element2     1
    Client sends message
    Bag message server
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.bar[0].int}      1
    Should be equal as integers   ${msg.intBag.bar[1].int}      1
    Should be equal as integers   ${msg.intBag.bar.len}         2
    Should be equal as integers   ${msg.intBag.len}             2

Bag with minimums
    Bag message client
    u8     element       1
    u8     element2      42
    u8     element3      1
    u8     first         12
    u8     second        55
    Client sends message
    Bag message server with minimums
    ${msg}=    Server receives message
    Should be equal as integers   ${msg.intBag.foo[0].int}      42
    Should be equal as integers   ${msg.intBag.bar[1].int}      1
    Should be equal as integers   ${msg.intBag.dar[0].first}    12
    Should be equal as integers   ${msg.intBag.len}             4

Fail when minimums are not met
    Bag message client
    u8     element       1
    u8     element3      1
    u8     first         12
    u8     second        55
    Client sends message
    Bag message server with minimums
    Run keyword and expect error    No values in bag intBag for foo (size 1).    Server receives message

*** Keywords ***
Bag message client
    New message   ConditionalExample   Example    header:messageType:0xb0b0

Bag message server
    New message   ConditionalExample   Example    header:messageType:0xb0b0
    Start bag    intBag
    case   0-1    u8    foo    42
    case   0-2    u8    bar    1
    case   0-1    u32   dar    0
    End bag

Bag message server with minimums
    New message   ConditionalExample   Example    header:messageType:0xb0b0
    Start bag    intBag
    case   1      u8    foo    42
    case   1-2    u8    bar    1
    case   *      simple struct
    End bag

Simple struct
   New Struct    FooType   dar
   u8    first
   u8    second     55
   End Struct



