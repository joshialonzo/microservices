import sqlite3
import threading

import pytest

from interview_prep.integrations.ex3_lost_update import (
    InsufficientFunds,
    connect,
    setup_schema,
    withdraw_atomic,
    withdraw_optimistic,
    withdraw_unsafe,
)

INICIAL = 10_000
RETIRO = 1_000
HILOS = 20
CABEN = INICIAL // RETIRO  # solo 10 retiros deberian pasar


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "bank.db")
    conn = connect(path)
    setup_schema(conn, INICIAL)
    conn.close()
    return path


@pytest.fixture
def conn(db_path):
    connection = connect(db_path)
    yield connection
    connection.close()


def balance_of(db_path):
    conn = connect(db_path)
    try:
        return conn.execute(
            "SELECT balance_cents FROM accounts WHERE id = 'acc-1'"
        ).fetchone()[0]
    finally:
        conn.close()


def run_concurrent_withdrawals(db_path, withdraw):
    """HILOS retiros simultaneos. Devuelve cuantos se dieron por buenos."""
    entregados = []
    lock = threading.Lock()

    def worker():
        conn = connect(db_path)  # cada hilo, su conexion
        try:
            withdraw(conn, "acc-1", RETIRO)
            with lock:
                entregados.append(RETIRO)
        except (InsufficientFunds, sqlite3.OperationalError):
            pass
        finally:
            conn.close()

    hilos = [threading.Thread(target=worker) for _ in range(HILOS)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return sum(entregados)


def test_un_retiro_normal_funciona(conn):
    assert withdraw_atomic(conn, "acc-1", 3_000) == 7_000


def test_sin_saldo_no_se_puede_retirar(conn):
    with pytest.raises(InsufficientFunds):
        withdraw_atomic(conn, "acc-1", 50_000)


def test_la_version_insegura_descuadra_las_cuentas(db_path):
    # Este test AFIRMA que el codigo con bug se rompe. Documenta el problema.
    entregado = run_concurrent_withdrawals(db_path, withdraw_unsafe)
    descontado = INICIAL - balance_of(db_path)

    # Se entrego mas dinero del que se descontó de la cuenta: dinero creado
    # de la nada. Ese hueco es el lost update.
    assert entregado > descontado


def test_el_update_atomico_cuadra(db_path):
    entregado = run_concurrent_withdrawals(db_path, withdraw_atomic)
    descontado = INICIAL - balance_of(db_path)

    assert entregado == descontado          # cuadra
    assert entregado == CABEN * RETIRO      # y solo salio lo que habia
    assert balance_of(db_path) == 0


def test_el_bloqueo_optimista_cuadra(db_path):
    entregado = run_concurrent_withdrawals(db_path, withdraw_optimistic)
    descontado = INICIAL - balance_of(db_path)

    assert entregado == descontado
    assert entregado == CABEN * RETIRO
    assert balance_of(db_path) == 0


def test_el_bloqueo_optimista_relee_tras_un_conflicto(conn):
    # Si al reintentar reutilizaras el balance viejo, reproducirias el bug.
    vistos = []

    def apply_rules(balance):
        vistos.append(balance)
        return balance

    withdraw_optimistic(conn, "acc-1", RETIRO, apply_rules=apply_rules)
    withdraw_optimistic(conn, "acc-1", RETIRO, apply_rules=apply_rules)

    assert vistos == [10_000, 9_000]  # el segundo vio el saldo ya actualizado
