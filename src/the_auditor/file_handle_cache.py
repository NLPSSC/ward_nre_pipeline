import aiofiles
import asyncio
from pathlib import Path
from typing import Dict


class FileHandleCache:
    def __init__(self, audit_root_path: Path):
        self._audit_root_path: Path = audit_root_path
        # Now cache is service_name -> process_name -> process_activity -> file_path
        self._cache: Dict[str, Dict[str, Dict[str, Path]]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def log_tick(
        self,
        service_name: str,
        process_name: str,
        process_activity: str,
        count: int,
        time_tick: int,
    ):
        if service_name not in self._cache:
            self._cache[service_name] = {}
        if process_name not in self._cache[service_name]:
            self._cache[service_name][process_name] = {}
        if process_activity not in self._cache[service_name][process_name]:
            log_dir = self._audit_root_path / service_name / process_name
            log_dir.mkdir(parents=True, exist_ok=True)
            file_path = log_dir / f"{process_activity}.csv"
            self._cache[service_name][process_name][process_activity] = file_path
            # Create lock for this file if not exists
            lock_key = str(file_path)
            if lock_key not in self._locks:
                self._locks[lock_key] = asyncio.Lock()
            # Write header if file is new or empty
            if not file_path.exists() or file_path.stat().st_size == 0:
                async with aiofiles.open(file_path, "a") as f:
                    await f.write("count,time_tick\n")
        file_path = self._cache[service_name][process_name][process_activity]
        lock_key = str(file_path)
        lock = self._locks[lock_key]
        async with lock:
            try:
                async with aiofiles.open(file_path, "a") as f:
                    await f.write(f"{count},{time_tick}\n")
            except Exception as e:
                raise RuntimeError(f"Failed to write tick: {e}")

    async def close_all(self):
        # No open file handles to close with aiofiles; just clear cache and locks
        self._cache.clear()
        self._locks.clear()
