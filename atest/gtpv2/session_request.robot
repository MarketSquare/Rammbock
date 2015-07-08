*** Settings ***
Test Setup        Create server and client, and define protocol
Test Teardown     Reset Rammbock
Default Tags      regression
Resource          gtpv2_resource.robot


*** Test Cases ***
Create Session Request
    Create and send Create Session Request
    Receive and Validate Create Session Request


*** Keywords ***
Create and send Create Session Request
    Create Session Request
    Create Session Request Values
    client sends message   header:sequence number:48

Receive and Validate Create Session Request
    Create Session Request
    Create Session Request Values
    ${msg}=    Server Receives message    header:sequence number:48

Create Session Request Values
    value   IMSI.instance.value                                     0x01
    value   IMSI.value.imsi.value                                   262120000000001
    value   ULI.value.flags                                         0b00011000
    value   ULI.value.tai.mcc.value                                 262
    value   ULI.value.tai.mnc.value                                 12
    value   ULI.value.ecgi.mcc.value                                262
    value   ULI.value.ecgi.mnc.value                                12
    value   ULI.value.ecgi.eci.ecgi                                 234
    value   ULI.value.tai.tracking_area_code                        1
    value   Serving network.value.mcc.value                         262
    value   Serving network.value.mnc.value                         12
    value   Rat type.value.rat_type                                 6
    value   Indication.value.fields.DAF                             1
    ip value   f-teid1.value.f-teid_ipv4                            192.168.0.1
    value   f-teid1.value.values.interface type                     7
    value   f-teid2.instance.value                                  1
    IP value   f-teid2.value.f-teid_ipv4                            127.0.0.1
    value   f-teid2.value.values.interface type                     10
    Label sequence value   APN.value.access_point_name                             sgw.foo.com.mnc012.mcc262.gprs
    value   Aggregate maximum bit rate.value.ambr_uplink            2
    value   Aggregate maximum bit rate.value.ambr_downlink          1
    value   Bearer context.value.eps_bearer_id.value.epsbid.value   5
    value   Bearer context.value.bearer_level_qos.value.arp.pl      1
    value   Bearer context.value.bearer_level_qos.value.label       9
    value   Recovery.value.recovery                                 1


Create Session Request
    new message    create session request    gtpv2    header:message type:${CREATE SESSION REQUEST}
    IE  IMSI
    IE  MSISDN
    IE  ULI
    IE  Serving network
    IE  Rat type
    IE  Indication
    Named IE    f-teid1     F-TEID
    Named IE    f-teid2     F-TEID
    IE  APN
    IE  Selection mode
    IE  PDN Type
    IE  PDN Address Allocation
    IE  APN Restriction
    IE  Aggregate maximum bit rate
    IE  Bearer context
    IE  Recovery
    IE  Ue time zone
    IE  charging characteristics

IMSI
    new tbcd container    imsi
    tbcd    15    value
    end tbcd container

MSISDN
    new tbcd container    msisdn
    tbcd    3    country_code       358
    tbcd    *   address_digits      6100000000001
    end tbcd container

ULI
    u8    flags
    TAI
    ECGI

TAI
    new struct    tai    tai
    single value tbcd container    mcc    3        ${none}
    single value tbcd container    mnc    2        ${none}
    u16    tracking_area_code
    end struct

ECGI
    new struct    E-UTRAN Cell Global Identifier    ecgi
    single value tbcd container    mcc    3        ${none}
    single value tbcd container    mnc    2        ${none}
    new binary container   eci
    Bin    4    spare    0
    bin    28   ecgi
    end binary container
    end struct

Serving network
    new tbcd container    mcc
    tbcd    3    value
    end tbcd container
    new tbcd container    mnc
    tbcd    2    value
    end tbcd container

Rat type
    u8    rat_type

Indication
    new binary container    fields
    Bin    1    DAF     0
    Bin    1    DTF     0
    Bin    1    HI      0
    Bin    1    DFI     0
    Bin    1    OI      0
    Bin    1    ISRSI   0
    Bin    1    ISRAI   0
    Bin    1    SGWCI   0
    Bin    1    SQCI    0
    Bin    1    UIMSI   0
    Bin    1    CFSI    0
    Bin    1    CRSI    0
    Bin    1    PS      0
    Bin    1    PT      0
    Bin    1    SI      0
    Bin    1    MSV     0
    Bin    3    SPARE   0
    Bin    1    S6AF    0
    Bin    1    S4AF    0
    Bin    1    MBMDT   0
    Bin    1    ISRAU   0
    Bin    1    CCRSI   0
    end binary container

F-TEID
    new binary container    values
    bin    1    v4    1
    bin    1    v6    0
    bin    6    interface type
    end binary container
    u32    teid_gre_key    0x00
    u32    f-teid_ipv4

APN
    chars  *  access_point_name

Selection mode
    new Binary container    selection_mode
    bin    6    spare    0b111111
    bin    2    value    0
    end binary container

PDN Type
    new Binary container    pdn_type
    bin    5    spare    0
    bin    3    value    1
    end binary container

PDN Address Allocation
    PDN Type
    u32    pdn_address_and_prefix   0

APN Restriction
    u8    apn_restriction   0

Aggregate maximum bit rate
    u32    ambr_uplink
    u32    ambr_downlink

Bearer context
    IE       eps_bearer_id
    IE       bearer_level_qos

EPS bearer id
    new binary container    epsbid
    bin    4    spare   0
    bin    4    value
    end binary container

Bearer level qos
    new binary container   arp
    bin   1    spare   0
    bin   1    pci    0
    bin   4    pl
    bin   1    spare_2   0
    bin   1    pvi     0
    end binary container
    u8    label
    u40    mbr_uplink      0
    u40    mbr_downlink    0
    u40    gbr_uplink      0
    u40    gbr_downlink    0

Recovery
    u8    recovery

UE time zone
    new binary container    timezone
    bin   6    spare    0b111111
    bin   2    value    0
    end binary container
    new binary container    dst
    bin   6    spare   0
    bin   2    value   0
    end binary container

Charging characteristics
    u16    charging_characteristic    0x3200

