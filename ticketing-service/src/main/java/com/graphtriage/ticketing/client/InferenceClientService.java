package com.graphtriage.ticketing.client;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Map;

/**
 * Calls the Python inference-service internally, per architecture.md
 * Section 2: Spring Boot owns the public API and business logic, and calls
 * a small Python inference microservice internally for ML predictions,
 * similarity retrieval, and explanations.
 *
 * Uses the "inferenceRestClient" bean defined in RestClientConfig, which is
 * configured to avoid an HTTP/2-upgrade compatibility issue with Uvicorn.
 */
@Service
@Slf4j
public class InferenceClientService {

    private final RestClient restClient;

    public InferenceClientService(RestClient inferenceRestClient) {
        this.restClient = inferenceRestClient;
    }

    public Map<String, Object> predict(String text) {
        return callInferenceEndpoint("/predict", text);
    }

    public Map<String, Object> similar(String text) {
        return callInferenceEndpoint("/similar", text);
    }

    public Map<String, Object> explain(String text) {
        return callInferenceEndpoint("/explain", text);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callInferenceEndpoint(String path, String text) {
        try {
            return restClient.post()
                    .uri(path)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(Map.of("text", text))
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException e) {
            // Per architecture.md Section 12 (Failure Modes & Resilience):
            // inference-service being down should degrade gracefully rather
            // than crash the whole request with an unhandled 500.
            log.error("Inference service call to {} failed: {}", path, e.getMessage());
            throw new InferenceServiceUnavailableException("Inference service is unavailable", e);
        }
    }
}
