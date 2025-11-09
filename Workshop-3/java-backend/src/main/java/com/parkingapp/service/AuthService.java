package com.parkingapp.service;

import com.parkingapp.dto.JwtResponse;
import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;

public interface AuthService {
    void register(RegisterRequest request);
    JwtResponse login(LoginRequest request);
}
