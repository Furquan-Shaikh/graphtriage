package com.graphtriage.ticketing.controller;

import com.graphtriage.ticketing.dto.LoginRequest;
import com.graphtriage.ticketing.dto.LoginResponse;
import com.graphtriage.ticketing.security.JwtService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Login endpoint — matches design.md Section 4.5.
 *
 * NOTE: This checks credentials against a single configured demo user
 * (app.demo-user.* in application.yml), not a real user database with
 * hashed-password storage. This is a deliberate scope simplification for
 * the academic project (see prd.md Section 6.2, Out of Scope) — a real
 * production system would never compare plaintext passwords like this.
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final JwtService jwtService;

    @Value("${app.demo-user.username}")
    private String demoUsername;

    @Value("${app.demo-user.password}")
    private String demoPassword;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        if (demoUsername.equals(request.getUsername()) && demoPassword.equals(request.getPassword())) {
            String token = jwtService.generateToken(request.getUsername());
            return ResponseEntity.ok(new LoginResponse(token));
        }
        return ResponseEntity.status(401).body(Map.of("error", "Invalid username or password"));
    }
}
