# Preparación: integraciones y fallos en producción

Tres ejercicios para practicar reintentos, timeouts, consistencia de datos y
condiciones de carrera. Cada uno tiene tests que fallan hasta que lo implementas.

## Plan sugerido (entrevista a las 17:00)

| Hora | Qué |
|---|---|
| ~15 min | **`TALKING_POINTS.md` sección 6** — la pregunta sobre IA. Está literalmente en la JD: es la única garantizada. Practícala **en voz alta**. |
| ~20 min | **Ejercicio 2**: idempotencia — el concepto que más sale |
| ~15 min | **Ejercicio 1** y **3**: léelos, ya están resueltos |
| 15:45 – 16:45 | **`TALKING_POINTS.md` entero**, en voz alta |
| 16:45 – 17:00 | Respirar. No abras más código. |

**Si solo te da tiempo a una cosa, que sea `TALKING_POINTS.md`.** La JD pide
experiencia y criterio, no que recites un backoff. El código es el andamio para
tener algo concreto que contar.

## Cómo correrlos

Los tres ejercicios están **ya resueltos y comentados**. Los 18 tests pasan.

```bash
cd interview_prep
source ../task_manager/venv/bin/activate

pytest -v                          # los 18, en verde
pytest test_ex2_idempotency.py -v  # uno solo
```

La forma de estudiarlos: corre los tests, **lee los tests primero** (dicen qué
comportamiento importa y por qué), y luego el código. Los comentarios explican
las decisiones, no la sintaxis.

Si quieres practicar de verdad y te queda tiempo, borra el cuerpo de una función
y reescríbelo hasta que los tests vuelvan a verde.

## Archivos

- `ex1_retries.py` — reintentos con backoff exponencial, jitter y deadline
- `ex2_idempotency.py` — idempotency keys, at-least-once → effectively-once
- `ex3_lost_update.py` — carreras contra la base, UPDATE atómico vs optimista
- `TALKING_POINTS.md` — **lo que más te va a servir hoy**

## Nota

Los tres ejercicios usan solo la librería estándar (`sqlite3`, `threading`) más
pytest. No hay red ni servicios externos: las APIs de terceros están simuladas
con funciones que fallan a voluntad, que es exactamente como se testean las
integraciones de verdad.
