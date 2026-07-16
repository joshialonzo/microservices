import pytest

from interview_prep.integrations.ex1_retries import (
    DeadlineExceeded,
    PermanentError,
    RetriesExhausted,
    TransientError,
    retry,
)


class FakeClock:
    """Reloj y sleep falsos: los tests corren instantaneos y deterministas."""

    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.t += seconds


def make_fn(*outcomes):
    """Devuelve una fn() que produce cada outcome en orden.

    Si el outcome es una excepcion, la lanza. Si no, la devuelve.
    """
    calls = []

    def fn():
        outcome = outcomes[len(calls)]
        calls.append(outcome)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    fn.calls = calls
    return fn


def test_devuelve_el_valor_si_va_bien_a_la_primera():
    fn = make_fn("ok")
    clock = FakeClock()

    assert retry(fn, sleep=clock.sleep, now=clock.now) == "ok"
    assert len(fn.calls) == 1
    assert clock.sleeps == []  # no durmio: no hubo fallo


def test_reintenta_los_errores_pasajeros_y_acaba_bien():
    fn = make_fn(TransientError("503"), TransientError("503"), "ok")
    clock = FakeClock()

    assert retry(fn, sleep=clock.sleep, now=clock.now) == "ok"
    assert len(fn.calls) == 3


def test_no_reintenta_los_errores_permanentes():
    # Lo mas importante del ejercicio: un 400 no se arregla repitiendolo.
    fn = make_fn(PermanentError("400 bad request"), "ok")
    clock = FakeClock()

    with pytest.raises(PermanentError):
        retry(fn, sleep=clock.sleep, now=clock.now)

    assert len(fn.calls) == 1  # solo se llamo una vez
    assert clock.sleeps == []


def test_se_rinde_tras_agotar_los_intentos():
    fn = make_fn(*[TransientError("503")] * 3)
    clock = FakeClock()

    with pytest.raises(RetriesExhausted):
        retry(fn, attempts=3, sleep=clock.sleep, now=clock.now)

    assert len(fn.calls) == 3
    assert len(clock.sleeps) == 2  # duerme entre intentos, no tras el ultimo


def test_el_backoff_crece_exponencialmente_y_topa_en_max_delay():
    fn = make_fn(*[TransientError("503")] * 5)
    clock = FakeClock()

    with pytest.raises(RetriesExhausted):
        retry(
            fn,
            attempts=5,
            base_delay=0.1,
            max_delay=0.3,
            sleep=clock.sleep,
            now=clock.now,
            jitter=lambda: 1.0,  # jitter fijo para poder comparar
        )

    # 0.1, 0.2, 0.4 -> topado a 0.3, 0.8 -> topado a 0.3
    assert clock.sleeps == [0.1, 0.2, 0.3, 0.3]


def test_el_jitter_reparte_las_esperas():
    fn = make_fn(*[TransientError("503")] * 3)
    clock = FakeClock()

    with pytest.raises(RetriesExhausted):
        retry(
            fn,
            attempts=3,
            base_delay=1.0,
            sleep=clock.sleep,
            now=clock.now,
            jitter=lambda: 0.5,  # media espera
        )

    assert clock.sleeps == [0.5, 1.0]


def test_el_deadline_corta_antes_de_dormir_de_mas():
    fn = make_fn(*[TransientError("503")] * 5)
    clock = FakeClock()

    # Presupuesto de 0.15s: cabe la primera espera (0.1) pero no la segunda.
    with pytest.raises(DeadlineExceeded):
        retry(
            fn,
            attempts=5,
            base_delay=0.1,
            deadline=0.15,
            sleep=clock.sleep,
            now=clock.now,
            jitter=lambda: 1.0,
        )

    assert clock.sleeps == [0.1]
