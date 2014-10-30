*** Settings ***
Library         OperatingSystem
default tags    regression

*** Variables ***
${UNIT TEST DIR}=    ${CURDIR}${/}..${/}utest

*** Test Cases ***
Execute unit tests
    ${rc}  ${output}  Run And Return Rc And Output  nosetests --cover-erase --with-coverage --with-xunit --xunit-file=nose-out.xml --where ${UNIT TEST DIR}
    Should Be Equal As Integers  ${rc}  0   ${output}

Execute pep8 without line length check
    ${rc}  ${output}  Run And Return Rc And Output  pep8 --exclude decorator.py --ignore=E501 src/ atest/ utest/
    Should Be Equal As Integers  ${rc}  0   ${output}
