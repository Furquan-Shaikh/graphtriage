package com.graphtriage.ticketing.service;

import com.graphtriage.ticketing.dto.TicketCreateRequest;
import com.graphtriage.ticketing.dto.TicketResponse;
import com.graphtriage.ticketing.entity.ServiceEntity;
import com.graphtriage.ticketing.entity.Ticket;
import com.graphtriage.ticketing.repository.ServiceRepository;
import com.graphtriage.ticketing.repository.TicketRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * Business logic for ticket creation/retrieval, per rules.md Section 3.1
 * (controllers stay thin, delegate here).
 */
@Service
@RequiredArgsConstructor
public class TicketService {

    private final TicketRepository ticketRepository;
    private final ServiceRepository serviceRepository;

    public TicketResponse createTicket(TicketCreateRequest request) {
        ServiceEntity service = serviceRepository.findByName(request.getServiceName())
                .orElseGet(() -> serviceRepository.save(
                        ServiceEntity.builder().name(request.getServiceName()).build()));

        Ticket ticket = Ticket.builder()
                .title(request.getTitle())
                .description(request.getDescription())
                .service(service)
                .priority(request.getPriority())
                .build();

        Ticket saved = ticketRepository.save(ticket);
        return toResponse(saved);
    }

    public TicketResponse getTicket(Integer id) {
        Ticket ticket = ticketRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Ticket not found: " + id));
        return toResponse(ticket);
    }

    private TicketResponse toResponse(Ticket ticket) {
        return TicketResponse.builder()
                .id(ticket.getId())
                .title(ticket.getTitle())
                .description(ticket.getDescription())
                .serviceName(ticket.getService() != null ? ticket.getService().getName() : null)
                .status(ticket.getStatus())
                .priority(ticket.getPriority())
                .createdAt(ticket.getCreatedAt())
                .build();
    }
}
