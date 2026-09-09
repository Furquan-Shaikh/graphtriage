package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.PredictionLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PredictionLogRepository extends JpaRepository<PredictionLog, Integer> {
}
