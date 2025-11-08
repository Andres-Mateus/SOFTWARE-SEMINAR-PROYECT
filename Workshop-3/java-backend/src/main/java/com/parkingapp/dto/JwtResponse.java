package com.parkingapp.dto;

/**
 * Authentication response payload returned after successful login.
 */
public class JwtResponse {

    private final String token;
    private final String type;

    public JwtResponse(String token, String type) {
        this.token = token;
        this.type = type;
    }

    public JwtResponse(String token) {
        this(token, "Bearer");
    }

    public String getToken() {
        return token;
    }

    public String getType() {
        return type;
    }
}
