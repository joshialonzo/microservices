"""Ejercicio 3 - Condiciones de carrera contra la base de datos.  (~45 min)

Es la MISMA carrera del task_manager, pero el estado compartido ya no es una
variable en memoria: es una fila. Y aqui el threading.Lock no te sirve, porque
los otros procesos que tocan esa fila corren en otra maquina.

El escenario: una cuenta con 100 euros y dos retiros de 100 simultaneos.

    Proceso A: SELECT balance -> 100. Hay saldo? Si.
    Proceso B: SELECT balance -> 100. Hay saldo? Si.
    Proceso A: UPDATE balance = 0     (entrega 100)
    Proceso B: UPDATE balance = 0     (entrega otros 100)

Los dos comprobaron el saldo correctamente. Los dos tenian razon. Y aun asi
se entregaron 200 euros de una cuenta de 100, y el saldo final dice 0.
A esto se le llama "lost update".

Fijate en el sintoma, porque es contraintuitivo: el saldo NO queda negativo.
Queda demasiado ALTO respecto al dinero entregado. El descuadre no se ve
mirando la fila; se ve al cuadrar lo entregado contra lo descontado.

Las dos soluciones que debes saber nombrar en la entrevista:

  1. UPDATE atomico condicional: dejar que la base compruebe y reste en una
     sola sentencia. Simple y rapido. Primera opcion siempre que la logica
     quepa en SQL.

  2. Bloqueo optimista (columna version): lees la fila con su version, y al
     escribir exiges que la version no haya cambiado. Si cambio, alguien te
     piso: reintentas. Se usa cuando la logica NO cabe en SQL (llamar a una
     API, aplicar reglas complejas, etc).

  Y la tercera, que conviene mencionar para demostrar que conoces el
  trade-off: el bloqueo pesimista (SELECT ... FOR UPDATE), que bloquea la
  fila. Correcto pero serializa y se presta a deadlocks. sqlite no lo
  soporta; Postgres si.

Corre los tests:

    cd interview_prep
    ../task_manager/venv/bin/pytest test_ex3_lost_update.py -v
"""

import sqlite3


class InsufficientFunds(Exception):
    """No hay saldo para este retiro."""


class ConcurrentModification(Exception):
    """Otro proceso modifico la fila; se agotaron los reintentos."""


def connect(db_path):
    """Una conexion nueva. Cada hilo debe llamar a esto por su cuenta."""
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def setup_schema(conn, initial_balance_cents):
    """Crea accounts con una cuenta 'acc-1' y su version a 0."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id             TEXT PRIMARY KEY,
            balance_cents  INTEGER NOT NULL,
            version        INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT INTO accounts VALUES ('acc-1', ?, 0)", (initial_balance_cents,)
    )
    conn.commit()


def withdraw_unsafe(conn, account_id, amount_cents):
    """La version con el bug. Ya esta escrita: leela, no la arregles.

    Su unico proposito es que el test demuestre el descuadre. Fijate en que
    NO hay nada obviamente mal: lee, comprueba, escribe. El bug es el hueco
    entre el SELECT y el UPDATE.
    """
    balance = conn.execute(
        "SELECT balance_cents FROM accounts WHERE id = ?", (account_id,)
    ).fetchone()[0]

    if balance < amount_cents:
        raise InsufficientFunds(f"saldo {balance}, pedido {amount_cents}")

    nuevo = balance - amount_cents
    with conn:
        conn.execute(
            "UPDATE accounts SET balance_cents = ? WHERE id = ?",
            (nuevo, account_id),
        )
    return nuevo


def withdraw_atomic(conn, account_id, amount_cents):
    """Solucion 1: que la base compruebe y reste en UNA sentencia.

    Returns:
        El saldo resultante.

    Raises:
        InsufficientFunds: si no habia saldo.
    """
    # Una sola sentencia. No hay hueco entre el SELECT y el UPDATE porque no
    # hay SELECT: la comprobacion del saldo vive en el WHERE, y la base la
    # evalua y aplica de forma atomica.
    #
    # Lo que lo salva es que la resta es RELATIVA: 'balance_cents - ?' lo
    # calcula la base sobre el valor real del momento. Si escribieramos
    # 'balance_cents = ?' con un numero calculado en Python, seria el bug otra
    # vez, aunque la sentencia pareciera igual de atomica.
    with conn:
        cursor = conn.execute(
            "UPDATE accounts SET balance_cents = balance_cents - ?,"
            " version = version + 1"
            " WHERE id = ? AND balance_cents >= ?",
            (amount_cents, account_id, amount_cents),
        )
        # rowcount == 0 significa que ninguna fila cumplia el WHERE, o sea que
        # no habia saldo. La base nos lo dice sin que tengamos que preguntarlo.
        if cursor.rowcount == 0:
            raise InsufficientFunds(f"sin saldo para {amount_cents}")

    return conn.execute(
        "SELECT balance_cents FROM accounts WHERE id = ?", (account_id,)
    ).fetchone()[0]


def withdraw_optimistic(conn, account_id, amount_cents, apply_rules=None,
                        max_retries=50):
    """Solucion 2: bloqueo optimista con columna version.

    Para cuando la logica NO cabe en SQL. apply_rules(balance) simula esa
    logica de negocio (llamar a una API antifraude, aplicar comisiones...).

    Args:
        apply_rules: callable(balance) -> balance_ajustado. Si es None, no
                     se aplica nada.
        max_retries: cuantas veces reintentar si otro nos pisa.

    Raises:
        InsufficientFunds / ConcurrentModification.
    """
    for _ in range(max_retries):
        # 1. Leer estado Y version juntos. La version es la foto del momento.
        balance, version = conn.execute(
            "SELECT balance_cents, version FROM accounts WHERE id = ?",
            (account_id,),
        ).fetchone()

        # 2. Aqui vive la logica que NO cabe en SQL: llamar a una API
        #    antifraude, aplicar comisiones, consultar reglas de negocio.
        #    Este es el unico motivo para preferir esto al UPDATE atomico.
        if apply_rules is not None:
            balance = apply_rules(balance)

        if balance < amount_cents:
            raise InsufficientFunds(f"saldo {balance}, pedido {amount_cents}")

        nuevo = balance - amount_cents

        # 3. Escribir SOLO si nadie toco la fila desde nuestro SELECT.
        #    El 'AND version = ?' es la apuesta: "creo que nadie me piso".
        #    De ahi el nombre "optimista": no bloqueamos nada, comprobamos
        #    al final si teniamos razon.
        with conn:
            cursor = conn.execute(
                "UPDATE accounts SET balance_cents = ?, version = version + 1"
                " WHERE id = ? AND version = ?",
                (nuevo, account_id, version),
            )

        if cursor.rowcount == 1:
            return nuevo  # ganamos la apuesta

        # 4. rowcount == 0: alguien escribio entre nuestro SELECT y nuestro
        #    UPDATE, y la version ya no coincide. Volvemos arriba a RELEER.
        #    Reintentar con el 'balance' viejo seria repetir el bug exacto
        #    que estamos evitando: por eso el bucle vuelve al SELECT y no
        #    solo al UPDATE.

    raise ConcurrentModification(f"{max_retries} reintentos sin exito")
