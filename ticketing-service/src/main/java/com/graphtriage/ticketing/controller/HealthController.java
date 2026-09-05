package com.graphtriage.ticketing.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Simple health endpoint used to verify the Day 1 setup:
 * Spring Boot is up, reading config correctly, and (once wired) can be
 * confirmed alongside MySQL, Neo4j, and the inference-service being reachable.
 *
 * GET /api/health
 */
@RestController
public class HealthController {

    @Value("${inference.service.url:not-configured}")
    private String inferenceServiceUrl;

    @GetMapping("/api/health")
    public Map<String, Object> health() {
        Map<String, Object> response = new LinkedHashMap<>();
        response.put("service", "ticketing-service");
        response.put("status", "UP");
        response.put("timestamp", Instant.now().toString());
        response.put("inferenceServiceUrl", inferenceServiceUrl);
        return response;
    }
}
