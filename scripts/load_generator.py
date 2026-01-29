#!/usr/bin/env python3
"""
Load generator for shadow mode testing.

Generates requests with varied inputs to see different predictions.
"""

import asyncio
import random
import time
from dataclasses import dataclass

import aiohttp


@dataclass
class LoadConfig:
    url: str = "http://localhost:8003/predict"
    total_requests: int = 10000
    duration_seconds: int = 300  # 5 minutes
    concurrent_workers: int = 10


def generate_random_input() -> dict:
    """Generate random reactor input within valid ranges."""
    # Mix of normal and potentially anomalous inputs
    if random.random() < 0.8:
        # Normal operating conditions (80%)
        return {
            "temperature": random.uniform(60, 100),
            "pressure": random.uniform(3, 7),
            "flow_rate": random.uniform(15, 35),
            "reactant_concentration": random.uniform(0.8, 1.5),
            "ph_level": random.uniform(6, 8),
            "stirrer_speed": random.uniform(200, 400),
        }
    else:
        # Edge cases / potential anomalies (20%)
        return {
            "temperature": random.uniform(100, 150),
            "pressure": random.uniform(7, 12),
            "flow_rate": random.uniform(5, 50),
            "reactant_concentration": random.uniform(1.5, 2.5),
            "ph_level": random.uniform(4, 10),
            "stirrer_speed": random.uniform(100, 600),
        }


async def send_request(session: aiohttp.ClientSession, url: str) -> tuple[bool, float]:
    """Send a single prediction request."""
    start = time.perf_counter()
    try:
        async with session.post(url, json=generate_random_input()) as response:
            await response.json()
            latency = time.perf_counter() - start
            return response.status == 200, latency
    except Exception:
        return False, time.perf_counter() - start


async def worker(
    session: aiohttp.ClientSession,
    url: str,
    request_queue: asyncio.Queue,
    results: list,
):
    """Worker that processes requests from the queue."""
    while True:
        try:
            _ = request_queue.get_nowait()
        except asyncio.QueueEmpty:
            break

        success, latency = await send_request(session, url)
        results.append((success, latency))


async def run_load_test(config: LoadConfig):
    """Run the load test."""
    print(f"Starting load test: {config.total_requests} requests over {config.duration_seconds}s")
    print(f"Target rate: {config.total_requests / config.duration_seconds:.1f} req/s")
    print(f"URL: {config.url}")
    print("-" * 50)

    # Calculate delay between request batches
    requests_per_second = config.total_requests / config.duration_seconds
    batch_size = config.concurrent_workers
    batch_delay = batch_size / requests_per_second

    results: list[tuple[bool, float]] = []
    request_queue: asyncio.Queue = asyncio.Queue()

    # Fill the queue
    for _ in range(config.total_requests):
        await request_queue.put(1)

    start_time = time.perf_counter()
    completed = 0

    async with aiohttp.ClientSession() as session:
        while not request_queue.empty():
            batch_start = time.perf_counter()

            # Launch batch of workers
            tasks = [
                worker(session, config.url, request_queue, results)
                for _ in range(min(batch_size, request_queue.qsize()))
            ]
            await asyncio.gather(*tasks)

            completed = len(results)
            elapsed = time.perf_counter() - start_time
            rate = completed / elapsed if elapsed > 0 else 0

            # Progress update every 500 requests
            if completed % 500 == 0:
                success_count = sum(1 for s, _ in results if s)
                print(
                    f"Progress: {completed}/{config.total_requests} "
                    f"({completed * 100 / config.total_requests:.1f}%) | "
                    f"Rate: {rate:.1f} req/s | "
                    f"Success: {success_count}/{completed}"
                )

            # Throttle to maintain target rate
            batch_elapsed = time.perf_counter() - batch_start
            if batch_elapsed < batch_delay:
                await asyncio.sleep(batch_delay - batch_elapsed)

    # Final stats
    total_time = time.perf_counter() - start_time
    success_count = sum(1 for s, _ in results if s)
    latencies = [l for _, l in results]

    print("-" * 50)
    print("Load test complete!")
    print(f"Total requests: {len(results)}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Actual rate: {len(results) / total_time:.1f} req/s")
    print(f"Success rate: {success_count / len(results) * 100:.1f}%")
    print(f"Latency p50: {sorted(latencies)[len(latencies) // 2] * 1000:.1f}ms")
    print(f"Latency p95: {sorted(latencies)[int(len(latencies) * 0.95)] * 1000:.1f}ms")
    print(f"Latency p99: {sorted(latencies)[int(len(latencies) * 0.99)] * 1000:.1f}ms")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load generator for ML inference platform")
    parser.add_argument("--requests", type=int, default=10000, help="Total requests to send")
    parser.add_argument("--duration", type=int, default=300, help="Duration in seconds")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent workers")
    parser.add_argument("--url", default="http://localhost:8003/predict", help="Target URL")

    args = parser.parse_args()

    config = LoadConfig(
        url=args.url,
        total_requests=args.requests,
        duration_seconds=args.duration,
        concurrent_workers=args.workers,
    )

    asyncio.run(run_load_test(config))
