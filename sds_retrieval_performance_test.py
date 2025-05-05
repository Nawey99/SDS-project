import enum
import random
import asyncio
import time
from dataclasses import dataclass
from typing import List, Dict
from statistics import mean, stdev

# Enum definitions for classification categories
class UsageFrequency(enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class ArtifactType(enum.Enum):
    PHOTOGRAPH = "Photograph"
    DOCUMENT = "Document"
    VIDEO = "Video"

class Importance(enum.Enum):
    CRITICAL = "Critical"
    STANDARD = "Standard"
    LOW = "Low"

class StorageTier(enum.Enum):
    HOT = "Hot Storage"
    WARM = "Warm Storage"
    COLD = "Cold Storage"

# Data class to represent an artifact
@dataclass
class Artifact:
    id: str
    name: str
    type: ArtifactType
    access_count: int
    last_accessed: float  # Unix timestamp
    importance: Importance

    def get_usage_frequency(self) -> UsageFrequency:
        """Determine usage frequency based on access count in the last 30 days."""
        days_since_access = (time.time() - self.last_accessed) / (24 * 3600)
        if days_since_access > 30:
            return UsageFrequency.LOW
        accesses_per_month = self.access_count
        if accesses_per_month > 10:
            return UsageFrequency.HIGH
        elif accesses_per_month >= 1:
            return UsageFrequency.MEDIUM
        return UsageFrequency.LOW

# Classification and storage assignment logic
class SDSClassifier:
    def classify_and_assign(self, artifact: Artifact) -> StorageTier:
        """Classify artifact and assign it to a storage tier."""
        usage = artifact.get_usage_frequency()
        if artifact.importance == Importance.CRITICAL or usage == UsageFrequency.HIGH:
            return StorageTier.HOT
        elif usage == UsageFrequency.MEDIUM or artifact.importance == Importance.STANDARD:
            return StorageTier.WARM
        else:
            return StorageTier.COLD

# Mock storage backend for retrieval simulation
class StorageBackend:
    def __init__(self):
        # Simulated base latencies (in seconds)
        self.latencies = {
            StorageTier.HOT: 0.010,  # 10 ms
            StorageTier.WARM: 0.050,  # 50 ms
            StorageTier.COLD: 0.200  # 200 ms
        }
        self.max_concurrent_requests = 1000  # System concurrency limit
        self.current_requests = 0
        self.lock = asyncio.Lock()

    async def retrieve_artifact(self, artifact_id: str, tier: StorageTier) -> float:
        """Simulate artifact retrieval with tier-specific latency."""
        async with self.lock:
            if self.current_requests >= self.max_concurrent_requests:
                raise RuntimeError("System overloaded: too many concurrent requests")
            self.current_requests += 1
        try:
            # Simulate latency with random variation (±10%)
            base_latency = self.latencies[tier]
            latency = base_latency * random.uniform(0.9, 1.1)
            await asyncio.sleep(latency)
            return latency
        finally:
            async with self.lock:
                self.current_requests -= 1

# Retrieval performance tester
class RetrievalPerformanceTester:
    def __init__(self, artifacts: List[Artifact]):
        self.classifier = SDSClassifier()
        self.storage = StorageBackend()
        self.artifacts = artifacts
        # Assign tiers to artifacts
        self.artifact_tiers = {a.id: self.classifier.classify_and_assign(a) for a in artifacts}

    async def simulate_retrieval(self, artifact_id: str) -> tuple:
        """Simulate a single retrieval and return latency."""
        try:
            start_time = time.time()
            tier = self.artifact_tiers[artifact_id]
            latency = await self.storage.retrieve_artifact(artifact_id, tier)
            return (artifact_id, latency, None)
        except Exception as e:
            return (artifact_id, 0, str(e))

    async def run_test(self, requests_per_second: int, duration_seconds: int) -> Dict:
        """Run retrieval test under specified load."""
        print(f"\nRunning retrieval test: {requests_per_second} requests/sec for {duration_seconds} seconds")
        total_requests = requests_per_second * duration_seconds
        interval = 1 / requests_per_second if requests_per_second > 0 else 1
        results = []
        errors = 0
        start_time = time.time()

        # Launch concurrent retrieval tasks
        for i in range(total_requests):
            artifact_id = random.choice([a.id for a in self.artifacts])
            results.append(asyncio.create_task(self.simulate_retrieval(artifact_id)))
            await asyncio.sleep(interval)

        # Collect results
        completed = await asyncio.gather(*results, return_exceptions=True)
        elapsed_time = time.time() - start_time

        # Process results
        latencies = []
        tier_latencies = {tier: [] for tier in StorageTier}
        for artifact_id, latency, error in completed:
            if error:
                errors += 1
            else:
                latencies.append(latency)
                tier = self.artifact_tiers[artifact_id]
                tier_latencies[tier].append(latency)

        return {
            "total_requests": total_requests,
            "elapsed_time": elapsed_time,
            "throughput": total_requests / elapsed_time if elapsed_time > 0 else 0,
            "avg_latency": mean(latencies) if latencies else 0,
            "latency_std": stdev(latencies) if len(latencies) > 1 else 0,
            "error_rate": errors / total_requests if total_requests > 0 else 0,
            "tier_latencies": {
                tier: {
                    "avg": mean(tl) if tl else 0,
                    "count": len(tl)
                } for tier, tl in tier_latencies.items()
            }
        }

    def analyze_results(self, results: Dict):
        """Print analysis of test results."""
        print(f"\nTest Analysis:")
        print(f"Total Requests: {results['total_requests']}")
        print(f"Elapsed Time: {results['elapsed_time']:.2f} seconds")
        print(f"Throughput: {results['throughput']:.2f} requests/sec")
        print(f"Average Latency: {results['avg_latency']*1000:.2f} ms")
        if results['latency_std'] > 0:
            print(f"Latency Std Dev: {results['latency_std']*1000:.2f} ms")
        print(f"Error Rate: {results['error_rate']*100:.2f}%")
        print("\nTier-Specific Performance:")
        for tier, stats in results['tier_latencies'].items():
            print(f"{tier.value}: {stats['count']} requests, Avg Latency: {stats['avg']*1000:.2f} ms")

# Generate sample artifacts
def generate_artifacts(num: int) -> List[Artifact]:
    artifacts = []
    types = list(ArtifactType)
    importances = list(Importance)
    for i in range(num):
        artifact_type = random.choice(types)
        artifacts.append(Artifact(
            id=f"A{i:04d}",
            name=f"Artifact_{i}.{artifact_type.value.lower()}",
            type=artifact_type,
            access_count=random.randint(0, 20),
            last_accessed=time.time() - random.randint(0, 60) * 24 * 3600,
            importance=random.choice(importances)
        ))
    return artifacts

async def main():
    # Generate 1000 sample artifacts
    artifacts = generate_artifacts(1000)
    tester = RetrievalPerformanceTester(artifacts)

    # Test scenarios
    test_scenarios = [
        {"requests_per_second": 10, "duration": 30},   # Low load
        {"requests_per_second": 100, "duration": 30},  # Medium load
        {"requests_per_second": 500, "duration": 30}   # High load
    ]

    for scenario in test_scenarios:
        results = await tester.run_test(scenario["requests_per_second"], scenario["duration"])
        tester.analyze_results(results)

if __name__ == "__main__":
    asyncio.run(main())