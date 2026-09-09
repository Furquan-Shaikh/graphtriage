package com.graphtriage.ticketing.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/** Maps to the `bug` table (design.md Section 1). Uses a plain ticketId
 * foreign key (not a @ManyToOne) - simple and avoids extra lazy-loading
 * complexity for this detail-record entity. */
@Entity
@Table(name = "bug")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Bug {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "ticket_id", nullable = false)
    private Integer ticketId;

    private String category;

    private String severity;
}
