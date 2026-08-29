from sih.resilience.rate_limiter import CircuitBreaker, CircuitState

def test_circuit_breaker_transition():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.1)
    assert cb.allow_request() is True
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False
