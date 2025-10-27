# Building a Kafka-Based Auditing API in Docker

This document describes how to build a centralized auditing API using Kafka, running inside a Docker container and orchestrated via `docker-compose`. The API exposes a single method, `tick`, which records audit events with the following parameters:

- `process_name` (str): Name of the process.
- `process_activity` (str): Activity performed by the process.
- `count` (int, default=1, must be >= 1): Number of times the activity occurred.

## 1. Installation and Configuration

### Prerequisites

- Docker & Docker Compose installed on your system.
- Python 3.9+ (for API service).

### Kafka Setup

Kafka requires both a Kafka broker and a Zookeeper instance. These can be defined in `docker-compose.yml`.

#### Example `docker-compose.yml`

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  auditor_api:
    build: ./auditor_api
    depends_on:
      - kafka
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    ports:
      - "8000:8000"
```

## 2. Auditor API Service Code

The API service can be implemented using FastAPI and the `kafka-python` library.

### Directory Structure

```
auditor_api/
├── Dockerfile
├── requirements.txt
└── main.py
```

### `requirements.txt`

```
fastapi
uvicorn
kafka-python
```

### `Dockerfile`

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `main.py`

```python
from fastapi import FastAPI, Query
from kafka import KafkaProducer
import os
import json

app = FastAPI()
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
AUDIT_TOPIC = "audit_events"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

@app.post("/tick")
def tick(
    process_name: str,
    process_activity: str,
    count: int = Query(1, ge=1)
):
    event = {
        "process_name": process_name,
        "process_activity": process_activity,
        "count": count
    }
    producer.send(AUDIT_TOPIC, event)
    return {"status": "success", "event": event}
```

## 3. Configuration Files

- **docker-compose.yml**: Defines Zookeeper, Kafka, and the API service.
- **Dockerfile**: Builds the API container.
- **requirements.txt**: Python dependencies.

## 4. Workflow Description

1. **Startup**: `docker-compose up` starts Zookeeper, Kafka, and the API service.
2. **API Call**: Clients POST to `/tick` with required parameters.
3. **Event Recording**: The API serializes the event and sends it to the Kafka topic `audit_events`.
4. **Scalability**: Kafka handles high throughput and multiple producers/consumers.

## 5. Notes

- You can scale the API service by increasing replicas in `docker-compose.yml`.
- Consumers can be added to process audit events from Kafka as needed.
- For production, consider securing Kafka and the API endpoints.

---

# Instructions for GPT-4.1 Agent: Kafka-Based Auditing API Project

**Goal:**  
Create a Dockerized FastAPI service that exposes a `/tick` endpoint, records audit events to a Kafka topic, and is orchestrated with `docker-compose`.  
All code, configuration, and setup must be generated from scratch in `/workspace/src/the_auditor` (or a new subfolder if needed).

---

## Steps

1. **Read the markdown in `/workspace/src/the_auditor/code_description.md` for requirements and workflow.**
2. **Create the following files and folders:**
   - `auditor_api/` (subfolder for API service)
     - `main.py` (FastAPI code for `/tick`)
     - `requirements.txt` (Python dependencies)
     - `Dockerfile` (for API container)
   - `docker-compose.yml` (in `/workspace/src/the_auditor/`)
3. **Ensure the API uses Kafka for event publishing as described.**
4. **Configure Kafka and Zookeeper services in `docker-compose.yml` using official images.**
5. **Set up environment variables for Kafka connection.**
6. **Document any additional steps needed for local development, such as installing Docker and Docker Compose.**
7. **Verify that the API service builds and runs, and that POST requests to `/tick` publish events to Kafka.**
8. **Do not require any files or context outside of `/workspace/src/the_auditor/code_description.md`.**
9. **If any ambiguity arises, follow best practices for Python, Docker, and Kafka integration.**

---

**Prompt Example:**  
"Read `/workspace/src/the_auditor/code_description.md` and generate all code, configuration, and setup needed to build and run the described Kafka-based auditing API project in Docker, with no external dependencies or assumptions."

---

With these instructions, a GPT-4.1 Agent will have all the context needed to fully recreate the project after a reboot.