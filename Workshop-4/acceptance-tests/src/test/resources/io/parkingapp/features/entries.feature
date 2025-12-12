Feature: Create parking entries
  Scenario: New vehicle entry reserves a slot
    Given a free parking slot with a random plate
    When I create a parking entry
    Then the entry is accepted with a slot assignment
