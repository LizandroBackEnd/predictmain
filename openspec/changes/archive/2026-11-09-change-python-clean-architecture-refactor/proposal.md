# Proposal: Refactor Python ML Service for Clean Code, KISS, and Clean Architecture

- **Change ID**: `change-python-clean-architecture-refactor`
- **Status**: PROPOSED
- **Author**: Lead Software Architect & Lizdev
- **Date**: 2026-11-09
- **Domain**: `ml_service` (Python Data Science & ML Inference Engine)

---

## 1. Problem Statement

The `ml_service` codebase currently handles the data ingestion, profiling, statistical treatment, and transformation pipelines for the AI4I 2020 Predictive Maintenance Dataset. While the 40 unit tests pass, the internal structure suffers from significant technical debt, code smells, and architectural drift:

1. **Architectural Confusion (Clean Architecture Violation)**:
   - Modules are organized in flat, disparate directories (`ingestion/`, `profiling/`, `null_treatment/`, `outlier_analysis/`, `transformation/`) without clear layer boundaries between Domain (entities and business invariants), Application (use cases), Infrastructure (I/O, filesystem, serialization), and Interfaces (CLI).
   - Hardcoded rules and configuration dictionaries are tangled with execution logic.

2. **Code Smells & KISS Violations**:
   - Monolithic `cli.py` (>260 lines) acts as a god-script handling argument parsing, ANSI print formatting, error interception, and manual instantiation of concrete services.
   - Boilerplate methods and imperative loops where idiomatic Python standard library and vectorized Pandas operations should be used.

3. **Typing & Modern Python Standards Non-Compliance**:
   - Violates `.agents/skills/python/SKILL.md` by using legacy `typing` constructs (`from typing import Any, Dict, List, Optional`) instead of native PEP 585 generic collections (`list[str]`, `dict[str, Any]`) and PEP 604 union operators (`str | None`).
   - Untyped method parameters (e.g. `y=None` in `DerivedFeatureAdder`) and inconsistent docstrings.
   - Inconsistent modeling: mixing mutable dataclasses and dictionary casting without validation constraints.

---

## 2. Proposed Solution

Refactor the `ml_service` following **Clean Architecture**, **Clean Code**, and the **KISS** (Keep It Simple, Stupid) principle, strictly respecting the existing business logic, mathematical constants, and data outputs:

### A. Concentric Layer Structure (Clean Architecture)

Restructure `ml_service/src/` into explicit, screaming architectural layers:

```text
ml_service/src/
├── domain/                      # Enterprise & Application Invariants (zero external deps)
│   ├── models.py                # Value objects & entities (Pydantic v2 / strict frozen dataclasses)
│   ├── null_rules.py            # Rules, dispositions, and imputation contracts
│   └── outlier_rules.py         # Outlier detection bounds & physical limits
│
├── application/                 # Use Cases & Orchestration Logic
│   ├── ingestion_service.py     # CSV validation, hashing, manifest generation
│   ├── profiling_service.py     # Statistical telemetry profiling
│   ├── null_treatment_service.py# Missing value handling
│   ├── outlier_service.py       # Outlier analysis and Winsorization
│   └── pipeline_service.py      # Feature engineering & Sklearn pipeline build
│
├── infrastructure/              # Frameworks, Storage & I/O
│   ├── paths.py                 # Centralized, immutable project paths
│   ├── joblib_storage.py        # Serializer / deserializer for fitted pipelines
│   └── markdown_reporter.py     # Profiling markdown report generation
│
└── interfaces/cli/              # Delivery Layer (Command-Line Interface)
    ├── main.py                  # Entrypoint router
    └── commands/                # Modular command handlers (ingest, profile, etc.)
```

### B. Pythonic Standards & Clean Code

- **Strict Typing**: Enforce PEP 585 (`list`, `dict`), PEP 604 (`X | None`), and complete type annotations on all public functions.
- **Pydantic v2 / Immutability**: Domain models configured with `frozen=True` and clear validation bounds.
- **KISS & Refactoring**: Clean, self-documenting method names, removal of redundant conversions, and separation of concerns.

---

## 3. User Stories & Value Proposition

- **As a Developer/Architect**: I can navigate `ml_service/` and immediately understand where domain rules end and application services begin without wading through monolithic scripts.
- **As a Maintainer**: I have type safety and clear protocols, preventing silent runtime bugs and import ambiguities.
- **As the Platform Core (Next.js)**: The HTTP/CLI contracts of `ml_service` remain 100% predictable, rock-solid, and regression-free.

---

## 4. Scope Boundaries

### In-Scope
- Relocating and organizing existing Python modules into Clean Architecture layers.
- Modernizing type hints and docstrings to PEP 8, PEP 585, PEP 604, and PEP 484.
- Upgrading domain models to Pydantic v2 / strict frozen models.
- Modularizing `cli.py` into decoupled interface commands.
- Updating test suites and ensuring all 40 tests pass with zero regressions.

### Out-of-Scope
- Changing mathematical algorithms, imputation formulas, IQR multipliers, or Winsorization logic.
- Adding new ML model architectures or modifying Next.js web application code in `src/app/`.
- Changing the dataset files in `data/raw/` or `data/processed/`.

---

## 5. Alternatives Considered

1. **In-place file cleanup without directory restructuring**:
   - *Tradeoff*: Less file movement, but fails to enforce Clean Architecture boundaries and leaves files cluttered in flat feature folders. Rejected.
2. **Complete pipeline rewrite**:
   - *Tradeoff*: High risk of introducing subtle numeric or preprocessing discrepancies that would invalidate `pipeline.joblib`. Rejected.

---

## 6. Risks & Mitigation Plan

- **Risk**: Test import paths breaking during module reorganization.
  - *Mitigation*: Update `conftest.py` and test imports incrementally; execute the test suite after each atomic move.
- **Risk**: Serialization compatibility with `pipeline.joblib`.
  - *Mitigation*: Ensure custom transformers (e.g. `DerivedFeatureAdder`) maintain identical class names and signatures for compatibility with existing artifacts.

---

## 7. Next Steps

Upon user approval of this proposal, proceed to:
1. `/sdd-spec change-python-clean-architecture-refactor`
2. Followed by `/sdd-design`, `/sdd-tasks`, and `/sdd-apply`.

