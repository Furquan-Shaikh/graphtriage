package com.graphtriage.ticketing.service;

import com.graphtriage.ticketing.dto.TicketCreateRequest;
import com.graphtriage.ticketing.dto.TicketResponse;
import com.graphtriage.ticketing.entity.ServiceEntity;
import com.graphtriage.ticketing.entity.Ticket;
import com.graphtriage.ticketing.repository.ServiceRepository;
import com.graphtriage.ticketing.repository.TicketRepository;
import jakarta.persistence.EntityNotFoundException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TicketServiceTest {

    @Mock
    private TicketRepository ticketRepository;

    @Mock
    private ServiceRepository serviceRepository;

    @InjectMocks
    private TicketService ticketService;

    @Test
    void createTicket_reusesExistingService_whenServiceNameAlreadyExists() {
        ServiceEntity existingService = ServiceEntity.builder().id(1).name("payment-service").build();
        when(serviceRepository.findByName("payment-service")).thenReturn(Optional.of(existingService));

        Ticket savedTicket = Ticket.builder()
                .id(100)
                .title("Timeout")
                .description("desc")
                .service(existingService)
                .status("OPEN")
                .build();
        when(ticketRepository.save(any(Ticket.class))).thenReturn(savedTicket);

        TicketCreateRequest request = new TicketCreateRequest();
        request.setTitle("Timeout");
        request.setDescription("desc");
        request.setServiceName("payment-service");

        TicketResponse response = ticketService.createTicket(request);

        assertEquals(100, response.getId());
        assertEquals("payment-service", response.getServiceName());
        assertEquals("OPEN", response.getStatus());
    }

    @Test
    void createTicket_createsNewService_whenServiceNameDoesNotExist() {
        when(serviceRepository.findByName("new-service")).thenReturn(Optional.empty());
        ServiceEntity newService = ServiceEntity.builder().id(2).name("new-service").build();
        when(serviceRepository.save(any(ServiceEntity.class))).thenReturn(newService);

        Ticket savedTicket = Ticket.builder()
                .id(101)
                .title("Bug")
                .description("desc")
                .service(newService)
                .status("OPEN")
                .build();
        when(ticketRepository.save(any(Ticket.class))).thenReturn(savedTicket);

        TicketCreateRequest request = new TicketCreateRequest();
        request.setTitle("Bug");
        request.setDescription("desc");
        request.setServiceName("new-service");

        TicketResponse response = ticketService.createTicket(request);

        assertEquals("new-service", response.getServiceName());
    }

    @Test
    void getTicket_throwsEntityNotFound_whenTicketDoesNotExist() {
        when(ticketRepository.findById(999)).thenReturn(Optional.empty());

        assertThrows(EntityNotFoundException.class, () -> ticketService.getTicket(999));
    }
}
