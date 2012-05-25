*** Settings ***
Library    Rammbock
Test teardown    Reset Rammbock
Default tags    Regression

*** Test Cases ***
Define two consecutive protocols
    [setup]
    Define first protocol
    define second protocol

Get valid error message when no protocols are defined
    run keyword and expect error    Protocol not defined! Please define a protocol before creating a message!    new message    any protocol

Get valid error message with nonexisting protocol
    Define first protocol
    run keyword and expect error    Protocol not defined! Please define a protocol before creating a message!    new message    nonexisting protocol

*** Keywords ***
Define first protocol
    new protocol    First
    u8    length    4
    pdu   length
    end protocol

Define second protocol
    new protocol    Second
    u8    length    4
    pdu   length
    end protocol
