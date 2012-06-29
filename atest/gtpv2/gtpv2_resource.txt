*** Settings ***
Library    Rammbock
Library    ../message_tools.py


*** Variables ***
${TEST MACHINE}   127.0.0.1
${SERVER}         ${TEST MACHINE}
${CLIENT}         ${TEST MACHINE}
${GTP CONTROL PORT}                 2123
${IMSI_type}                        1
${Recovery_type}                    3
${CREATE SESSION REQUEST}           32
${APN_type}                         71
${Aggregate maximum bit rate_type}  72
${EPS bearer id_type}               73
${MSISDN_type}                      76
${Indication_type}                  77
${PDN Address Allocation_type}      79
${Bearer level qos_type}            80
${Rat type_type}                    82
${Serving network_type}             83
${ULI_type}                         86
${F-TEID_type}                      87
${Bearer context_type}              93
${Charging characteristics_type}    95
${PDN Type_Type}                    99
${Ue time zone_type}                114
${APN Restriction_type}             127
${Selection mode_type}              128


*** Keywords ***
define gtpv2 protocol
    new protocol    gtpv2
    u8    flags    72
    u8    message type
    u16   message length
    u32   tunnel endpoint identifier    0
    u24   sequence number
    u8    spare    0
    pdu    message length-12
    end protocol

Create server and client, and define protocol
    define gtpv2 protocol
    start udp server    ${SERVER}    ${GTP CONTROL PORT}    protocol=gtpv2
    start udp client    ip=${CLIENT}    protocol=gtpv2
    connect    ${SERVER}    ${GTP CONTROL PORT}

IE
    [Arguments]    ${name}
    Named IE    ${name}    ${name}

Named IE
    [Arguments]    ${field name}  ${name}
    ${type}     Find type if defined or empty    ${name}
    New struct    IE    ${field name}
    IE header   ${name}    ${type}
    IE value    ${name}
    End struct

Find type if defined or empty
    [Arguments]    ${name}
    ${type} =      Get variable value    ${${name}_type}     ${empty}
    [return]      ${type}

IE header
    [Arguments]    ${name}    ${type}
    u8    ie type    ${type}
    u16    ie_length
    new binary container    instance
    bin    4    spare    0
    bin    4    value    0
    end binary container

IE Value
    [Arguments]    ${kw}    
    new struct    Container    value    length=ie_length
    run keyword    ${kw}
    end struct

ADDRESS
    [Arguments]    ${value}
    IE    address    54    Chars    ie length    ${value}

single value tbcd container
    [Arguments]    ${name}    ${len}    ${value}
    new tbcd container    ${name}
    tbcd   ${len}    value    ${value}
    end tbcd container

IP Value
    [arguments]    ${field}    ${value}
    ${converted}=    convert to ip    ${value}
    Value    ${field}    ${converted}

Label sequence value
    [arguments]    ${field}    ${domain}
    ${converted}=    convert to label sequence    ${domain}
    Value    ${field}    ${converted}