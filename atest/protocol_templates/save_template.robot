*** Settings ***
Test Setup        Define Simple Protocol
Test Teardown     Reset rammbock
Default Tags      regression
Resource          template_resources.robot


*** Test Cases ***
Save templates
    Save single and double templates
    Load template    single
    ${msg}=          Get message
    Should be equal as integers    ${msg.single.int}   1
    Load template    double
    ${msg}=          Get message
    Should be equal as integers    ${msg.double_1.int}   22

Save templates and field values
    Save single and double templates with values
    Load template    single
    ${msg}=          Get message
    Should be equal as integers    ${msg.single.int}   42
    Load template    double
    ${msg}=          Get message
    Should be equal as integers    ${msg.double_1.int}   4242

Load template with header parameters
    Save single and double templates
    Load template     single       header:field:10
    ${msg}=           Get message
    Should be equal as integers    ${msg._header.field}    10

Load template with header parameters does not alter the original template
    Save single and double templates
    Load template     single       header:field:10
    Load template     single
    ${msg}=           Get message
    Should be equal as integers    ${msg._header.field}    16

Trying to set pdu fields in Load template fails
    Save single and double templates
    Run keyword and expect error    Cannot set configs or pdu fields in Load template    Load template     single     single:1

Trying to set pdu fields in New message fails
    Save single and double templates
    Run keyword and expect error    Cannot set configs or pdu fields in New message    New message     single    Example    timeout=1

Adding fields to message after loading template is not allowed
    Save single and double templates
    Load template      single
    Run keyword and expect error
    ...    Adding fields to message loaded with Load template is not allowed
    ...    u32    new_field   2

Adding fields to message after loading template is allowed if saved as not locked
    Single valued
    Save template   unlocked   unlocked=True
    Load template   unlocked
    u32    new_field   2

Using load copy of template should preserve saved values in template
    Save single and double templates with values
    Load copy of template    single
    ${msg}=          Get message    single:43
    Should be equal as integers    ${msg.single.int}   43
    load template    single
    ${msg}=          Get message
    Should be equal as integers    ${msg.single.int}   42

Using load copy of template should preserve saved values in template when content is dynamic
    Save dynamic length valued
    Load copy of template    dynamic
    ${msg}=          Get message    length:4    string:fofafefa
    Should be equal as integers    ${msg.length.int}   4
    Should be equal as strings   ${msg.string}   fofafefa
    load template    dynamic
    ${msg}=          Get message
    Should be equal as integers    ${msg.length.int}   3
    Should be equal as strings   ${msg.string}   foofee

*** Keywords ***
Save single and double templates
    Single valued
    Save template    single
    Double valued
    Save template    double

Single valued
    New message    SingleRequest    Example
    u32    single    1

Double valued
    New message    DoubleRequest    Example
    u16    double_1  22
    u16    double_2  2222

Save single and double templates with values
    Single valued
    value   single   42
    Save template    single
    Double valued
    value  double_1  4242
    Save template    double

Dynamic length valued
    New message    DynamicRequest    Example
    u8      length
    Chars   length*2    string

Save dynamic length valued
    Dynamic length valued
    Value    length    3
    Value    string    foofee
    Save template    dynamic
