package com.graphtriage.ticketing.controller;

import com.graphtriage.ticketing.client.InferenceClientService;
import com.graphtriage.ticketing.client.InferenceServiceUnavailableException;
import com.graphtriage.ticketing.dto.TicketCreateRequest;
import com.graphtriage.ticketing.dto.TicketResponse;
import com.graphtriage.ticketing.service.TicketService;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** Ticket CRUD + ML endpoints — matches design.md Section 4. */
@RestController
@RequestMapping("/api/tickets")
@RequiredArgsConstructor
public class TicketController {

    private final TicketService ticketService;
    private final InferenceClientService inferenceClientService;

    @PostMapping
    public ResponseEntity<TicketResponse> createTicket(@RequestBody TicketCreateRequest request) {
        TicketResponse response = ticketService.createTicket(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TicketResponse> getTicket(@PathVariable Integer id) {
        return ResponseEntity.ok(ticketService.getTicket(id));
    }

    @GetMapping("/{id}/predict")
    public ResponseEntity<Map<String, Object>> predictTicket(@PathVariable Integer id) {
        String text = ticketText(id);
        return ResponseEntity.ok(inferenceClientService.predict(text));
    }

    @GetMapping("/{id}/similar")
    public ResponseEntity<Map<String, Object>> similarTickets(@PathVariable Integer id) {
        String text = ticketText(id);
        return ResponseEntity.ok(inferenceClientService.similar(text));
    }

    @GetMapping("/{id}/explain")
    public ResponseEntity<Map<String, Object>> explainTicket(@PathVariable Integer id) {
        String text = ticketText(id);
        return ResponseEntity.ok(inferenceClientService.explain(text));
    }

    private String ticketText(Integer id) {
        TicketResponse ticket = ticketService.getTicket(id);
        return ticket.getTitle() + ". " + ticket.getDescription();
    }

    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<Void> handleNotFound() {
        return ResponseEntity.notFound().build();
    }

    @ExceptionHandler(InferenceServiceUnavailableException.class)
    public ResponseEntity<Map<String, String>> handleInferenceUnavailable() {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "Inference service is currently unavailable. Please try again later."));
    }
}
