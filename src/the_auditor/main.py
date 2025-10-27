from io import TextIOWrapper
from typing import Dict
from fastapi import FastAPI, Query
from kafka import KafkaProducer
import os
import json
import time
from pathlib import Path

from the_auditor.file_handle_cache import FileHandleCache

app = FastAPI()
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
AUDIT_TOPIC = "audit_events"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

_file_handle_cache: FileHandleCache = FileHandleCache(Path("/the_auditor"))


@app.post("/tick")
async def tick(
    service_name: str,
    process_name: str,
    process_activity: str,
    count: int = Query(1, ge=1),
):
    time_tick = int(time.time())
    await _file_handle_cache.log_tick(
        service_name, process_name, process_activity, count, time_tick
    )

    event = {
        "service_name": service_name,
        "process_name": process_name,
        "process_activity": process_activity,
        "count": count,
        "time_tick": time_tick,
    }
    producer.send(AUDIT_TOPIC, event)
    return {"status": "success", "event": event}
