package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.ServiceEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ServiceRepository extends JpaRepository<ServiceEntity, Integer> {
    Optional<ServiceEntity> findByName(String name);
}
