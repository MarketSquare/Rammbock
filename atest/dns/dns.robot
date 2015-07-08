*** Settings ***
Suite setup    define dns protocol and setup server and client
Suite teardown    Reset Rammbock
Library    Rammbock
Library    ../message_tools.py
Resource    ../Protocols.robot
Default tags    Regression

*** Test cases ***
DNS Query
    dns A query with one domain
    ${msg}=    Get message

dns answer
    dns answer with one domain and IPv4 answer
    ${msg}=    Get message

send and receive dns request
    dns A query with one domain
    client sends message
    server receives message

Send two and receive two dns request in sequence
    dns A query with one domain
    client sends message
    client sends message
    server receives message
    server receives message

*** Keywords ***
dns answer with one domain and IPv4 answer
    new message    name    DNS    header:questions:1    header:answer_rrs:1
    query for example.com
    answer for example.com

answer for ${DOMAIN}
    Value    answers[0].type    1
    Value    answers[0].class    1
    Value    answers[0].time_to_live    1200
    Value    answers[0].data_length    4
    IP Value    answers[0].address    192.168.0.1

IP Value
    [arguments]    ${field}    ${value}
    ${converted}=    convert to ip    ${value}
    Value    ${field}    ${converted}

dns A query with one domain
    new message    name    DNS    header:questions:1
    query for google.com

query for ${DOMAIN}
    Value    transaction_id           0xbabe
    Value    flags.response           0
    Label sequence value    queries[0].name    ${DOMAIN}
    Value    queries[0].type    0x0001
    Value    queries[0].class   0x0001

Label sequence value
    [arguments]    ${field}    ${domain}
    ${converted}=    convert to label sequence    ${domain}
    Value    ${field}    ${converted}

define dns protocol and setup server and client
    define dns protocol
    Setup UDP server and client      DNS

define dns protocol
    new protocol    DNS
    dns header
    Array     questions        dns_query    queries
    Array     answer_rrs       dns_answer    answers
    Array     authority_rrs    authority_rr    authorities
    Array     additional_rrs   additional_rr    additionals
    end protocol

dns header
    u16    transaction_id
    dns flags
    u16    questions        0
    u16    answer_rrs       0
    u16    authority_rrs    0
    u16    additional_rrs   0

authority_rr
    [arguments]    ${name}
    u8    placeholder

additional_rr
    [arguments]    ${name}
    u8    placeholder

dns_query
    [arguments]    ${name}
    new struct    DNS query    ${name}
    label sequence    name
    u16    type
    u16    class
    end struct

dns_answer
    [arguments]    ${name}
    new struct    DNS answer    answer
    u16    name    0xc00c
    u16    type
    u16    class
    u32    time_to_live
    u16    data_length
    Uint    data_length    address
    end struct

Label sequence
    [arguments]    ${name}
    Chars    *    ${name}    terminator=0x00

dns flags
    new binary container    flags
    bin    1    response
    bin    4    opcode       0
    bin    1    spare_1        0
    bin    1    truncated    0
    bin    1    recursion_desired    0
    bin    1    spare_2        0
    bin    1    Z        0
    bin    1    spare        0
    bin    1    non_authenticated_data        0
    bin    4    spare_3        0
    end binary container
