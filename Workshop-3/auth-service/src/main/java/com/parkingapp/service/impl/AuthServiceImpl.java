package com.parkingapp.service.impl;

import com.parkingapp.dto.AuthResponse;
import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;
import com.parkingapp.dto.UserDto;
import com.parkingapp.model.Role;
import com.parkingapp.model.User;
import com.parkingapp.repository.RoleRepository;
import com.parkingapp.repository.UserRepository;
import com.parkingapp.security.JwtUtil;
import com.parkingapp.service.AuthService;
import jakarta.transaction.Transactional;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;

    public AuthServiceImpl(UserRepository userRepository, RoleRepository roleRepository, PasswordEncoder passwordEncoder, AuthenticationManager authenticationManager, JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
    }

    @Override
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already in use");
        }
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        Role role = roleRepository.findByName("ROLE_USER")
                .orElseThrow(() -> new IllegalStateException("ROLE_USER not configured"));
        user.getRoles().add(role);

        User saved = userRepository.save(user);
        String token = jwtUtil.generateToken(saved.getEmail());
        return AuthResponse.builder()
                .access_token(token)
                .user(new UserDto(saved.getId(), saved.getUsername(), saved.getEmail()))
                .build();
    }

    @Override
    public AuthResponse login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword())
        );

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));

        String token = jwtUtil.generateToken(user.getEmail());
        return AuthResponse.builder()
                .access_token(token)
                .user(new UserDto(user.getId(), user.getUsername(), user.getEmail()))
                .build();
    }
}
