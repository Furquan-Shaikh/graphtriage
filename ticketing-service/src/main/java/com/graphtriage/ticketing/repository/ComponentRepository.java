package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.Component;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ComponentRepository extends JpaRepository<Component, Integer> {
}
