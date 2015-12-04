*** Settings ***
Test Setup          Setup up server for test
Test Teardown       Reset Rammbock
Library             Rammbock
Resource            Protocols.robot
Default Tags        regression

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

String message field matching the header filter with regexp
    Define and send example message
    Receive example message with filter value    REGEXP:.*message

String message field not matching the header filter with regexp
    Define and send example message
    Run keyword and expect error  * timed out  Receive example message with filter value    REGEXP:.*invalid

String message field matching the header filter with invalid regexp
    Define and send example message
    Run keyword and expect error  Invalid RegEx *  Receive example message with filter value    REGEXP:**

String message field matching the regexp
    Define and send example message
    Receive example message with regexp value    REGEXP:.*message

String message field not matching the regexp
    Define and send example message
    Run keyword and expect error  * does not match the RegEx *  Receive example message with regexp value    REGEXP:.*invalid

Comparing string message field with an invalid regexp
    Define and send example message
    Run keyword and expect error  Invalid RegEx *  Receive example message with regexp value    REGEXP:[0-9]++

Comparing string message field with a blank regexp
    Define and send example message
    Receive example message with regexp value    REGEXP:

Comparing string message field with a invalid ending regexp
    Define and send example message
    Run keyword and expect error  Invalid RegEx *  Receive example message with regexp value    REGEXP:[]

Comparing integer message field with a regexp
    Define and send example message
    New message  exMessage  StringInHeader  header:integer_field:REGEXP:.*
    Run keyword and expect error  * can not be matched to regular expression pattern *  Server receives message

String message field matching the header filter with multiple messages in stream
    Define and send multiple messages
    Receive example message with filter value    REGEXP:^first

*** Keywords ***
Setup up server for test
    Define a protocol with string field in header
    Setup UDP server and client    protocol=StringInHeader

Define a protocol with string field in header
    New protocol    StringInHeader
    Uint      1     integer_field
    Chars     *     string_field    terminator=0x00
    End protocol

Define and send example message
    New message  exMessage  StringInHeader  header:string_field:match string message  header:integer_field:10
    Client sends message

Define and send multiple messages
    New message  exMessage1  StringInHeader  header:string_field:first string message  header:integer_field:10
	Client sends message
	New message  exMessage2  StringInHeader  header:string_field:second string message  header:integer_field:10
    Client sends message

Receive example message matching filter
    New message  exMessage  StringInHeader  header:string_field:match string message
    Server receives message  header_filter=string_field

Receive example message with filter value
    [arguments]    ${value}
    New message  exMessage  StringInHeader  header:string_field:${value}
    Server receives message   header_filter=string_field

Receive example message with regexp value
    [arguments]    ${value}
    New message  exMessage  StringInHeader  header:string_field:${value}
    Server receives message
