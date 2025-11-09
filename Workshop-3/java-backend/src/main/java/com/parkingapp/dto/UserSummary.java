package com.parkingapp.dto;

import java.util.Set;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class UserSummary {
    private final String username;
    private final String email;
    private final String role;
    private final Set<String> roles;
}
