package com.graphtriage.ticketing.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Response body for GET /api/tickets/{id}/predict — matches design.md Section 4.2.
 * Note: /similar and /explain responses are proxied through as generic JSON
 * (Map/JsonNode) in the service layer (Step 4) rather than strictly-typed DTOs,
 * since they wrap the inference-service's response shape directly. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PredictionResponse {
    private Integer ticketId;
    private String predictedCategory;
    private Double predictedResolutionHours;
    private Double confidence;
}
