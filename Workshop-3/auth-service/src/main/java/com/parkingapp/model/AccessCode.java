package com.parkingapp.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "access_codes")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class AccessCode {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String code;

    private boolean used = false;

    private LocalDateTime expiresAt;

    public AccessCode(String code, boolean used, LocalDateTime expiresAt) {
        this.code = code;
        this.used = used;
        this.expiresAt = expiresAt;
    }
}
