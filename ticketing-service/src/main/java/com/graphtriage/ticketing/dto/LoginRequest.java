package com.graphtriage.ticketing.dto;

import lombok.Data;

/** Request body for POST /api/auth/login — matches design.md Section 4.5. */
@Data
public class LoginRequest {
    private String username;
    private String password;
}
