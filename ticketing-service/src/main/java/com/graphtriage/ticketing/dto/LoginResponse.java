package com.graphtriage.ticketing.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Response body for POST /api/auth/login — matches design.md Section 4.5. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {
    private String token;
}
