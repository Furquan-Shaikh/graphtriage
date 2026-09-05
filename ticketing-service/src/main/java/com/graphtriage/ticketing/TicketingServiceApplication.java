package com.graphtriage.ticketing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the GraphTriage ticketing-service.
 * This is the public-facing Spring Boot API layer described in architecture.md.
 * It owns ticket CRUD + auth, and internally calls the Python inference-service
 * for predictions, similarity search, and explanations.
 */
@SpringBootApplication
public class TicketingServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(TicketingServiceApplication.class, args);
    }
}
