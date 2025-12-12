package com.parkingapp.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.parkingapp.dto.LoginRequest;
import com.parkingapp.dto.RegisterRequest;
import com.parkingapp.model.Role;
import com.parkingapp.model.User;
import com.parkingapp.repository.RoleRepository;
import com.parkingapp.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
        roleRepository.findByName("ROLE_USER").orElseGet(() -> {
            Role role = new Role();
            role.setName("ROLE_USER");
            return roleRepository.save(role);
        });
    }

    @Test
    void register_returnsTokenAndUser() throws Exception {
        RegisterRequest request = new RegisterRequest();
        request.setUsername("john");
        request.setEmail("john@example.com");
        request.setPassword("secret");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.access_token").exists())
                .andExpect(jsonPath("$.user.email").value("john@example.com"))
                .andExpect(jsonPath("$.user.username").value("john"));

        assertThat(userRepository.findByEmail("john@example.com")).isPresent();
    }

    @Test
    void register_failsWhenEmailExists() throws Exception {
        Role role = roleRepository.findByName("ROLE_USER").orElseThrow();

        User existing = new User();
        existing.setUsername("john");
        existing.setEmail("john@example.com");
        existing.setPassword(passwordEncoder.encode("secret"));
        existing.getRoles().add(role);
        userRepository.save(existing);

        RegisterRequest request = new RegisterRequest();
        request.setUsername("johnny");
        request.setEmail("john@example.com");
        request.setPassword("another");

        org.assertj.core.api.Assertions.assertThatThrownBy(() ->
                mockMvc.perform(
                        MockMvcRequestBuilders.post("/api/auth/register")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request))
                ).andReturn()
        )
        .hasRootCauseInstanceOf(IllegalArgumentException.class)
        .hasRootCauseMessage("Email already in use");
    }

    @Test
    void login_returnsTokenForExistingUser() throws Exception {
        Role role = roleRepository.findByName("ROLE_USER").orElseThrow();
        User user = new User();
        user.setUsername("alice");
        user.setEmail("alice@example.com");
        user.setPassword(passwordEncoder.encode("password"));
        user.getRoles().add(role);
        userRepository.save(user);

        LoginRequest request = new LoginRequest();
        request.setEmail("alice@example.com");
        request.setPassword("password");

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.access_token").isNotEmpty())
                .andExpect(jsonPath("$.user.username").value("alice"))
                .andExpect(jsonPath("$.user.email").value("alice@example.com"));
    }

    @Test
    void login_failsWithBadCredentials() throws Exception {
        Role role = roleRepository.findByName("ROLE_USER").orElseThrow();
        User user = new User();
        user.setUsername("bob");
        user.setEmail("bob@example.com");
        user.setPassword(passwordEncoder.encode("correct"));
        user.getRoles().add(role);
        userRepository.save(user);

        LoginRequest request = new LoginRequest();
        request.setEmail("bob@example.com");
        request.setPassword("wrong");

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(MockMvcResultMatchers.status().isForbidden());
    }
}
