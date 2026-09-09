package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.Bug;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface BugRepository extends JpaRepository<Bug, Integer> {
    Optional<Bug> findByTicketId(Integer ticketId);
}
