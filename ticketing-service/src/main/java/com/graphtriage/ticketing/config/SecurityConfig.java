package com.graphtriage.ticketing.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Day 1 placeholder security config.
 *
 * For now: /api/health is public so we can verify the stack is up.
 * Everything else is left open too (permitAll) ONLY for the initial setup day -
 * this MUST be tightened to JWT-based auth in Day 7 (Backend Integration),
 * per architecture.md Section 10 (Security Architecture) and rules.md.
 *
 * Do not deploy this file as-is beyond Day 1-6 local development.
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/health").permitAll()
                // TODO (Day 7): replace this permitAll() with JWT-secured rules
                // once auth endpoints and the JWT filter are implemented.
                .anyRequest().permitAll()
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
