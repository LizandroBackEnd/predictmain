"""Domain entities and value objects for dataset metadata, ingestion, and profiling."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ManifestData:
    """Represents the raw dataset metadata and cryptographic provenance."""

    manifest_version: str
    source_url: str
    file_name: str
    ingestion_date: str
    n_rows: int
    n_columns: int
    columns: List[str]
    size_bytes: int
    sha256: str
    data_layer: str = "raw"
    file_format: str = "CSV"
    encoding: str = "UTF-8"
    delimiter: str = ","
    transformed: bool = False
    cleaned: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest entity to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating a dataset file structure and checksum."""

    is_valid: bool
    n_rows: int
    n_columns: int
    columns: List[str]
    size_bytes: int
    sha256: str
    error_message: Optional[str] = None


@dataclass(frozen=True)
class IngestionResult:
    """Result of an ingestion execution."""

    success: bool
    is_new: bool
    manifest: ManifestData
    message: str


@dataclass
class ColumnMetric:
    """Summary statistics for a single column."""

    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_value: Optional[float] = None
    distribution: Optional[Dict[str, int]] = None


@dataclass
class DatasetSummary:
    """Aggregated dataset profiling metrics."""

    total_rows: int
    total_columns: int
    columns: List[ColumnMetric]
    target_distribution: Dict[str, int]
    failure_modes_distribution: Dict[str, int]
