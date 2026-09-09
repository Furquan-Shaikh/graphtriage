package com.graphtriage.ticketing.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Maps to the `fix` table (design.md Section 1). */
@Entity
@Table(name = "fix")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Fix {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "bug_id", nullable = false)
    private Integer bugId;

    @Lob
    private String description;

    @Column(name = "resolution_time_hours")
    private Float resolutionTimeHours;
}
