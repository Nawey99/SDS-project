import enum
import random
import datetime
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
    last_accessed: datetime.datetime
    importance: Importance

    def get_usage_frequency(self) -> UsageFrequency:
        """Determine usage frequency based on access count in the last 30 days."""
        days_since_access = (datetime.datetime.now() - self.last_accessed).days
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

# Mock storage resource manager
class StorageResourceManager:
    def __init__(self):
        # Initial storage capacities (in arbitrary units, e.g., GB)
        self.capacities = {
            StorageTier.HOT: 100,
            StorageTier.WARM: 500,
            StorageTier.COLD: 1000
        }
        # Current usage
        self.usage = {
            StorageTier.HOT: 0,
            StorageTier.WARM: 0,
            StorageTier.COLD: 0
        }
        # Size per artifact (in arbitrary units)
        self.artifact_sizes = {
            ArtifactType.PHOTOGRAPH: 1,
            ArtifactType.DOCUMENT: 0.5,
            ArtifactType.VIDEO: 5
        }

    def add_artifact(self, artifact: Artifact, tier: StorageTier) -> bool:
        """Add artifact to a storage tier and adjust resources if needed."""
        size = self.artifact_sizes[artifact.type]
        if self.usage[tier] + size > self.capacities[tier] * 0.8:  # 80% capacity threshold
            self.adjust_resources(tier)
        if self.usage[tier] + size <= self.capacities[tier]:
            self.usage[tier] += size
            return True
        return False

    def adjust_resources(self, tier: StorageTier):
        """Simulate resource scaling by increasing capacity."""
        increase = self.capacities[tier] * 0.5  # Increase capacity by 50%
        self.capacities[tier] += increase
        print(f"Scaled {tier.value} capacity to {self.capacities[tier]} units")

    def get_usage_stats(self) -> Dict:
        """Return current storage usage and capacity stats."""
        return {
            "capacities": self.capacities.copy(),
            "usage": self.usage.copy()
        }

# Scalability test simulator
class ScalabilityTester:
    def __init__(self):
        self.classifier = SDSClassifier()
        self.resource_manager = StorageResourceManager()
        self.tier_counts = {tier: 0 for tier in StorageTier}
        self.classification_times = []

    def generate_artifact(self, artifact_id: int) -> Artifact:
        """Generate a random artifact."""
        types = list(ArtifactType)
        importances = list(Importance)
        artifact_type = random.choice(types)
        return Artifact(
            id=f"A{artifact_id:04d}",
            name=f"Artifact_{artifact_id}.{artifact_type.value.lower()}",
            type=artifact_type,
            access_count=random.randint(0, 20),
            last_accessed=datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 60)),
            importance=random.choice(importances)
        )

    def run_test(self, rate: int, duration_minutes: float) -> Dict:
        """Simulate artifact ingestion at a given rate for a duration."""
        print(f"\nRunning test: {rate} artifacts/min for {duration_minutes} minutes")
        total_artifacts = int(rate * duration_minutes)
        interval = 60 / rate if rate > 0 else 1  # Seconds between artifacts
        start_time = time.time()

        for i in range(total_artifacts):
            artifact = self.generate_artifact(i)
            # Measure classification time
            class_start = time.time()
            tier = self.classifier.classify_and_assign(artifact)
            class_time = time.time() - class_start
            self.classification_times.append(class_time)
            # Assign to storage
            if self.resource_manager.add_artifact(artifact, tier):
                self.tier_counts[tier] += 1
            # Simulate real-time ingestion
            time.sleep(max(0, interval - (time.time() - start_time) / (i + 1)))

        # Collect results
        elapsed_time = time.time() - start_time
        stats = self.resource_manager.get_usage_stats()
        return {
            "total_artifacts": total_artifacts,
            "elapsed_time": elapsed_time,
            "tier_counts": self.tier_counts.copy(),
            "avg_classification_time": mean(self.classification_times) if self.classification_times else 0,
            "classification_time_std": stdev(self.classification_times) if len(self.classification_times) > 1 else 0,
            "storage_stats": stats
        }

    def analyze_results(self, results: Dict):
        """Print analysis of test results."""
        print(f"\nTest Analysis:")
        print(f"Total Artifacts Processed: {results['total_artifacts']}")
        print(f"Elapsed Time: {results['elapsed_time']:.2f} seconds")
        print(f"Average Classification Time: {results['avg_classification_time']*1000:.2f} ms")
        if results['classification_time_std'] > 0:
            print(f"Classification Time Std Dev: {results['classification_time_std']*1000:.2f} ms")
        print("\nStorage Tier Distribution:")
        for tier, count in results['tier_counts'].items():
            print(f"{tier.value}: {count} artifacts")
        print("\nStorage Usage and Capacity:")
        for tier in StorageTier:
            usage = results['storage_stats']['usage'][tier]
            capacity = results['storage_stats']['capacities'][tier]
            print(f"{tier.value}: {usage:.2f}/{capacity:.2f} units ({usage/capacity*100:.1f}%)")

def main():
    tester = ScalabilityTester()
    test_scenarios = [
        {"rate": 10, "duration": 5},    # Low load
        {"rate": 100, "duration": 5},   # Medium load
        {"rate": 1000, "duration": 5}   # High load
    ]

    for scenario in test_scenarios:
        results = tester.run_test(scenario["rate"], scenario["duration"])
        tester.analyze_results(results)
        # Reset tier counts for next test
        tester.tier_counts = {tier: 0 for tier in StorageTier}
        tester.classification_times = []

if __name__ == "__main__":
    main()