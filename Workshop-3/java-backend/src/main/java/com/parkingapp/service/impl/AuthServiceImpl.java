package com.parkingapp.service.impl;

import com.parkingapp.dto.JwtResponse;
import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;
import com.parkingapp.dto.UserSummary;
import com.parkingapp.model.AccessCode;
import com.parkingapp.model.Role;
import com.parkingapp.model.User;
import com.parkingapp.repository.AccessCodeRepository;
import com.parkingapp.repository.RoleRepository;
import com.parkingapp.repository.UserRepository;
import com.parkingapp.security.JwtUtil;
import com.parkingapp.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final AccessCodeRepository accessCodeRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;

    @Override
    @Transactional
    public void register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email address is already registered");
        }

        AccessCode code = accessCodeRepository.findByCode(request.getAccessCode())
                .orElseThrow(() -> new IllegalArgumentException("Invalid access code"));

        if (code.isUsed()) {
            throw new IllegalArgumentException("The access code has already been used");
        }

        if (code.getExpiresAt() != null && code.getExpiresAt().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("The access code has expired");
        }

        String username = request.getUsername();
        if (username == null || username.isBlank()) {
            String base = request.getEmail().split("@")[0];
            String candidate = base;
            int suffix = 1;
            while (userRepository.existsByUsername(candidate)) {
                candidate = base + suffix;
                suffix++;
            }
            username = candidate;
        } else if (userRepository.existsByUsername(username)) {
            throw new IllegalArgumentException("Username already exists");
        }

        User user = new User();
        user.setUsername(username);
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        Role role = roleRepository.findByName("ROLE_USER")
                .orElseThrow(() -> new IllegalStateException("ROLE_USER is not configured"));
        user.getRoles().add(role);

        userRepository.save(user);

        code.setUsed(true);
        accessCodeRepository.save(code);
    }

    @Override
    public JwtResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new IllegalArgumentException("User not found"));

        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(user.getUsername(), request.getPassword())
        );

        String token = jwtUtil.generateToken(user.getUsername());
        var roles = user.getRoles().stream().map(Role::getName).collect(Collectors.toSet());
        String primaryRole = roles.stream().findFirst().orElse("ROLE_USER");

        UserSummary summary = new UserSummary(
                user.getUsername(),
                user.getEmail(),
                primaryRole,
                roles
        );
        return new JwtResponse(token, summary);
    }
}
