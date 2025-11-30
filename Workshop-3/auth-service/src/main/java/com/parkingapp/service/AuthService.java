package com.parkingapp.service;

import com.parkingapp.dto.AuthResponse;
import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;

public interface AuthService {
    AuthResponse register(RegisterRequest request);
    AuthResponse login(LoginRequest request);
}
