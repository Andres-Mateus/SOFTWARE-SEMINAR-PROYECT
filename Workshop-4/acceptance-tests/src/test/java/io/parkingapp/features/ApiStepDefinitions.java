package io.parkingapp.features;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.hamcrest.Matchers;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class ApiStepDefinitions {

    private static final String AUTH_BASE = System.getenv().getOrDefault("AUTH_BASE_URL", "http://localhost:8080/api/auth");
    private static final String CORE_BASE = System.getenv().getOrDefault("CORE_BASE_URL", "http://localhost:8000");

    private final Map<String, Object> payload = new HashMap<>();
    private Response lastResponse;
    private String authToken;
    private String plate;

    @Given("a unique user registration payload")
    public void a_unique_user_registration_payload() {
        String suffix = UUID.randomUUID().toString().substring(0, 8);
        payload.clear();
        payload.put("username", "user" + suffix);
        payload.put("email", "user" + suffix + "@example.com");
        payload.put("password", "Password123!");
    }

    @When("I register via the auth service")
    public void i_register_via_auth_service() {
        lastResponse = RestAssured.given()
                .contentType("application/json")
                .body(payload)
                .post(AUTH_BASE + "/register");
    }

    @Then("the registration is successful")
    public void the_registration_is_successful() {
        lastResponse.then()
                .statusCode(200)
                .body("access_token", Matchers.notNullValue())
                .body("user.email", Matchers.containsString("@"));
    }

    @Given("an existing user payload")
    public void an_existing_user_payload() {
        if (payload.isEmpty()) {
            a_unique_user_registration_payload();
            i_register_via_auth_service();
        }
        payload.clear();
        payload.put("email", lastResponse.jsonPath().getString("user.email"));
        payload.put("password", "Password123!");
    }

    @When("I log in via the auth service")
    public void i_log_in_via_the_auth_service() {
        lastResponse = RestAssured.given()
                .contentType("application/json")
                .body(payload)
                .post(AUTH_BASE + "/login");
        if (lastResponse.statusCode() == 200) {
            authToken = lastResponse.jsonPath().getString("access_token");
        }
    }

    @Then("a JWT token is returned")
    public void a_jwt_token_is_returned() {
        lastResponse.then()
                .statusCode(200)
                .body("access_token", Matchers.notNullValue())
                .body("user.username", Matchers.notNullValue());
    }

    @Given("a free parking slot with a random plate")
    public void a_free_parking_slot_with_a_random_plate() {
        plate = "ABC-" + UUID.randomUUID().toString().substring(0, 3).toUpperCase();
    }

    @When("I create a parking entry")
    public void i_create_a_parking_entry() {
        Map<String, Object> body = Map.of("plate", plate);
        lastResponse = RestAssured.given()
                .contentType("application/json")
                .body(body)
                .post(CORE_BASE + "/api/core/entries");
    }

    @Then("the entry is accepted with a slot assignment")
    public void the_entry_is_accepted_with_a_slot_assignment() {
        lastResponse.then()
                .statusCode(200)
                .body("plate", Matchers.notNullValue())
                .body("slot_code", Matchers.notNullValue());
    }

    @When("I request the parking exit")
    public void i_request_the_parking_exit() {
        Map<String, Object> body = Map.of("plate", plate);
        lastResponse = RestAssured.given()
                .contentType("application/json")
                .body(body)
                .post(CORE_BASE + "/api/core/exits");
    }

    @Then("I receive the receipt details")
    public void i_receive_the_receipt_details() {
        lastResponse.then()
                .statusCode(200)
                .body("minutes", Matchers.greaterThanOrEqualTo(1))
                .body("amount", Matchers.greaterThanOrEqualTo(0f));
    }

    @When("I fetch the overview stats")
    public void i_fetch_the_overview_stats() {
        lastResponse = RestAssured.get(CORE_BASE + "/api/core/stats/overview");
    }

    @Then("the occupancy metrics are returned")
    public void the_occupancy_metrics_are_returned() {
        lastResponse.then()
                .statusCode(200)
                .body("occupied", Matchers.greaterThanOrEqualTo(0))
                .body("free", Matchers.greaterThanOrEqualTo(0));
    }
}
