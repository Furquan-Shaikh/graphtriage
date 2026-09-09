package com.graphtriage.ticketing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/** Response body for ticket endpoints — matches design.md Section 4.1/4.2. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TicketResponse {
    private Integer id;
    private String title;
    private String description;
    private String serviceName;
    private String status;
    private String priority;
    private LocalDateTime createdAt;
}
