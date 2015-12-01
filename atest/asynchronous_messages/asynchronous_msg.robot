*** Settings ***
Library     Process
Resource    async_resources.robot
Test Setup     Setup protocol, nodes, and define templates
Test teardown    Teardown rammbock and increment port numbers
Force tags    regression
Test timeout    60s

*** Test cases ***
Register an auto reply
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.handle_sample     header_filter=messageType
    Server sends sample message
    Server sends another message
    Client receives another message
    Handler should have been called with '1' sample messages
    Message cache should be empty
Respond to an asynchronous message
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.respond_to_sample    header_filter=messageType
    Server sends sample message
    Server sends another message
    Client receives another message
    Server should receive response to sample
Multiple clients
    [Setup]   Setup protocol, server, two clients, and define templates
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.respond_to_sample    name=ExampleClient2    header_filter=messageType
    Server sends sample message   Connection1
    Server sends another message  Connection1
    Client receives another message    name=ExampleClient1
    Sample message should be in cache   name=ExampleClient1
    Server sends sample message   Connection2
    Server sends another message  Connection2
    Client receives another message    name=ExampleClient2
    Server should receive response to sample
Asynchronous messages on background
    [Setup]    Setup protocol, one client, background server, and define templates      Serve on background
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.respond_to_sample     header_filter=messageType
    Load template    another
    client sends message
    Wait until keyword succeeds     2s  0.1s  Handler should have been called with '1' sample messages
    client receives message    header_filter=messageType
    [Teardown]     Get background results and reset
100 asynchronous messages on background
    [Documentation]     This test is rather slow, so run with --exclude slow to skip this.
    [Tags]     slow
    [Setup]    Setup protocol, one client, background server, and define templates      Loop on background
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.respond_to_sample     header_filter=messageType     interval=0.01
    Repeat keyword   100    Send receive another
    Wait until keyword succeeds     20s  0.5s  Handler should have been called with '101' sample messages
    [Teardown]     Get background results and reset
Register an auto reply to work on background
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.handle_sample    header_filter=messageType
    Server sends sample message
    Wait until keyword succeeds   2s  0.1s   Handler should have been called with '1' sample messages
    Message cache should be empty
Timeout at background
    [timeout]    3s
    [Setup]    Setup protocol, one client, background server, and define templates  Send 10 messages every 0.5 seconds
    Load Template   sample
    Reset received messages
    Set client handler  my_handler.respond_to_sample    header_filter=messageType
    Load Template   another
    Run keyword and expect error  Timeout 0.6*  Client receives message   header_filter=messageType   timeout=0.6
    [Teardown]     Get background results and reset

*** Variables ***
${SOURCEDIR}=   ${CURDIR}${/}..${/}..${/}src
${BACKGROUND FILE}=    ${CURDIR}${/}background_server.robot

*** Keywords ***
Send receive another
    Load template    another
    client sends message
    client receives message     header_filter=messageType
Get background results and reset
    ${res}=    Terminate Process
    Log    STDOUT:\n${res.stdout}\nSTDERR:\n${res.stderr}
    log handler messages
    Teardown rammbock and increment port numbers
Setup protocol, one client, background server, and define templates
    [Arguments]    ${background operation}
    Define Example protocol
    Define templates
    Remove File     ${SIGNAL FILE}
    Start background process    ${background operation}
    Start TCP client    127.0.0.1   45555   name=client   protocol=Example
    Wait Until Created    ${SIGNAL FILE}     timeout=10 seconds
    sleep   0.1s     # Just to make sure we dont get inbetween keywordcalls
    Connect     127.0.0.1   ${SERVER PORT}
Setup protocol, server, two clients, and define templates
    Define protocol, start tcp server and two clients    protocol=Example
    Define templates
Setup protocol, nodes, and define templates
    Setup protocol, TCP server, and client
    Define Templates
Server sends sample message    [Arguments]    ${connection}=
    Load Template   sample
    Server sends message    connection=${connection}
Server sends another message   [Arguments]    ${connection}=
    Load Template   another
    Server sends message    connection=${connection}
Client receives another message
    [Arguments]     ${name}=
    Load Template   another
    Client receives message   name=${name}  header_filter=messageType
Server should receive response to sample
    Load Template   sample response
    Server receives message     timeout=1
Message cache should be empty
    ${my_count}=     Get Client Unread Messages Count
    Should be Equal as integers     ${my_count}     0
Sample message should be in cache
    [Arguments]     ${name}=
    ${my_count}=     Get Client Unread Messages Count   ${name}
    Should be Equal as integers     ${my_count}     1
Start background process
    [Arguments]     ${name}
    ${process}=    Start process  python  -m  robot.run  --test  ${name}  --loglevel   DEBUG
    ...            --variable  BACKGROUND:True   --variable  PORT:${SERVER PORT}  --pythonpath  ${SOURCEDIR}
    ...            --outputdir  ${TEMPDIR}  ${BACKGROUND FILE}
    [Return]    ${process}
