package com.parkingapp.dto;

import lombok.Getter;

@Getter
public class JwtResponse {
    private final String accessToken;
    private final String tokenType;
    private final UserSummary user;

    public JwtResponse(String accessToken, UserSummary user) {
        this.accessToken = accessToken;
        this.tokenType = "Bearer";
        this.user = user;
    }
}
