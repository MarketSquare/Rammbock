*** Settings ***
Library    Rammbock
Library    message_tools.py

*** Variables ***
${Host-IP-Address type}                     257
${Auth-Application-ID type}                 258
${Vendor-Specific-Application-Id type}      260
${Origin-Host type}                         264
${Supported-Vendor-ID type}                 265
${Vendor-ID type}                           266
${Firmware-revision type}                   267
${Result-Code type}                         268
${Product-Name type}                        269
${Origin-State type}                        278
${Origin-Realm type}                        296

*** Test cases ***
Diameter
    Define Diameter protocol and message templates
    Start server
    Start client
    Client sends CER      vendorId.value.id:42
    Server receives CER
    Server sends CEA
    ${msg}=   Client receives CEA
    Should be equal as integers    ${msg.avps.result[0].value.code}    2001

*** Keywords ***
Populate CER-CEA default values
    Value      originHost.value.ident               example
    Value      originRealm.value.ident              foo.example.com
    IP Value   hostIP.value.address                 10.0.0.1
    Value      vendorId.value.id                    11111
    Value      productName.value.name               Rammbock Diameter Stack
    Value      supportedVendorId[0].value.id        11112
    Value      supportedVendorId[1].value.id        11113
    Value      supportedVendorId[2].value.id        11114
    Value      firmware.flags.Mandatory             0
    Value      firmware.value.revision              1

Populate default values for CER
    Populate CER-CEA default values
    Value      appId.value.vendorId.value.id        11115
    Value      appId.value.authApplicationId.value.id   0x01000000


Populate default values for CEA
    Populate CER-CEA default values
    Value      result.value.code                    2001
    Value      appId.*                              11115
    Value      appId[0].value.authApplicationId.value.id   0x01000000
    Value      appId[1].value.authApplicationId.value.id   0x01000005
    Value      appId[2].value.authApplicationId.value.id   0x01000031
    Value      appId[3].value.authApplicationId.value.id   0x01000023
    Value      appId[4].value.authApplicationId.value.id   0x01000001
    Value      appId[5].value.authApplicationId.value.id   0x01000003
    Value      originState.value.id                 1380800502


Start server
    Start TCP Server    localhost   3868    protocol=Diameter

Start client
    Start TCP Client    protocol=Diameter
    Connect	     localhost      3868
    Accept connection

Client sends CER
    [Arguments]       @{parameters}
    Load template    CER
    Populate default values for CER
    Client sends message      @{parameters}

Server receives CER
    Load template    CER
    Value   firmware.flags.Mandatory       0
    Server receives message

Server sends CEA
    [Arguments]       @{parameters}
    Load template    CEA send
    Populate default values for CEA
    Server sends message      @{parameters}

Client receives CEA
    Load template    CEA receive
    ${msg}=   Client receives message
    [return]   ${msg}

Define Diameter protocol and message templates
    Define Diameter Protocol
    Define CER Message
    Define CEA Message for sending
    Define CEA Message for receiving

Define diameter protocol
    New protocol    Diameter
    u8      message version        0x01
    u24     message length
    Diameter flags
    u24     command_code
    u32     application id         0
    u32     Hop-By-Hop Identifier  0xe36006e2
    u32     End-To-End Identifier  0x00003bab
    pdu     message length-20
    End protocol

Diameter flags
    New binary container    flags
    bin   1    Request           0
    bin   1    Proxyable         0
    bin   1    Error             0
    bin   1    T                 0
    bin   4    reserved          0
    End binary container

Define CER message
    New message  CER  Diameter  header:flags.Request:1  header:command_code:257
    AVP     originHost      Origin-Host
    AVP     originRealm     Origin-Realm
    AVP     hostIP          Host-IP-Address
    AVP     vendorId        Vendor-ID
    AVP     productName     Product-Name
    Array  3  AVP  supportedVendorId  Supported-Vendor-ID
    AVP     appId           Vendor-Specific-Application-Id
    AVP     firmware        Firmware-revision
    Populate default values for CER
    Save template           CER

Define CEA message for sending
    New message  CEA  Diameter  header:command_code:257
    AVP    result           Result-Code
    AVP    originHost       Origin-Host
    AVP    originRealm      Origin-Realm
    AVP    hostIP           Host-IP-Address
    AVP    vendorId         Vendor-ID
    AVP    productName      Product-Name
    Array  3  AVP  supportedVendorId    Supported-Vendor-ID
    Array  6  AVP  appId                Vendor-Specific-Application-Id
    AVP    originState      Origin-State
    AVP    firmware         Firmware-revision       mandatory=0
    Save template           CEA send

Define CEA message for receiving
    New message  CEA  Diameter  header:command_code:257
    Start bag    avps
    Case   1    AVP    result           Result-Code
    Case   1    AVP    originHost       Origin-Host
    Case   1    AVP    originRealm      Origin-Realm
    Case   1    AVP    hostIP           Host-IP-Address
    Case   1    AVP    vendorId         Vendor-ID
    Case   1    AVP    productName      Product-Name
    Case   *    AVP    supportedVendorId    Supported-Vendor-ID
    Case   *    AVP    appId                Vendor-Specific-Application-Id
    Case   0-1  AVP    originState      Origin-State
    Case   0-1  AVP    firmware         Firmware-revision    mandatory=0
    Case   *    AVP    unknown          Anything             mandatory=0
    End bag
    Save template           CEA receive

AVP
    [Arguments]     ${name}     ${type}    ${mandatory}=1
    New struct    AVP    ${name}           align=4
    ${type code}      Find type if defined or empty    ${type}
    AVP Header   ${type code}     ${mandatory}
    AVP value    ${type}
    End struct

AVP Header
    [Arguments]    ${type code}    ${mandatory}
    U32           AvpCode          ${type code}
    AVP Flags     ${mandatory}
    U24           avpLength

AVP flags
    [Arguments]    ${mandatory}
    New binary container    flags
    bin   1    Vendor-Specific   0
    bin   1    Mandatory         ${mandatory}
    bin   1    Protected         0
    bin   5    reserved          0
    End binary container

AVP Value
    [Arguments]    ${kw}
    new struct    Container    value    length=avpLength-8
    run keyword    ${kw}
    end struct

Origin-Realm
    Chars   *    ident

Origin-Host
    Chars   *    ident

Host-IP-Address
    u16    addressType   0x0001    # At the moment support only ipv4
    u32    address

Result-Code
    u32    code

Vendor-ID
    u32    id

Product-Name
    Chars   *   name

Supported-Vendor-ID
    u32    id

Vendor-Specific-Application-Id
    AVP    vendorId            Vendor-ID
    AVP    authApplicationId   Auth-Application-ID

Auth-Application-ID
    u32    id

Firmware-revision
    u32    revision

Origin-State
    u32     id

Anything
    Chars   *   bytes

IP Value
    [arguments]    ${field}    ${value}
    ${converted}=    convert to ip    ${value}
    Value    ${field}    ${converted}

Find type if defined or empty
    [Arguments]    ${name}
    ${type} =      Get variable value    ${${name}_type}     ${empty}
    [return]       ${type}

Set name
    [Arguments]    ${type}            ${name}
    ${result} =    Set variable if    """${name}"""    ${name}    ${type}
    [Return]       ${result}
