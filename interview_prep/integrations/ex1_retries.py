"""Ejercicio 1 - Reintentos, backoff, jitter y deadlines.  (~45 min)

El escenario: llamas a una API de un tercero que a veces falla. Tienes que
decidir cuando reintentar, cuanto esperar entre intentos, y cuando rendirte.

Corre los tests y ponlos en verde uno a uno:

    cd interview_prep
    ../task_manager/venv/bin/pytest test_ex1_retries.py -v

Las 5 decisiones que estas practicando (y que te van a preguntar):

  1. NO todo error se reintenta. Un 500 o un timeout, si. Un 400 o un 401,
     no: reintentarlo solo multiplica la carga y el resultado sera el mismo.
  2. Backoff exponencial: 0.1s, 0.2s, 0.4s... Si reintentas de inmediato
     tumbas al servicio que ya esta sufriendo.
  3. Jitter (aleatoriedad): si 100 clientes fallan a la vez y todos esperan
     exactamente 0.2s, los 100 vuelven a golpear a la vez. A eso se le llama
     "thundering herd". El jitter los reparte.
  4. Deadline: el presupuesto total de tiempo. De nada sirve reintentar 5
     veces si el usuario del otro lado ya se fue hace rato.
  5. sleep y now se inyectan como parametros. Asi los tests corren en
     milisegundos en vez de esperar de verdad. Esto es media respuesta a
     "como testeas logica de reintentos?".
"""

import random
import time


class TransientError(Exception):
    """Fallo pasajero: 500, 503, timeout, conexion caida. SE reintenta."""


class PermanentError(Exception):
    """Fallo definitivo: 400, 401, 404, validacion. NO se reintenta."""


class RetriesExhausted(Exception):
    """Se acabaron los intentos y seguimos fallando."""


class DeadlineExceeded(Exception):
    """Se acabo el presupuesto de tiempo total."""


def retry(
    fn,
    *,
    attempts=3,
    base_delay=0.1,
    max_delay=2.0,
    deadline=None,
    sleep=time.sleep,
    now=time.monotonic,
    jitter=random.random,
):
    """Llama a fn() reintentando los fallos pasajeros.

    Args:
        fn: funcion sin argumentos. Puede devolver un valor o lanzar.
        attempts: numero maximo de intentos (incluye el primero).
        base_delay: espera tras el primer fallo, en segundos.
        max_delay: tope de la espera; el backoff no crece mas alla de aqui.
        deadline: instante (en la escala de now()) tras el cual nos rendimos.
        sleep / now / jitter: inyectados para poder testear sin esperar.

    Returns:
        Lo que devuelva fn().

    Raises:
        PermanentError: tal cual, sin reintentar.
        RetriesExhausted: si se agotan los intentos.
        DeadlineExceeded: si la siguiente espera se pasaria del deadline.
    """
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            return fn()

        except PermanentError:
            # Decision numero uno: un 400 no se arregla repitiendolo. Salimos
            # sin dormir y sin gastar intentos.
            raise

        except TransientError as exc:
            last_error = exc

            # Si este era el ultimo intento, no dormimos para nada.
            if attempt == attempts:
                break

            # Backoff exponencial: 0.1, 0.2, 0.4, 0.8...  topado a max_delay
            # para que el quinto reintento no espere media hora.
            delay = min(base_delay * 2 ** (attempt - 1), max_delay)

            # "Full jitter": multiplicamos por un aleatorio en [0, 1). Reparte
            # a los clientes en el tiempo en vez de que vuelvan todos juntos.
            delay *= jitter()

            # El deadline se comprueba ANTES de dormir: si la espera nos saca
            # del presupuesto, rendirse ya es mejor que dormir en balde.
            if deadline is not None and now() + delay > deadline:
                raise DeadlineExceeded(
                    f"deadline agotado tras {attempt} intentos"
                ) from exc

            sleep(delay)

    # 'from last_error' encadena la causa: en el traceback se ve el fallo real
    # del tercero, no solo "me rendi". Esto te lo agradeceras a las 3 am.
    raise RetriesExhausted(f"fallo tras {attempts} intentos") from last_error
