package com.parkingapp.controller;

import com.parkingapp.model.AccessCode;
import com.parkingapp.repository.AccessCodeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.UUID;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {
    private final AccessCodeRepository accessCodeRepository;

    @PostMapping("/access-code/generate")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<?> generateAccessCode() {
        String code = "REGISTER-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        AccessCode ac = new AccessCode();
        ac.setCode(code);
        ac.setUsed(false);
        ac.setExpiresAt(LocalDateTime.now().plusDays(30));
        accessCodeRepository.save(ac);
        return ResponseEntity.ok(ac);
    }
}
