package com.graphtriage.ticketing;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Day 1 smoke test: confirms the Spring application context loads successfully.
 * More meaningful tests (controller/service layer) get added from Day 7 onward,
 * per rules.md Section 7 (Testing Requirements).
 */
@SpringBootTest
class TicketingServiceApplicationTests {

    @Test
    void contextLoads() {
        // If the application context fails to start, this test fails.
    }
}
