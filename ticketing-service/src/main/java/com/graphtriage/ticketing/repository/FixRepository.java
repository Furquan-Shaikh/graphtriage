package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.Fix;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface FixRepository extends JpaRepository<Fix, Integer> {
    Optional<Fix> findByBugId(Integer bugId);
}
