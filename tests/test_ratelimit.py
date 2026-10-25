from schemebot.api.ratelimit import AskLimiter, RateLimiter


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_allows_up_to_the_limit_then_says_how_long_to_wait() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=2, window_s=60, clock=clock)

    assert limiter.check("a") is None
    clock.now += 10
    assert limiter.check("a") is None
    clock.now += 5

    assert limiter.check("a") == 45.0  # the first request leaves the window 45 s from now


def test_window_slides_so_old_requests_stop_counting() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=1, window_s=60, clock=clock)
    limiter.check("a")

    clock.now += 60

    assert limiter.check("a") is None


def test_clients_are_counted_separately() -> None:
    limiter = RateLimiter(limit=1, window_s=60, clock=Clock())
    limiter.check("a")

    assert limiter.check("b") is None


def test_a_refused_request_does_not_use_up_a_slot() -> None:
    clock = Clock()
    limiter = RateLimiter(limit=1, window_s=60, clock=clock)
    limiter.check("a")
    limiter.check("a")  # refused

    clock.now += 60

    assert limiter.check("a") is None


def test_total_daily_cap_applies_across_clients() -> None:
    limiter = AskLimiter(per_client_per_minute=5, total_per_day=2, clock=Clock())
    limiter.check("a")
    limiter.check("b")

    wait = limiter.check("c")

    assert wait is not None and wait > 3600
