import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Any, Dict

@dataclass
class CallEvent:
    call_id: str
    payload: Any

# Simulated event handler; assume this is given.
async def handle_event(call_id: str, event: CallEvent) -> None:
    # In real life this might call STT/LLM/TTS or hit external APIs.
    # Here we simulate some async work.
    await asyncio.sleep(0.1)

MAX_CONCURRENT_CALLS = 10
async def process_event_stream(events: AsyncIterator[CallEvent]) -> None:
    """
    Consume an async stream of CallEvent objects and process them with
    handle_event.
    Requirements:
    - Per-call ordering: events for a given call_id must be processed
    sequentially,in arrival order.
    - Concurrency across calls: events for different call_ids may be
    processed in parallel, up to MAX_CONCURRENT_CALLS active calls
    at a time.
    - Backpressure: if there are already MAX_CONCURRENT_CALLS active,
    new call_ids must wait until at least one active call finishes
    all its events.
    - Graceful shutdown: when the `events` iterator is exhausted,
    wait for all in-flight work to complete before returning.
    """
    # TODO: implement this
    sem = asyncio.Semaphore(MAX_CONCURRENT_CALLS)

    queues: Dict[str, asyncio.Queue] = {}
    tasks: Dict[str, asyncio.Task] = {}
    async def call_worker(call_id, queue):
        await sem.acquire()
        try:
            while True:
                event = await queue.get()
                if event is None:
                    print(f"None event for call {event}: {queue}")
                    break
                await handle_event(call_id, event)
        finally:
            sem.release()

    async for event in events:
        if event.call_id not in queues:
            queue = asyncio.Queue()
            queues[event.call_id] = queue
            tasks[event.call_id] = asyncio.create_task(call_worker(event.call_id, queue))
            print(f"Processing event for call {event.call_id}:::: {queues}")


        await queues[event.call_id].put(event)

    for q in queues.values():
        await q.put(None)

    await asyncio.gather(*tasks.values())


# Optional: simple test harness you can use for manual testing
async def fake_event_stream() -> AsyncIterator[CallEvent]:
    for call_id in ["A", "B", "C", "A", "B", "A", "B", "B", "A", "A", "B", "A", "D","A","B"]:
        yield CallEvent(call_id=call_id, payload={"seq": id(call_id)})
        await asyncio.sleep(0.001)


if __name__ == "__main__":
    asyncio.run(process_event_stream(fake_event_stream()))