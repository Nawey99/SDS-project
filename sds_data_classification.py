import enum
import datetime
from dataclasses import dataclass
from typing import List

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
        
        # Classification rules for storage tier assignment
        if artifact.importance == Importance.CRITICAL or usage == UsageFrequency.HIGH:
            return StorageTier.HOT
        elif usage == UsageFrequency.MEDIUM or artifact.importance == Importance.STANDARD:
            return StorageTier.WARM
        else:
            return StorageTier.COLD

    def process_artifacts(self, artifacts: List[Artifact]) -> List[dict]:
        """Process a list of artifacts and return classification results."""
        results = []
        for artifact in artifacts:
            tier = self.classify_and_assign(artifact)
            results.append({
                "id": artifact.id,
                "name": artifact.name,
                "type": artifact.type.value,
                "usage_frequency": artifact.get_usage_frequency().value,
                "importance": artifact.importance.value,
                "assigned_tier": tier.value
            })
        return results

# Prototype simulation
def main():
    # Sample artifacts
    artifacts = [
        Artifact(
            id="A001",
            name="Rare_Manuscript.jpg",
            type=ArtifactType.PHOTOGRAPH,
            access_count=15,
            last_accessed=datetime.datetime.now() - datetime.timedelta(days=5),
            importance=Importance.CRITICAL
        ),
        Artifact(
            id="A002",
            name="Meeting_Notes.pdf",
            type=ArtifactType.DOCUMENT,
            access_count=3,
            last_accessed=datetime.datetime.now() - datetime.timedelta(days=10),
            importance=Importance.STANDARD
        ),
        Artifact(
            id="A003",
            name="Old_Video.mp4",
            type=ArtifactType.VIDEO,
            access_count=0,
            last_accessed=datetime.datetime.now() - datetime.timedelta(days=60),
            importance=Importance.LOW
        )
    ]

    # Initialize classifier
    classifier = SDSClassifier()
    
    # Process artifacts and print results
    results = classifier.process_artifacts(artifacts)
    print("SDS Classification and Storage Assignment Results:")
    for result in results:
        print(f"Artifact {result['id']} ({result['name']}):")
        print(f"  Type: {result['type']}")
        print(f"  Usage Frequency: {result['usage_frequency']}")
        print(f"  Importance: {result['importance']}")
        print(f"  Assigned Tier: {result['assigned_tier']}")
        print()

if __name__ == "__main__":
    main()