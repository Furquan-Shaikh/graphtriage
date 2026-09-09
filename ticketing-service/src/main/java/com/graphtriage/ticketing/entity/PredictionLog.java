package com.graphtriage.ticketing.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

/** Maps to the `prediction_log` table (design.md Section 1). Logs every
 * prediction served, per rules.md Section 10 (Logging Standards) - needed
 * later for the evaluation/audit trail. */
@Entity
@Table(name = "prediction_log")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PredictionLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "ticket_id", nullable = false)
    private Integer ticketId;

    @Column(name = "predicted_service")
    private String predictedService;

    @Column(name = "predicted_root_cause")
    private String predictedRootCause;

    @Column(name = "predicted_resolution_hours")
    private Float predictedResolutionHours;

    private Float confidence;

    @Lob
    private String explanation;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }
}
