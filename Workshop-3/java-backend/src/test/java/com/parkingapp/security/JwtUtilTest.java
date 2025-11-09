package com.parkingapp.security;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest(classes = JwtUtil.class)
@TestPropertySource(properties = {
        "app.jwt.secret=0123456789ABCDEF0123456789ABCDEF",
        "app.jwt.expiration-ms=3600000"
})
class JwtUtilTest {

    @Autowired
    private JwtUtil jwtUtil;

    private String token;

    @BeforeEach
    void setUp() {
        token = jwtUtil.generateToken("user@example.com");
    }

    @Test
    void generatedTokenShouldExposeUsername() {
        assertThat(jwtUtil.extractUsername(token)).isEqualTo("user@example.com");
    }

    @Test
    void tamperedTokenShouldBeRejected() {
        String tampered = token.substring(0, token.length() - 2) + "aa";
        assertThat(jwtUtil.validateToken(token)).isTrue();
        assertThat(jwtUtil.validateToken(tampered)).isFalse();
    }
}
