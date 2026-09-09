package com.graphtriage.ticketing.dto;

import lombok.Data;

/** Request body for POST /api/tickets — matches design.md Section 4.1. */
@Data
public class TicketCreateRequest {
    private String title;
    private String description;
    private String serviceName;
    private String priority;
}
