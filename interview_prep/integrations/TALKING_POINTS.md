# Chuleta para la entrevista

Ajustada a la JD completa. Te van a preguntar por **decisiones y trade-offs**,
no por implementar un backoff en la pizarra.

**Lee primero las secciones 0, 1 y 6.** Si solo te da tiempo a una, que sea la
**6** (la pregunta sobre IA): está escrita literalmente en la JD, así que es la
única pregunta *garantizada* — y es donde tienes ventaja real.

---

## 0. La idea que ordena toda la conversación

> **En una integración, la pregunta no es "¿y si falla?", es "¿qué hago cuando
> falle?". Los fallos no son excepciones: son parte del contrato.**

Suéltala pronto y el resto de tus respuestas suenan coherentes.

La JD dice: *"alguien que haya vivido la realidad compleja de sistemas
interdependientes"*. Traducción: quieren oír **cicatrices**, no definiciones.
Cada respuesta debe terminar en un trade-off, no en un patrón.

---

## 1. Los 4 temas core

### 1.1 Reintentos

- Reintentar **solo lo transitorio**: 500, 503, 429, timeout, conexión caída.
  Un 400 o un 401 se reintenta cero veces — el resultado será idéntico y solo
  añades carga a un sistema que ya sufre.

  **La regla que lo ordena todo:** `4xx` = *la culpa es tuya* (la petición está
  mal). `5xx` = *la culpa es suya* (la petición está bien, el servidor falló).

  | Código | Significa | ¿Reintentar? |
  |---|---|---|
  | **400** Bad Request | Mandaste algo inválido (JSON roto, campo que falta) | ❌ Nunca |
  | **401** Unauthorized | No estás autenticado, o el token caducó | ❌ Arregla el token primero |
  | **403** Forbidden | Autenticado, pero sin permiso | ❌ Nunca |
  | **404** Not Found | El recurso no existe | ❌ Nunca |
  | **409** Conflict | Choque de estado. Es lo que devuelve Stripe ante dos reintentos simultáneos con la misma key — tu `ChargeInProgress` | ⚠️ Más tarde, con cuidado |
  | **422** Unprocessable | Sintaxis bien, viola una regla de negocio | ❌ Nunca |
  | **429** Too Many Requests | Rate limit: vas demasiado rápido | ✅ **Sí**, respeta `Retry-After` |
  | **500** Internal Server Error | Se les rompió algo por dentro | ✅ Sí |
  | **502** Bad Gateway | Un proxy no pudo hablar con el de detrás | ✅ Sí |
  | **503** Service Unavailable | Caído o saturado, temporalmente | ✅ Sí |
  | **504** Gateway Timeout | Un proxy se cansó de esperar | ✅ Sí, **pero ojo** |

  **Los dos matices que demuestran que lo has vivido:**

  1. **El 429 rompe la regla**: es `4xx` pero SÍ se reintenta. Es el único que
     te dice "vuelve luego", y trae `Retry-After`: úsala en vez de tu backoff.
  2. **El 504 es el peligroso**: timeout disfrazado de respuesta. Significa "no
     sé qué pasó ahí dentro" — la operación pudo completarse. Reintentarlo sin
     idempotency key es exactamente cómo se cobra dos veces a un cliente.

- **Backoff exponencial + jitter**. El *thundering herd* es lo que pasa **cuando
  NO hay jitter**: si el servicio parpadea, los 100 clientes que fallaron
  esperan exactamente 200 ms y vuelven **todos a la vez**, convirtiendo un
  parpadeo en una caída. El jitter reparte esas vueltas.

  **Reintentar nunca es una solución completa.** Añade carga a un sistema que ya
  está mal. El backoff y el jitter *reducen* el daño; no lo eliminan. Por eso:
  - **Circuit breaker**: si el 50% falla, deja de intentarlo un rato.
    Reintentar contra un servicio caído no lo levanta — le impide levantarse.
  - **Load shedding**: rechazar rápido lo que no puedes atender, en vez de
    aceptarlo todo y morir lento.

  > *"El backoff con jitter evita que los clientes se sincronicen, pero seguir
  > reintentando contra un servicio caído solo le impide recuperarse. Por eso el
  > reintento va siempre acompañado de un circuit breaker."*

- **Deadline / presupuesto de tiempo**, no solo número de intentos.

  **¿De dónde sale?** De dos sitios, y ninguno es "la industria":
  1. **Del producto, hacia atrás.** Si la pantalla debe responder en 1s y llamas
     a dos servicios, cada uno tiene ~400ms y guardas margen. El presupuesto se
     **hereda y se reparte**, nunca se inventa por servicio.
  2. **De medir la dependencia, no de adivinar:**
     > *"El timeout se pone mirando la distribución de latencia real del
     > servicio del que dependes — su p99 o p99.9 — no eligiendo un número
     > redondo. Si su p99 es 300ms y pones 200ms, estás cortando el 1% de
     > peticiones que iban a funcionar perfectamente."*

  | Caso | Presupuesto razonable |
  |---|---|
  | Timeout de **conexión** (TCP) | 1–3 s |
  | Llamada interna entre servicios | 100 ms – 1 s |
  | Endpoint de cara al usuario | 1–3 s total, reintentos incluidos |
  | Pasarela de pago | 10–30 s (son lentas y el usuario lo tolera) |
  | Llamada a un LLM | 10–60 s (ver sección 3) |
  | Job en background / cola | minutos |

  **El remate:** el sitio donde reintentas cambia el presupuesto por completo.
  Con un humano esperando tienes 1–2s y un reintento. En una cola, tienes horas.
  Por eso **"¿esto puede ser asíncrono?"** suele ser la mejor respuesta a "¿cómo
  manejas los fallos?".

> *"Reintentar sin idempotencia no es resiliencia, es duplicar datos con más
> pasos."*

### 1.2 Timeouts

- **Siempre** hay que ponerlos. `requests` sin `timeout=` espera **para
  siempre**: es el bug de producción más común en integraciones Python.
- Distingue **timeout de conexión** y **de lectura**: "no llegué" vs "llegué y
  no me contestan". Son problemas distintos y se configuran por separado.
- El timeout es **ambigüedad, no fracaso**. NO significa que la operación no
  ocurrió — significa que **no sabes** si ocurrió. De ahí sale la idempotencia.
- **Propagación del deadline**: si tu endpoint tiene 3s, no puedes gastar 5s
  reintentando río abajo.

### 1.3 Consistencia de datos

- **At-least-once + idempotencia = effectively-once.** Grábatela.
  "Exactly-once *delivery*" no existe; lo que existe es *exactly-once
  processing* construido sobre entregas repetidas.
- **Idempotency key generada por el cliente**, estable entre reintentos, con
  restricción `UNIQUE` en la base. **La restricción la impone la base, no tu
  `if`** — entre tu `SELECT` y tu `INSERT` cabe otro proceso.
- Orden: **reservar → ejecutar → confirmar**. Se prefiere el fallo recuperable
  (registro de algo que no pasó) al irreversible (cobraste sin registrarlo).
- **No hay transacción entre tu base y una API de terceros.** Lo que hay es
  **outbox pattern**, **sagas** y **compensaciones**. Nombra el outbox: es la
  respuesta a *"¿cómo publicas un evento y guardas en base a la vez?"*.
- **Reconciliación**: ningún diseño cierra el hueco del todo (si el proceso
  muere entre cobrar y confirmar, quedas inconsistente). Por eso en producción
  hay un job que cuadra tus datos con los del tercero. Decir esto te sitúa por
  encima de la media.
- Dinero en **enteros de céntimos, nunca float**. `0.1 + 0.2 != 0.3`.

### 1.4 Condiciones de carrera

- **El resultado depende del orden de ejecución**, y ese orden no lo controlas.
- Los dos niveles (mucha gente solo conoce uno):
  - **En memoria**: `threading.Lock`. El GIL **no** te protege: evita que la
    memoria se corrompa, no que tu lógica se rompa.
  - **En base de datos**: el `Lock` no sirve — el otro proceso está en otra
    máquina.
- **Lost update**: dos procesos leen, los dos comprueban bien, los dos escriben,
  uno pisa al otro. Los dos tenían razón y el resultado está mal. El síntoma es
  contraintuitivo: **el saldo no queda negativo, queda demasiado alto** respecto
  al dinero entregado. No se ve mirando la fila; se ve reconciliando.
- Las tres soluciones, en orden de preferencia:
  1. **UPDATE atómico condicional** — `SET saldo = saldo - ? WHERE saldo >= ?`.
     Lo que lo salva es que la resta es **relativa**; con un valor calculado en
     Python sería el bug otra vez.
  2. **Bloqueo optimista** (columna `version`) — cuando la lógica no cabe en
     SQL. Barato con poca contención, terrible con mucha.
  3. **Bloqueo pesimista** (`SELECT ... FOR UPDATE`) — correcto pero serializa y
     abre la puerta a deadlocks.

> *"Las condiciones de carrera no se arreglan con tests, se arreglan con diseño.
> El test solo te dice que hoy tuviste suerte."*

---

## 2. Cómo conectas sistemas: REST, webhooks y colas

La JD los nombra los tres. Cada uno falla distinto.

### Webhooks (recibir) — el que más se olvida

Un webhook es **una API que tú expones y que no controlas quién llama**. Todo lo
de arriba se da la vuelta: ahora **tú** eres el sistema poco fiable del otro.

Las cinco reglas, en orden:

1. **Responde 2xx rápido y procesa después.** Encola y devuelve. Si procesas
   dentro del handler, su timeout dispara su reintento y te llega duplicado.
2. **Verifica la firma** (HMAC). Un webhook es un endpoint público: cualquiera
   puede POSTear. Compara en tiempo constante.
3. **Son at-least-once: te van a llegar duplicados.** Mismo problema, misma
   solución: `event_id` con `UNIQUE`. Es tu ejercicio 2 otra vez.
4. **Llegan desordenados.** El evento `updated` puede llegar antes que
   `created`. Usa el timestamp o versión del *evento*, no el orden de llegada.
5. **Un 2xx tuyo es una promesa.** Si dices 200 y luego lo pierdes, no te lo
   reenvían nunca. Persiste antes de confirmar.

> *"Un webhook no es un evento, es un aviso. Lo que hago es confirmarlo rápido,
> y luego releer el estado real desde su API — porque el payload puede estar
> desordenado o desactualizado."*

### Colas de mensajes

- **At-least-once por defecto** → idempotencia otra vez. Es el mismo patrón en
  todas partes; esa es la idea que quieres transmitir.
- **DLQ (dead letter queue)**: tras N fallos, el mensaje sale de la cola
  principal. Sin DLQ, un mensaje envenenado bloquea el consumidor para siempre.
- **Visibility timeout**: si tarda más que él, otro consumidor coge el mismo
  mensaje y lo procesas dos veces.
- **Orden**: casi ninguna cola lo garantiza salvo que renuncies a paralelismo.
  Si necesitas orden, particiona por clave (ej: por `customer_id`).
- **El valor real de la cola**: desacopla el presupuesto de tiempo. Convierte
  "el usuario espera" en "el sistema ya lo hará".

### REST

- Los verbos ya te dicen qué es idempotente: `GET`/`PUT`/`DELETE` lo son por
  definición, **`POST` no** — por eso las idempotency keys viven en los POST.
- **Paginación y rate limits**: si sincronizas datos de un tercero, esto es el
  90% del trabajo real.
- **Versionado y contratos**: un tercero cambia su API sin avisarte. Valida el
  payload en tu frontera (Pydantic) y falla claro, no tres capas más abajo.

---

## 3. Integraciones con IA/ML (está en las responsabilidades)

Es lo mismo de siempre **más cuatro problemas nuevos**. Aquí puedes brillar
porque poca gente lo ha pensado en términos de fiabilidad:

1. **Son lentas y de latencia impredecible.** Un LLM puede tardar 2s o 60s por
   la misma llamada. Tu p99 no te sirve tanto: usa streaming si hay un humano
   delante, y cola si no lo hay.
2. **Fallan de formas nuevas.** No solo 500: te devuelven JSON inválido, o
   válido pero con campos inventados. **Valida siempre la salida** (Pydantic,
   JSON schema). Un reintento aquí no es por red, es por formato.
3. **No son deterministas.** La misma entrada da salidas distintas → tu
   idempotency key no puede depender de la respuesta, y cachear es más sutil.
4. **Cuestan dinero por llamada.** Un bucle de reintentos mal puesto no te tira
   el sistema: te vacía el presupuesto. Aquí el circuit breaker protege la
   cartera, no la latencia.

> *"Un servicio de IA es una dependencia de terceros lenta, cara y no
> determinista. Se trata igual que cualquier otra: timeout, reintento con
> backoff, circuit breaker e idempotencia. Lo único que añado es validar la
> salida contra un esquema, porque puede fallar devolviendo un 200."*

---

## 4. Full stack: frontend, SQL y "límites claros entre sistemas"

La JD pide comodidad en todo el stack y **"límites claros entre sistemas"**.

### El as en la manga: las carreras también están en el frontend

Esto conecta tu tema con React/Vue y demuestra que piensas igual en todo el
stack:

```js
// El usuario teclea rápido. La respuesta de "ab" puede llegar DESPUÉS
// que la de "abc", y pintas resultados viejos sobre los nuevos.
const results = await search(query);
setResults(results);              // <-- lost update, en la UI
```

Es **exactamente** tu `withdraw_unsafe`: lees, tardas, escribes encima de algo
más nuevo. Se arregla igual — comprobando que lo que escribes sigue siendo
válido: `AbortController`, o descartar la respuesta si el query ya cambió (el
equivalente a la columna `version`).

> *"La condición de carrera del ejercicio de backend es la misma que la de un
> autocomplete en React. Cambia el estado compartido, no el problema."*

### SQL

- **Transacción = límite de consistencia.** Lo que va junto, va en la misma
  transacción; lo que no cabe (una API de terceros), va con outbox o saga.
- **Índices**: si mencionas la idempotency key, di que el `UNIQUE` **es** el
  índice que la hace rápida y correcta a la vez.
- **N+1**: el bug de rendimiento más común en full stack.
- **Migraciones**: cambiar un esquema con la app corriendo se hace en dos pasos
  (añadir columna nullable → backfill → hacerla obligatoria). Si lo mencionas,
  suena a producción de verdad.

### Límites claros

> *"Mi regla es que los datos de un tercero no entran crudos en mi dominio.
> Tengo una capa de frontera que valida, normaliza y traduce sus errores a los
> míos. Así, cuando cambian su API, se rompe un solo archivo — no toda la
> aplicación."*

---

## 5. Automatización, pipelines y CI/CD

- **Pipelines y tareas programadas**: un cron que corre cada 5 min y tarda 6 se
  solapa consigo mismo → carrera contra tus propios datos. Solución: **lock
  distribuido** o marcar las filas en proceso. Es tu ejercicio 3 con sombrero.
- **Disparadores por evento vs polling**: los eventos son más rápidos pero se
  pierden; el polling es aburrido y fiable. Lo habitual es **eventos + un
  reconciliador periódico** que recoge lo que se cayó.
- **Backfills**: cuando una integración lleva 3 días rota, alguien tiene que
  reprocesar. Si tu pipeline es idempotente, es trivial. Si no, es un infierno.
  **Ese es el argumento de negocio de la idempotencia.**
- **CI/CD**: tests en cada PR, migraciones versionadas, despliegue reversible.
  El punto que importa: **los tests de integración con terceros no llaman al
  tercero** — se mockean, como en tus ejercicios. El contrato se verifica aparte.
- **Git**: ramas cortas, PRs pequeños, commits que explican el *por qué*.

---

## 6. ⭐ La pregunta sobre herramientas de IA (garantizada)

> *"¿Cómo estás utilizando actualmente herramientas de codificación con IA y qué
> hiciste cuando detectaste una debilidad en ellas?"*

Está **literalmente escrita en la JD**. Es la única pregunta que sabes seguro.
Y no buscan "uso Copilot y va muy bien" — buscan **criterio y escepticismo**.

**Y tú tienes una historia real, de hoy.** Cuéntala así:

### La historia (estructura: situación → tensión → acción → aprendizaje)

> *"Esta misma semana estaba repasando condiciones de carrera en Python con un
> asistente de IA. Me generó el ejemplo clásico: cuatro hilos incrementando un
> contador global 100.000 veces, con el comentario 'el resultado casi nunca será
> 400.000'.*
>
> *Lo ejecuté y me dio 400.000. Exacto. Lo corrí otra vez: 400.000. Cinco veces
> más: siempre exacto.*
>
> *Podría haberlo dado por bueno — el código 'funcionaba'. Pero la explicación y
> el comportamiento no coincidían, y eso significa que uno de los dos estaba mal.
> Así que en vez de discutir, monté el experimento: desensamblé el bucle con
> `dis`, y medí.*
>
> *Resultó que desde CPython 3.10 el intérprete solo evalúa el cambio de hilo en
> las llamadas a función y en los saltos hacia atrás — no entre bytecodes
> cualesquiera. El `contador += 1` compila a cuatro instrucciones seguidas sin
> ningún punto de interrupción en medio, así que la ventana de la carrera no
> existe. El ejemplo era correcto para Python 3.8 y llevaba años circulando en
> internet; la IA lo reprodujo tal cual, sin saber que el intérprete había
> cambiado debajo.*
>
> *Lo arreglé metiendo una llamada a función entre la lectura y la escritura,
> que es lo que abre la ventana de verdad. Con eso se pierde el 60% de los
> incrementos, de forma reproducible.*
>
> *La lección que me llevé: la IA es rapidísima produciendo código plausible, y
> 'plausible' es justo el tipo de error más caro, porque pasa la revisión. Lo
> que no hace es dudar de sí misma. Ese sigue siendo mi trabajo: diseñar el
> experimento que la desmienta."*

### Por qué esta historia funciona

Marca, sin que tengas que decirlo:

- **Verificas en vez de confiar** — la debilidad la detectaste ejecutando.
- **Proceso sistemático y estructurado** (lo pide la JD literalmente):
  observación → hipótesis → medición → causa raíz → arreglo verificado.
- **Profundidad técnica real**: el eval breaker de CPython no es trivia de
  tutorial.
- **Sabes que las herramientas tienen fecha de caducidad**: el entrenamiento
  refleja el internet de hace años, y el internet está lleno de código correcto
  para versiones viejas.

### Si repreguntan "¿otro ejemplo?"

> *"Ese mismo día, montando unos ejercicios, el código generado compartía una
> conexión de SQLite entre hilos con `check_same_thread=False`. Parecía
> razonable — el parámetro existe justo para eso. Pero ese flag solo silencia la
> comprobación: no hace la conexión thread-safe. Los tests fallaban de forma
> intermitente y rarísima. Lo pillé porque no me fío de un test de concurrencia
> que pasa una vez; los corro diez veces seguidas. La solución fue lo que se
> hace en producción de todas formas: una conexión por hilo."*

### Tu política de uso, en una frase

> *"La uso como un junior muy rápido y muy leído que nunca dice 'no estoy
> seguro'. Le delego el andamiaje, los tests repetitivos y explorar una API que
> no conozco. No le delego las decisiones de diseño ni nada sobre concurrencia o
> consistencia — precisamente porque ahí el código incorrecto también compila y
> también pasa los tests el 99% de las veces. Y todo lo que toca producción lo
> ejecuto antes de creérmelo."*

### Automatización del navegador con IA (lo nombra la JD)

Si sale, conecta con tu tema en vez de fingir experiencia:

> *"No lo he usado en producción, pero el problema que me imagino es el mismo:
> es una dependencia lenta, no determinista y cara. Un agente que pincha en una
> web falla como cualquier integración — timeouts, pasos que se ejecutan dos
> veces, estado que cambió debajo. Yo lo trataría igual: cada paso idempotente,
> timeouts explícitos, y un estado persistido para poder reanudar en vez de
> repetir desde cero."*

---

## 7. Preguntas que te van a hacer, y el gancho

| Pregunta | Por dónde entrar |
|---|---|
| "¿Cómo manejas un fallo de un tercero?" | Clasificar transitorio vs permanente **primero**. Todo depende de eso. |
| "¿Qué pasa si la API cobra pero no responde?" | Idempotency key. Es el ejercicio 2. |
| "¿Cómo evitas duplicados?" | `UNIQUE` en la base, no un `if` en Python. |
| "¿Has tenido una condición de carrera?" | Lost update entre dos workers. **Cuenta el síntoma antes que la causa** — así suena a vivido. |
| "¿Cómo procesas webhooks?" | 2xx rápido + encolar + firma + `event_id` único. |
| "¿Cómo testeas esto?" | Inyectar reloj y sleep; mockear el tercero. Y correr los tests de concurrencia 10 veces. |
| "¿Cómo sabes que algo va mal?" | Métricas de error/latencia, alertas y **reconciliación**. |
| "¿Cómo usas la IA?" | Sección 6. Es la que tienes regalada. |
| "¿Cómo diseñas un pipeline?" | Idempotente de punta a punta, para que un backfill sea trivial. |

---

## 8. Junior vs senior en esta conversación

Un junior explica **el mecanismo** ("uso backoff exponencial").
Un senior explica **el trade-off** ("uso backoff exponencial, pero con deadline
total, porque prefiero fallar rápido y que la cola absorba el retry a tener 500
conexiones esperando").

**Cada respuesta termina en una contrapartida.** Las tienes listas:

- Reintentos → añaden carga a un sistema que ya está mal → circuit breaker.
- Bloqueo optimista → gratis con poca contención, terrible con mucha.
- Idempotencia → te obliga a almacenar y limpiar keys (TTL).
- Timeouts agresivos → cortas peticiones que iban a funcionar.
- Colas → resuelven el presupuesto de tiempo, pero traen orden y DLQ.
- Eventos → más rápidos que el polling, pero se pierden → reconciliador.

---

## 9. Si te preguntan por experiencia que no tienes

No inventes: se cae a la segunda repregunta. Reencuadra:

> *"En producción a esa escala no lo he hecho, pero he trabajado el problema. Lo
> que más me sorprendió es que un timeout no te dice que la operación falló — te
> dice que no sabes si ocurrió. Y eso cambia el diseño entero, porque te obliga
> a la idempotencia desde el principio en vez de añadirla después."*

Un "no lo he hecho, pero entiendo por qué es difícil" vale más que un ejemplo
inflado. **Están comprando criterio.**

---

## 10. Bonus: Python vs JavaScript en concurrencia

La diferencia cabe en una palabra: **preemptivo vs cooperativo**.

| | Python (`threading`) | JS / Python (`asyncio`) |
|---|---|---|
| Modelo | Hilos del SO | Un hilo + event loop |
| Quién decide el cambio | **El intérprete**, cuando quiere | **Tú**, con `await` |
| ¿Dónde se interrumpe? | En sitios que no escribiste | Solo en los `await` |
| ¿Ves el peligro leyendo? | **No** | **Sí** |

**Async NO elimina las carreras. Solo hace visibles los puntos donde ocurren:**

```js
const balance = await getBalance(id);        // aquí cede el control
if (balance >= amount) {                     // otra tarea se cuela
  await setBalance(id, balance - amount);    // escribes un valor viejo
}
```

Idéntico a tu `withdraw_unsafe`.

> *"Async no te quita las carreras, te quita la sorpresa. En Node sé dónde puedo
> perder el control: en los `await`. Con hilos en Python lo puedo perder en
> cualquier sitio. Pero la solución es la misma, porque el estado compartido está
> en la base, no en el proceso."*

- **CPU intensivo**: los hilos de Python no ayudan (GIL); en JS bloqueas el
  event loop entero. Ambos necesitan salir del proceso.
- **Python 3.14 free-threaded**: sin GIL, los hilos van de verdad en paralelo y
  sale a la luz todo lo que el GIL escondía por accidente.

---

## 11. Inglés

La JD pide inglés conversacional, así que **puede que cambien de idioma sin
avisar**. Ten listos los términos — no traduzcas: *retry, backoff, jitter,
timeout, deadline, idempotency key, race condition, lost update, optimistic
locking, at-least-once, dead letter queue, circuit breaker, webhook signature,
reconciliation, thundering herd.*

Practica esta en voz alta, que es tu frase estrella:

> *"A timeout doesn't tell you the operation failed — it tells you that you
> don't know whether it happened. That's why idempotency has to be in the design
> from the start, not bolted on later."*
