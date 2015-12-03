*** Settings ***
Test Setup          Setup up server for test
Test Teardown       Reset Rammbock
Library             Rammbock
Resource            Protocols.robot

*** Test Cases ***
String message field matching the header filter
    Define and send example message
    Receive example message matching filter

String message field not matching the header filter
    Define and send example message
    Run keyword and expect error  * timed out  Receive example message with filter value    NOT MATCHING

String message field not matching the header filter with unicode value
    Define and send example message
    Run keyword and expect error  * timed out  Receive example message with filter value     देवनागरी

*** Keywords ***
Setup up server for test
    Define a protocol with string field in header
    Setup UDP server and client    protocol=StringInHeader

Define a protocol with string field in header
    New protocol    StringInHeader
    Chars     *     string_field 
    End protocol

Define and send example message
    New message  exMessage  StringInHeader  header:string_field:match string message
    Client sends message

Receive example message matching filter
    New message  exMessage  StringInHeader  header:string_field:match string message
    Server receives message  header_filter=string_field

Receive example message with filter value
    [arguments]    ${value}
    New message  exMessage  StringInHeader  header:string_field:${value}
    Server receives message  header_filter=string_field
