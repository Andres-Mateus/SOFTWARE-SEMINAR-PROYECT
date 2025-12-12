Feature: Complete parking exits
  Scenario: An active session can be closed
    Given a free parking slot with a random plate
    When I create a parking entry
    And I request the parking exit
    Then I receive the receipt details
