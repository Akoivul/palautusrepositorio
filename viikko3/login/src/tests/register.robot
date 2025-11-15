*** Settings ***
Resource  resource.robot
Suite Setup     Open And Configure Browser
Suite Teardown  Close Browser
Test Setup      Reset Application Create User And Go To Register Page

*** Test Cases ***

Register With Valid Username And Password
    Set Username  user1
    Set Password  password1
    Set Password Confirmation  password1
    Click Button  Register
    Registration Should Succeed

Register With Too Short Username And Valid Password
    Set Username  us
    Set Password  password2
    Set Password Confirmation  password2
    Click Button  Register
    Registration Should Fail With Message  Username has to be at least 3 characters long

Register With Valid Username And Too Short Password
    Set Username  user2
    Set Password  pass
    Set Password Confirmation  pass
    Click Button  Register
    Registration Should Fail With Message  Password has to be at least 8 characters long

Register With Valid Username And Invalid Password
    Set Username  user3
    Set Password  password
    Set Password Confirmation  password
    Click Button  Register
    Registration Should Fail With Message  Password has to include at least one non-letter character

Register With Nonmatching Password And Password Confirmation
    Set Username  user4
    Set Password  password3
    Set Password Confirmation  password1
    Click Button  Register
    Registration Should Fail With Message  Passwords do not match

Register With Username That Is Already In Use
    Set Username  kalle
    Set Password  password4
    Set Password Confirmation  password4
    Click Button  Register
    Registration Should Fail With Message  Username already exists

*** Keywords ***
Registration Should Succeed
    Welcome Page Should Be Open


Registration Should Fail With Message
    [Arguments]  ${message}
    Register Page Should Be Open
    Page Should Contain  ${message}

Reset Application Create User And Go To Register Page
    Reset Application
    Create User  kalle  kalle123
    Go To Register Page

Set Username
    [Arguments]  ${username}
    Input Text  username  ${username}

Set Password
    [Arguments]  ${password}
    Input Password  password  ${password}

Set Password Confirmation
    [Arguments]  ${password}
    Input Password  password_confirmation  ${password}