Feature: Register and login through the auth service
  Scenario: User registers and logs in successfully
    Given a unique user registration payload
    When I register via the auth service
    Then the registration is successful
    Given an existing user payload
    When I log in via the auth service
    Then a JWT token is returned
