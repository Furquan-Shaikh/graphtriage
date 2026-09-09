package com.graphtriage.ticketing.repository;

import com.graphtriage.ticketing.entity.Ticket;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface TicketRepository extends JpaRepository<Ticket, Integer> {
    List<Ticket> findByDatasetSplit(String datasetSplit);
}
