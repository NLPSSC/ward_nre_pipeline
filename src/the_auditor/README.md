# Kafka-Based Auditing API

This project provides a Dockerized FastAPI service for centralized auditing, publishing events to Kafka.

## Prerequisites
- Docker & Docker Compose

## Setup & Usage

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```
   This will start Zookeeper, Kafka, and the API service.

2. **API Usage:**
   - Endpoint: `POST /tick`
   - Example request:
     ```bash
     curl -X POST "http://localhost:8000/tick" \
          -H "Content-Type: application/json" \
          -d '{"process_name": "my_process", "process_activity": "run", "count": 1}'
     ```
   - Parameters:
     - `process_name` (str): Name of the process
     - `process_activity` (str): Activity performed
     - `count` (int, default=1, >=1): Number of times

3. **Kafka Events:**
   - Events are published to the `audit_events` topic in Kafka.
   - You can add consumers to process these events as needed.

## File Structure
- `auditor_api/` — FastAPI service
  - `main.py` — API code
  - `requirements.txt` — Python dependencies
  - `Dockerfile` — Container build
- `docker-compose.yml` — Orchestrates Zookeeper, Kafka, and API

## Notes
- No external dependencies required beyond Docker and Docker Compose.
- For production, secure Kafka and API endpoints as needed.
