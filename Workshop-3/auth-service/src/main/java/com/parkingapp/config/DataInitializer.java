package com.parkingapp.config;

import com.parkingapp.model.AccessCode;
import com.parkingapp.model.Role;
import com.parkingapp.model.User;
import com.parkingapp.repository.AccessCodeRepository;
import com.parkingapp.repository.RoleRepository;
import com.parkingapp.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {
    private final RoleRepository roleRepository;
    private final UserRepository userRepository;
    private final AccessCodeRepository accessCodeRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        Role admin = roleRepository.findByName("ROLE_ADMIN").orElseGet(() -> roleRepository.save(new Role("ROLE_ADMIN")));
        Role user = roleRepository.findByName("ROLE_USER").orElseGet(() -> roleRepository.save(new Role("ROLE_USER")));

        if (!userRepository.existsByUsername("admin")) {
            User adminUser = new User();
            adminUser.setUsername("admin");
            adminUser.setEmail("admin@parking.com");
            adminUser.setPassword(passwordEncoder.encode("Admin@123"));
            adminUser.getRoles().add(admin);
            userRepository.save(adminUser);
            System.out.println("Admin user created: admin / Admin@123");
        }

        if (accessCodeRepository.count() == 0) {
            accessCodeRepository.save(new AccessCode("REGISTER-2025-01", false, LocalDateTime.now().plusDays(30)));
        }
    }
}
