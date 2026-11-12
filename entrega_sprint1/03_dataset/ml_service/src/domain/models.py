"""Domain entities and value objects for dataset metadata, ingestion, profiling,
null treatment, outlier analysis, and transformation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


# ---------------------------------------------------------------------------
# Dominio de ingesta
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ManifestData:
    """Represents the raw dataset metadata and cryptographic provenance."""

    manifest_version: str
    source_url: str
    file_name: str
    ingestion_date: str
    n_rows: int
    n_columns: int
    columns: list[str]
    size_bytes: int
    sha256: str
    data_layer: str = "raw"
    file_format: str = "CSV"
    encoding: str = "UTF-8"
    delimiter: str = ","
    transformed: bool = False
    cleaned: bool = False

    def to_dict(self) -> dict[str, object]:
        """Convert manifest entity to a JSON-serializable dictionary."""
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validating a dataset file structure and checksum."""

    is_valid: bool
    n_rows: int
    n_columns: int
    columns: list[str]
    size_bytes: int
    sha256: str
    error_message: str | None = None


@dataclass(frozen=True)
class IngestionResult:
    """Result of an ingestion execution."""

    success: bool
    is_new: bool
    manifest: ManifestData
    message: str


# ---------------------------------------------------------------------------
# Dominio de perfilado
# ---------------------------------------------------------------------------


@dataclass
class ColumnMetric:
    """Summary statistics for a single column."""

    name: str
    dtype: str
    non_null_count: int
    null_count: int
    unique_count: int
    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    median_value: float | None = None
    std_value: float | None = None
    distribution: dict[str, int] | None = None


@dataclass
class QualityReport:
    """Data quality findings: duplicates, nulls, and physical range violations."""

    duplicate_rows: int
    null_counts: dict[str, int]        # {nombre_columna: cantidad_nulos}
    out_of_range: dict[str, list[int]] # {nombre_columna: [índices de filas]}
    invalid_type_values: dict[str, int] # {nombre_columna: cantidad de valores inesperados}
    total_issues: int


@dataclass
class DatasetSummary:
    """Aggregated dataset profiling metrics."""

    total_rows: int
    total_columns: int
    columns: list[ColumnMetric]
    target_distribution: dict[str, int]
    failure_modes_distribution: dict[str, int]
    quality_report: QualityReport | None = None


# ---------------------------------------------------------------------------
# Dominio de tratamiento de nulos
# ---------------------------------------------------------------------------


@dataclass
class ColumnNullStat:
    """Missing-value statistics for one column before treatment."""

    column: str
    null_count_before: int
    null_pct_before: float
    disposition: str
    strategy: str | None
    imputed_count: int = 0
    dropped_rows: int = 0


@dataclass
class NullTreatmentResult:
    """Full outcome of the null-treatment pipeline run."""

    source_file: str
    output_file: str
    executed_at: str
    rows_before: int
    rows_after: int
    rows_dropped: int
    total_nulls_before: int
    total_values_imputed: int
    column_stats: list[ColumnNullStat]
    rows_with_nulls_before: int  # registros que tenían ≥1 nulo


# ---------------------------------------------------------------------------
# Dominio de análisis de atípicos
# ---------------------------------------------------------------------------


@dataclass
class ColumnOutlierStat:
    """Outlier detection results for a single sensor column."""

    column: str
    decision: str
    outlier_type: str
    detection_method: str

    # Estadísticas IQR
    q1: float
    q3: float
    iqr: float
    iqr_fence_low: float
    iqr_fence_high: float
    iqr_outliers_count: int

    # Estadísticas de percentiles
    p1: float
    p99: float
    percentile_outliers_count: int

    # Rango físico UCI
    uci_physical_min: float
    uci_physical_max: float
    outside_physical_range: int

    # Conteos posteriores a la decisión
    records_detected: int   # unión de atípicos IQR + percentiles
    records_modified: int   # cuántos fueron recortados (CAP)
    records_excluded: int   # cuántas filas fueron eliminadas


@dataclass
class OutlierAnalysisResult:
    """Full outcome of the outlier analysis pipeline."""

    source_file: str
    executed_at: str
    rows_input: int
    rows_output: int
    total_detected: int
    total_modified: int
    total_excluded: int
    column_stats: list[ColumnOutlierStat]


# ---------------------------------------------------------------------------
# Dominio de transformación
# ---------------------------------------------------------------------------


@dataclass
class TransformationResult:
    """Outcome of a pipeline fit_transform or transform call."""

    rows: int
    feature_columns: list[str]
    pipeline_path: str | None   # None si aún no se ha guardado
