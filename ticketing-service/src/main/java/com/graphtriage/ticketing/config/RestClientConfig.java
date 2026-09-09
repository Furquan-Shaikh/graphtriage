package com.graphtriage.ticketing.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

/**
 * Provides the RestClient bean used to call the inference-service internally.
 *
 * Uses SimpleClientHttpRequestFactory (backed by java.net.HttpURLConnection)
 * rather than the JDK's newer HttpClient. The newer client defaults to
 * attempting an HTTP/2 upgrade, which Uvicorn (the inference-service's ASGI
 * server) misinterprets as a WebSocket upgrade attempt - this caused POST
 * request bodies to arrive empty (422 "Field required: body"). This factory
 * always speaks plain HTTP/1.1, avoiding that issue entirely.
 */
@Configuration
public class RestClientConfig {

    @Value("${inference.service.url}")
    private String inferenceServiceUrl;

    @Bean
    public RestClient inferenceRestClient() {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(5000);
        requestFactory.setReadTimeout(120000);

        return RestClient.builder()
                .requestFactory(requestFactory)
                .baseUrl(inferenceServiceUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader(HttpHeaders.ACCEPT, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }
}
