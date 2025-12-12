Feature: Fetch parking overview
  Scenario: Dashboard shows occupancy metrics
    When I fetch the overview stats
    Then the occupancy metrics are returned
