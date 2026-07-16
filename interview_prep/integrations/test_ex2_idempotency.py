import threading

import pytest

from interview_prep.integrations.ex2_idempotency import ChargeInProgress, charge, connect, setup_schema


@pytest.fixture
def db_path(tmp_path):
    """Ruta a una base ya migrada. Cada hilo abrira su propia conexion."""
    path = str(tmp_path / "payments.db")
    conn = connect(path)
    setup_schema(conn)
    conn.close()
    return path


@pytest.fixture
def conn(db_path):
    connection = connect(db_path)
    yield connection
    connection.close()


def make_gateway(fail_with=None):
    """Pasarela falsa que cuenta cuantas veces la han llamado."""
    calls = []
    lock = threading.Lock()

    def gateway():
        with lock:
            calls.append(1)
            n = len(calls)
        if fail_with is not None:
            raise fail_with
        return f"ch_{n}"

    gateway.calls = calls
    return gateway


def test_el_primer_cobro_llama_a_la_pasarela(conn):
    gateway = make_gateway()

    assert charge(conn, "key-1", 1000, gateway) == "ch_1"
    assert len(gateway.calls) == 1


def test_reintentar_con_la_misma_key_no_vuelve_a_cobrar(conn):
    # El corazon del ejercicio: esto es el reintento tras el timeout.
    gateway = make_gateway()

    primero = charge(conn, "key-1", 1000, gateway)
    segundo = charge(conn, "key-1", 1000, gateway)

    assert primero == segundo
    assert len(gateway.calls) == 1  # la pasarela solo se toco una vez


def test_keys_distintas_son_cobros_distintos(conn):
    gateway = make_gateway()

    primero = charge(conn, "key-1", 1000, gateway)
    segundo = charge(conn, "key-2", 1000, gateway)

    assert primero != segundo
    assert len(gateway.calls) == 2


def test_si_la_pasarela_falla_se_puede_reintentar_con_la_misma_key(conn):
    # Si el cobro fallo de verdad, la key no puede quedar bloqueada para
    # siempre: el reintento tiene que poder volver a intentarlo.
    fallando = make_gateway(fail_with=RuntimeError("gateway 503"))

    with pytest.raises(RuntimeError):
        charge(conn, "key-1", 1000, fallando)

    funcionando = make_gateway()
    assert charge(conn, "key-1", 1000, funcionando) == "ch_1"
    assert len(funcionando.calls) == 1


def test_diez_hilos_con_la_misma_key_cobran_una_sola_vez(db_path):
    # La carrera de verdad: reintentos concurrentes sobre la misma key.
    gateway = make_gateway()
    resultados = []
    errores = []
    lock = threading.Lock()

    def worker():
        conn = connect(db_path)  # cada hilo, su conexion
        try:
            result = charge(conn, "key-1", 1000, gateway)
            with lock:
                resultados.append(result)
        except ChargeInProgress as exc:
            with lock:
                errores.append(exc)
        finally:
            conn.close()

    hilos = [threading.Thread(target=worker) for _ in range(10)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    # Lo unico innegociable: al cliente se le cobro UNA vez.
    assert len(gateway.calls) == 1
    # Quien obtuvo respuesta, obtuvo la misma. El resto vio ChargeInProgress,
    # que es lo que devuelve Stripe (409) ante reintentos simultaneos.
    assert len(set(resultados)) == 1
    assert len(resultados) + len(errores) == 10
