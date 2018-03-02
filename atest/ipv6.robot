*** Settings ***
Resource         Protocols.robot
Test Teardown    Teardown rammbock and increment port numbers
Default Tags     Regression

*** Variables ***
${IPV6 LOOPBACK} =    0:0:0:0:0:0:0:1

*** Test Cases ***
IPv6 TCP
    Start TCP SERVER    name=ExampleServer    ip=${IPV6 LOOPBACK}    port=${SERVER PORT}    family=ipv6
    Start TCP client    name=ExampleClient    family=ipv6
    connect    ${IPV6 LOOPBACK}    ${SERVER PORT}    name=ExampleClient
    Accept connection    name=ExampleServer
    Client and server send and receive binary

IPv6 UDP
    Start UDP SERVER    name=ExampleServer    ip=${IPV6 LOOPBACK}    port=${SERVER PORT}    family=ipv6
    Start UDP client    name=ExampleClient    family=ipv6
    connect    ${IPV6 LOOPBACK}    ${SERVER PORT}    name=ExampleClient
    Client and server send and receive binary

IPv6 with protocols
    Define simple protocol
    Start UDP SERVER    name=ExampleServer    ip=${IPV6 LOOPBACK}    port=${SERVER PORT}    protocol=Example    family=ipv6
    Start UDP client    name=ExampleClient    protocol=Example    family=ipv6
    connect    ${IPV6 LOOPBACK}    ${SERVER PORT}    name=ExampleClient
    New message   Foo    Example
    u32     foo
    Client sends message    foo:1
    ${msg}=    Server receives message
    Should be equal as integers    ${msg.foo}    1

*** Keywords ***
Client and server send and receive binary
    Client sends binary    foo
    ${message}=    Server receives binary
    Should be equal as strings    ${message}    foo
    Server sends binary    bar
    ${message}=    Client receives binary
    Should be equal as strings    ${message}    bar
