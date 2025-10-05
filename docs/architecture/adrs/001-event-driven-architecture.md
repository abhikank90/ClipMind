# ADR 001: Event-Driven Architecture

## Status
Accepted

## Context
Need to process videos asynchronously without blocking API responses.

## Decision
Use Celery with Redis for event-driven processing.

## Consequences

### Positive
- Scalable worker processes
- Retry mechanisms
- Decoupled services

### Negative
- Eventually consistent
- More complex debugging

## Alternatives Considered
- Synchronous processing (rejected - too slow)
- AWS Step Functions (rejected - higher cost)
