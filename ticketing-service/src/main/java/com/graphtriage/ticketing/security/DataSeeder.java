package com.graphtriage.ticketing.security;

import com.graphtriage.ticketing.entity.User;
import com.graphtriage.ticketing.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * TEST-ONLY: seeds one demo user on startup so login can be tested right
 * away without a separate register endpoint. Remove this class (or gate
 * it behind a "dev" profile) before any real/shared deployment — it
 * exists purely for local testing.
 *
 * Demo credentials: username = demo_user, password = ChangeMe123!
 */
@Component
@RequiredArgsConstructor
public class DataSeeder implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (userRepository.findByUsername("demo_user").isEmpty()) {
            User user = User.builder()
                    .username("demo_user")
                    .password(passwordEncoder.encode("ChangeMe123!"))
                    .role("USER")
                    .build();
            userRepository.save(user);
        }
    }
}