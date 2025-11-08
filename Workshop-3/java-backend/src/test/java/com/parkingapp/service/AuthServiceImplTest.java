package com.parkingapp.service;

import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;
import com.parkingapp.model.AccessCode;
import com.parkingapp.model.Role;
import com.parkingapp.repository.AccessCodeRepository;
import com.parkingapp.repository.RoleRepository;
import com.parkingapp.repository.UserRepository;
import com.parkingapp.security.JwtUtil;
import com.parkingapp.service.impl.AuthServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.*;

class AuthServiceImplTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private RoleRepository roleRepository;

    @Mock
    private AccessCodeRepository accessCodeRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private AuthenticationManager authenticationManager;

    @Mock
    private JwtUtil jwtUtil;

    private AuthServiceImpl authService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        authService = new AuthServiceImpl(
                userRepository,
                roleRepository,
                accessCodeRepository,
                passwordEncoder,
                authenticationManager,
                jwtUtil
        );
    }

    @Test
    void registerCreatesUserAndMarksCodeAsUsed() {
        RegisterRequest request = new RegisterRequest();
        request.setUsername("newuser");
        request.setEmail("newuser@example.com");
        request.setPassword("password123");
        request.setAccessCode("CODE123");

        when(userRepository.existsByUsername("newuser")).thenReturn(false);
        when(userRepository.existsByEmail("newuser@example.com")).thenReturn(false);

        AccessCode accessCode = new AccessCode();
        accessCode.setCode("CODE123");
        accessCode.setUsed(false);
        accessCode.setExpiresAt(LocalDateTime.now().plusDays(1));
        when(accessCodeRepository.findByCode("CODE123")).thenReturn(Optional.of(accessCode));

        Role role = new Role();
        role.setName("ROLE_USER");
        when(roleRepository.findByName("ROLE_USER")).thenReturn(Optional.of(role));

        when(passwordEncoder.encode("password123")).thenReturn("encoded-password");

        authService.register(request);

        ArgumentCaptor<com.parkingapp.model.User> userCaptor = ArgumentCaptor.forClass(com.parkingapp.model.User.class);
        verify(userRepository).save(userCaptor.capture());
        com.parkingapp.model.User savedUser = userCaptor.getValue();

        assertThat(savedUser.getUsername()).isEqualTo("newuser");
        assertThat(savedUser.getEmail()).isEqualTo("newuser@example.com");
        assertThat(savedUser.getPassword()).isEqualTo("encoded-password");
        assertThat(savedUser.getRoles()).contains(role);
        assertThat(accessCode.isUsed()).isTrue();
        verify(accessCodeRepository).save(accessCode);
    }

    @Test
    void registerThrowsWhenUsernameAlreadyExists() {
        RegisterRequest request = new RegisterRequest();
        request.setUsername("existing");
        request.setEmail("existing@example.com");

        when(userRepository.existsByUsername("existing")).thenReturn(true);

        assertThatThrownBy(() -> authService.register(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("El nombre de usuario ya existe");

        verify(userRepository, never()).save(any());
    }

    @Test
    void loginAuthenticatesAndReturnsToken() {
        LoginRequest request = new LoginRequest();
        request.setUsername("john");
        request.setPassword("secret");

        when(jwtUtil.generateToken("john")).thenReturn("jwt-token");

        String token = authService.login(request);

        assertThat(token).isEqualTo("jwt-token");
        ArgumentCaptor<UsernamePasswordAuthenticationToken> captor =
                ArgumentCaptor.forClass(UsernamePasswordAuthenticationToken.class);
        verify(authenticationManager).authenticate(captor.capture());
        UsernamePasswordAuthenticationToken authenticationToken = captor.getValue();
        assertThat(authenticationToken.getPrincipal()).isEqualTo("john");
        assertThat(authenticationToken.getCredentials()).isEqualTo("secret");
    }
}
