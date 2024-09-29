*** Settings ***
Test Setup        Setup TCP server and client
Test Teardown     Teardown rammbock and increment port numbers
Default Tags      Regression
Resource          Protocols.robot

*** Test cases ***
TCP Client sends binary to server
    Client sends binary    foo
    ${message}=    Server receives binary
    Should be equal as strings    ${message}    foo

TCP Server sends binary to client
    Server sends binary    foo
    ${message}=    Client receives binary
    Should be equal as strings    ${message}    foo

Multiple UDP clients
    [Setup]    Start two udp clients
    Start udp server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Connect two clients    ${SERVER PORT}    ${SERVER PORT}
    Two clients send foo and bar
    Server 'ExampleServer' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    Server 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'

Multiple UDP servers
    [Setup]    Start two udp clients
    Start udp server    ${SERVER}    ${SERVER PORT}    name=Server_1
    Start udp server    ${SERVER}    ${SERVER PORT 2}    name=Server_2
    Connect two clients    ${SERVER PORT}    ${SERVER PORT 2}
    Two clients send foo and bar
    Server 'Server_1' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    Server 'Server_2' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'

Multiple TCP clients
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Connect two clients and accept connections
    Two clients send foo and bar
    'Connection_1' on 'ExampleServer' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    'Connection_2' on 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'

Multiple TCP servers
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=Server_1
    Start tcp server    ${SERVER}    ${SERVER PORT 2}    name=Server_2
    Connect two clients and accept connections    Server_1    ${SERVER PORT}    Server_2    ${SERVER PORT 2}
    Two clients send foo and bar
    Server 'Server_1' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    Server 'Server_2' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'

SCTP Client sends binary to server
    [Tags]    ${EMPTY}
    [Setup]    Setup SCTP server and client
    Client sends binary    foo
    ${message}=    Server receives binary
    Should be equal    ${message}    foo

SCTP Server sends binary to client
    [Tags]    ${EMPTY}
    [Setup]    Setup SCTP server and client
    Server sends binary    foo
    ${message}=    Client receives binary
    Should be equal    ${message}    foo

Error for missing client
    [Setup]   Define example protocol
    Run keyword and expect error  No clients defined!   Client sends binary   foo

Error for missing server
    [Setup]   Define example protocol
    Run keyword and expect error  No servers defined!   Server sends binary   foo

Error for missing server connection
    [Setup]   Define example protocol
    Start TCP server    ${SERVER}    ${SERVER PORT}    protocol=Example
    Run keyword and expect error  No connections accepted!   Server receives binary

Timeouts failure when accepting connection
    [Setup]
    Start TCP server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Run Keyword and Expect Error   * timed out  Accept Connection    ExampleServer  alias_example   timeout=1

Timeouts when successfully accepting connection
    [Setup]
    Start TCP server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Start TCP client    name=ExampleClient
    connect    ${SERVER}    ${SERVER PORT}    name=ExampleClient
    Accept Connection    ExampleServer  alias_example   timeout=1

Multiple TCP Clients Closing Particular client and Switch Client
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Connect two clients and accept connections
    Two clients send foo and bar
    'Connection_1' on 'ExampleServer' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    'Connection_2' on 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'
    Close client 'Client_2' and switch to client 'Client_1'
    Client Sends binary    fooswitch
    'Connection_1' on 'ExampleServer' should get 'fooswitch' from '${CLIENT}':'${CLIENT 1 PORT}'

Multiple TCP Clients Closing Particular client and not performing switch client.
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Connect two clients and accept connections
    Two clients send foo and bar
    'Connection_1' on 'ExampleServer' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    'Connection_2' on 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'
    Close client    name=Client_2
    Client Sends binary   bar   name=Client_1
    'Connection_1' on 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 1 PORT}'

Multiple TCP Clients Closing Particlar client without Switch Client
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=ExampleServer
    Connect two clients and accept connections
    Two clients send foo and bar
    'Connection_1' on 'ExampleServer' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    'Connection_2' on 'ExampleServer' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'
    Close Client   name=Client_2
    Run keyword and expect error   *Bad file descriptor   Client Sends binary    fooswitch

Multiple TCP Clients and TCP Server with Close and Switch Client and Server
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=Server_1
    Start tcp server    ${SERVER}    ${SERVER PORT 2}    name=Server_2
    Connect two clients and accept connections    Server_1    ${SERVER PORT}    Server_2    ${SERVER PORT 2}
    Two clients send foo and bar
    Server 'Server_1' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    Server 'Server_2' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'
    Close server 'Server_2' and switch to server 'Server_1'
    Close client 'Client_2' and switch to client 'Client_1'
    Client Sends binary   bar
    Server 'Server_1' should get 'bar' from '${CLIENT}':'${CLIENT 1 PORT}'

Multiple TCP Servers and TCP Client with Close and not performing Switch Server
    [Setup]    Start two tcp clients
    Start tcp server    ${SERVER}    ${SERVER PORT}    name=Server_1
    Start tcp server    ${SERVER}    ${SERVER PORT 2}    name=Server_2
    Connect two clients and accept connections    Server_1    ${SERVER PORT}    Server_2    ${SERVER PORT 2}
    Two clients send foo and bar
    Server 'Server_1' should get 'foo' from '${CLIENT}':'${CLIENT 1 PORT}'
    Server 'Server_2' should get 'bar' from '${CLIENT}':'${CLIENT 2 PORT}'
    Close server    name=Server_2
    Client Sends binary   bar   name=Client_1
    Run keyword and expect error   *No connections accepted*    Server Receives Binary
    Server 'Server_1' should get 'bar' from '${CLIENT}':'${CLIENT 1 PORT}'