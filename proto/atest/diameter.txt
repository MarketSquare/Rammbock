*** Test cases ***


*** Keywords ***
Define diameter protocol
    Start Protocol Description    Diameter
    uint  1   message version        0x01
    uint  3   message length
    uint  1   message flags          0x80
    uint  3   command code           257
    uint  4   application id         0
    uint  4   Hop-By-Hop Identifier  0xe36006e2
    uint  4   End-To-End Identifier  0x00003bab
    pdu   message length-20
    End protocol description