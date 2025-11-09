package com.parkingapp.service.impl;

import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;
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
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("El nombre de usuario ya existe");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("El email ya está en uso");
        }

        AccessCode code = accessCodeRepository.findByCode(request.getAccessCode())
                .orElseThrow(() -> new IllegalArgumentException("Código de acceso inválido"));

        if (code.isUsed()) {
            throw new IllegalArgumentException("El código ya fue usado");
        }

        if (code.getExpiresAt() != null && code.getExpiresAt().isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("El código ha expirado");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));

        Role role = roleRepository.findByName("ROLE_USER")
                .orElseThrow(() -> new IllegalStateException("ROLE_USER no existe"));
        user.getRoles().add(role);

        userRepository.save(user);

        code.setUsed(true);
        accessCodeRepository.save(code);
    }

    @Override
    public String login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );
        return jwtUtil.generateToken(request.getUsername());
    }
}
