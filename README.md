# Backend Challenge – Async Event Processing (Python)

Este proyecto implementa la solución al **Technical Challenge — Backend Developer (Python/.NET)**, donde se debe procesar un flujo asíncrono de eventos en tiempo real garantizando:

- **Orden por llamada** (per-call ordering)
- **Concurrencia máxima configurada entre llamadas**
- **Backpressure** cuando se excede el límite de llamadas activas
- **Finalización correcta y ordenada** cuando termina el stream de eventos

La solución está desarrollada exclusivamente con `asyncio`, sin librerías externas.

---

## Descripción del Problema

El sistema recibe un *async stream* de eventos (`CallEvent`), cada uno asociado a un `call_id`.
Debemos procesarlos con la función ya provista `handle_event(call_id, event)`.

La función requerida:

```python
async def process_event_stream(events: AsyncIterator[CallEvent]) -> None:
    ...
```

Cumple los siguientes requerimientos:

### ✔ R1 – Per-call ordering
Los eventos de cada `call_id` deben procesarse en **orden de llegada**.

### ✔ R2 – Concurrency across calls
Diferentes llamadas pueden procesarse en paralelo, hasta un máximo definido:

```python
MAX_CONCURRENT_CALLS = 10
```

### ✔ R3 – Backpressure
Si ya existen 10 llamadas procesándose, un nuevo `call_id` debe esperar a que una finalice.

### ✔ R4 – Graceful Shutdown
Cuando el stream finaliza, se debe esperar la finalización de **todas las tareas activas** antes de retornar.

---

## 🏗️ Arquitectura de la Solución

La implementación utiliza los siguientes componentes:

### 🔹 1. Una `asyncio.Queue` por cada `call_id`
Asegura orden y procesamiento secuencial.

### 🔹 2. Un worker asíncrono por llamada
Cada worker:
- Procesa eventos secuencialmente
- Mantiene el semáforo adquirido
- Libera el semáforo al finalizar

### 🔹 3. Un `asyncio.Semaphore` para controlar concurrencia
Evita que más de `MAX_CONCURRENT_CALLS` llamadas estén en proceso simultáneo.

### 🔹 4. Un sentinel (`None`) para indicar fin de cada cola
Permite al worker finalizar cuando ya no habrá más eventos.

### 🔹 5. `asyncio.gather()` para esperar workers al finalizar
Garantiza el **graceful shutdown**.

---

## ▶️ Ejecución

Ejecuta el script directamente:

```bash
python main.py
```

Se utiliza `fake_event_stream()` para pruebas manuales.

---

## 🧪 Cómo Probar el Semáforo
Activar logs para verificar que **nunca hay más de 10 llamadas activas**.

Ejemplo de debug dentro del worker:

```python
print(f"[START] {call_id} active={active_calls}")
print(f"[END]   {call_id} active={active_calls}")
```

Si el semáforo funciona, `active` nunca será mayor a `MAX_CONCURRENT_CALLS`.

---

## 📁 Estructura del Proyecto

```
.
├── main.py
├── README.md

```

---

## 🔧 Requisitos

- Python 3.13+
- No se requieren dependencias externas

---

## 📌 Notas

Esta solución está diseñada para ejecutarse dentro de un servicio de larga vida.
No usa variables globales compartidas en el sistema (solo para debugging). Se prioriza
claridad, aislamiento de tasks y robustez.
