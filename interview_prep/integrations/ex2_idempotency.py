"""Ejercicio 2 - Idempotencia y consistencia de datos.  (~45 min)

El escenario que SIEMPRE sale en entrevistas de integraciones:

    Llamas a la API de pagos. Se cobra correctamente... pero la respuesta se
    pierde por un timeout. Tu codigo del ejercicio 1 reintenta.
    Has cobrado dos veces al cliente.

Esta es la consecuencia incomoda de los reintentos: convierten tu sistema en
"at-least-once" (al menos una vez). No lo puedes evitar, porque una red que
se cae no te deja distinguir "no llego" de "llego pero se perdio el acuse".

La solucion NO es reintentar menos. Es hacer la operacion idempotente: que
ejecutarla N veces tenga el mismo efecto que ejecutarla una vez. Se hace con
una idempotency key que el CLIENTE genera y reenvia identica en cada
reintento, y una restriccion UNIQUE en la base que la haga cumplir.

    at-least-once + idempotencia = effectively-once

Nota sobre las conexiones: cada hilo abre la suya contra un fichero
compartido, como cada worker en produccion. Una conexion sqlite NO se puede
compartir entre hilos, y check_same_thread=False solo silencia el aviso.

Corre los tests:

    cd interview_prep
    ../task_manager/venv/bin/pytest test_ex2_idempotency.py -v
"""

import sqlite3


class ChargeInProgress(Exception):
    """Otro intento con esta misma key esta cobrando ahora mismo.

    Es lo que devuelve Stripe (409 Conflict) cuando le llegan dos reintentos
    simultaneos con la misma idempotency key. El cliente debe reintentar mas
    tarde, no cobrar por su cuenta.
    """


def connect(db_path):
    """Una conexion nueva. Cada hilo debe llamar a esto por su cuenta."""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")  # lectores y escritor a la vez
    return conn


def setup_schema(conn):
    """Crea la tabla de cobros.

    La clave del ejercicio esta en 'idempotency_key TEXT PRIMARY KEY'.

    Por que la restriccion y no un "SELECT ... si no existe, INSERT" en
    Python? Porque entre tu SELECT y tu INSERT cabe otro proceso haciendo lo
    mismo: es la misma condicion de carrera del task_manager, pero contra la
    base. La restriccion la garantiza la base, que si es atomica.
    Esto es exactamente lo que quieren oirte decir.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS charges (
            idempotency_key TEXT PRIMARY KEY,
            amount_cents    INTEGER NOT NULL,
            charge_id       TEXT,
            status          TEXT NOT NULL     -- 'pending' | 'succeeded'
        )
        """
    )
    conn.commit()


def charge(conn, idempotency_key, amount_cents, gateway):
    """Cobra amount_cents, como maximo una vez por idempotency_key.

    Args:
        conn: conexion sqlite propia de este hilo.
        idempotency_key: id unico del intento, generado por el cliente.
        amount_cents: importe en centimos (int, nunca float, ver TALKING_POINTS).
        gateway: callable() -> str que simula la pasarela y devuelve un
                 charge_id. Puede fallar o tardar.

    Returns:
        El charge_id. Si la key ya se cobro, devuelve el charge_id anterior
        SIN volver a llamar a gateway().

    Raises:
        ChargeInProgress: si otro intento con la misma key esta en curso.

    La pregunta clave es el ORDEN de las operaciones:
      - Si llamas a gateway() y luego insertas, y el INSERT falla: cobraste
        sin registrarlo. Cobras otra vez al reintentar. INACEPTABLE.
      - Si insertas y luego llamas a gateway(), y gateway() falla: tienes un
        registro de un cobro que no ocurrio, y la key queda bloqueada.
        Recuperable, si liberas la key al fallar.

    Por eso el patron es en tres fases: reservar la key -> cobrar -> confirmar.
    Se prefiere el error recuperable al irreversible. Di esto en la entrevista.
    """
    # ---- Fase 1: reservar la key ANTES de tocar la pasarela --------------
    # El INSERT es atomico, asi que de N intentos concurrentes exactamente uno
    # gana. Los demas se estrellan contra el PRIMARY KEY. Esta es la linea que
    # sustituye a un "if not existe" que seria una condicion de carrera.
    try:
        with conn:  # 'with conn' hace commit al salir, o rollback si peta
            conn.execute(
                "INSERT INTO charges (idempotency_key, amount_cents, status)"
                " VALUES (?, ?, 'pending')",
                (idempotency_key, amount_cents),
            )
    except sqlite3.IntegrityError:
        # Perdimos la carrera: la key ya existia. Dos casos muy distintos.
        charge_id, status = conn.execute(
            "SELECT charge_id, status FROM charges WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()

        if status == "succeeded":
            # AQUI aterriza el reintento del timeout: el cobro ya se hizo, le
            # devolvemos el mismo charge_id y NO tocamos la pasarela.
            return charge_id

        # status == 'pending': hay otro intento cobrando ahora mismo. No
        # podemos cobrar nosotros ni devolver un charge_id que aun no existe.
        raise ChargeInProgress(f"{idempotency_key} en curso")

    # ---- Fase 2: ganamos la reserva, cobramos de verdad -------------------
    try:
        charge_id = gateway()
    except Exception:
        # El cobro fallo de verdad: liberamos la key para que el reintento
        # pueda volver a intentarlo. Si la dejaramos en 'pending', esa key
        # quedaria envenenada para siempre.
        with conn:
            conn.execute(
                "DELETE FROM charges WHERE idempotency_key = ?",
                (idempotency_key,),
            )
        raise

    # ---- Fase 3: confirmar ------------------------------------------------
    # Si el proceso muere justo aqui, la fila queda en 'pending' con el cobro
    # ya hecho. Es el hueco que ningun diseño elimina del todo: por eso en
    # produccion se cierra con un job de reconciliacion contra el tercero.
    with conn:
        conn.execute(
            "UPDATE charges SET charge_id = ?, status = 'succeeded'"
            " WHERE idempotency_key = ?",
            (charge_id, idempotency_key),
        )
    return charge_id
