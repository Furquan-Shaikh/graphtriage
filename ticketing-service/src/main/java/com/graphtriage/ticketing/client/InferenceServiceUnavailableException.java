package com.graphtriage.ticketing.client;

/** Thrown when the inference-service call fails, per architecture.md
 * Section 12 (Failure Modes & Resilience) — lets the controller degrade
 * gracefully instead of a raw 500. */
public class InferenceServiceUnavailableException extends RuntimeException {
    public InferenceServiceUnavailableException(String message, Throwable cause) {
        super(message, cause);
    }
}
