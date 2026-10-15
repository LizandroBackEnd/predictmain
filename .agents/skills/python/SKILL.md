---
name: python-clean-architecture
description: 'Universal Python clean architecture, strict typing, data validation, and modern toolchain skill. Directs the creation of production-grade, type-safe, maintainable, and high-performance Python code avoiding common anti-patterns. Covers PEP 8 formatting, PEP 484 type hints, Pydantic v2 data models, dunder/magic methods, Ruff configuration, and Pytest fixture patterns across any Python service or framework. Triggers on "python", "py", "pep8", "pydantic", "pytest", "type hints", "ruff", "python clean code".'
license: MIT
metadata:
  author: lizdev
  version: "1.0.0"
---

# CORE PYTHONIC PHILOSOPHY AND PEP COMPLIANCE

## Idiomatic Python and PEP Standards

Modern Python architecture demands strict adherence to idiomatic design principles defined in PEP 20 (The Zen of Python) and formatting rules specified in PEP 8. Code must be explicit, readable, and structurally consistent.

1. Layout and Spacing: Use 4 spaces per indentation level and limit code lines to 79 or 88 characters depending on modern formatter configurations.
2. Explicit Imports: Use absolute imports for clarity and maintainability. Avoid wildcard imports (`from module import *`) which pollute namespaces and break static analysis.
3. Interface Naming: Follow PEP 8 naming conventions: `snake_case` for functions, methods, and variables; `PascalCase` for classes and exceptions; and `UPPER_CASE_WITH_UNDERSCORES` for constants.

## Strict Typing Conventions

Type annotations are critical for static analysis, contract verification, and IDE tooling.

1. Modern Union Syntax: Use PEP 604 pipe syntax (`str | int`) for union types instead of legacy `Union[str, int]` or `Optional[T]` constructs.
2. Generic Collection Subscripting: Prefer native built-in generic collections (`list[str]`, `dict[str, int]`, `tuple[int,...]`) per PEP 585 rather than importing deprecated aliases from `typing` (`List`, `Dict`, `Tuple`).
3. Structural Subtyping: Use `typing.Protocol` for compile-time static duck-typing interfaces rather than forcing explicit class inheritance where structural contracts suffice.

## Absolute Typing Prohibitions

To prevent type leaks and untyped runtime bugs, the following practices are strictly forbidden:

1. Unannotated Parameters or Returns: All public function parameters and return signatures must be explicitly annotated.
2. Implicit `Any`: Never rely on dynamic fallback typing. If an arbitrary type must be accepted safely, annotate it explicitly as `object` or narrow `unknown` data before processing.
3. Mutable Default Parameters: Never use mutable objects (`def fn(items: list[str] = [])`) as default argument values. Use `None` as the default value and instantiate mutables inside the function body.

## Python Data Model Integration

Leverage Python's native special methods (dunder methods) to build intuitive, object-oriented domain abstractions.

1. String Representations: Implement `__repr__` to return unambiguous, developer-focused representations for debugging, and `__str__` for user-facing outputs.
2. Equality and Hashing: Implement `__eq__` alongside `__hash__` for immutable domain value objects to enable usage in sets and dictionary keys.
3. Context Managers: Implement `__enter__` and `__exit__` (or `__aenter__` and `__aexit__` for asynchronous workflows) to guarantee deterministic resource setup and teardown.

---

# DATA VALIDATION AND DOMAIN MODELING (PYDANTIC V2)

## Type-Safe Domain Models

Pydantic v2 provides high-performance schema validation powered by Rust core logic. Domain models must enforce strict field typing and model configuration.

```python
from pydantic import BaseModel, ConfigDict, Field

class EntityModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    id: str = Field(..., description="Unique entity identifier")
    value: int = Field(..., gt=0, description="Positive value threshold")
```

## Validation and Computation Constraints

1. Field Constraints: Apply granular validation constraints using `Field()` (e.g., `gt`, `ge`, `pattern`, `min_length`) directly on model attributes.
2. Model and Field Validators: Use `@field_validator` for field-specific transformation/validation, and `@model_validator(mode='after')` for cross-field consistency checks.
3. Computed Fields: Use `@computed_field` to declare dynamic property methods that automatically include their evaluated values during model serialization (`model_dump()`).

## Immutability Patterns

Domain Entities and Value Objects should enforce immutability by setting `frozen=True` within `ConfigDict`. This ensures instances remain hashable, thread-safe, and protected against unintended field mutations during application runtime.

---

# WORKFLOW: DESIGNING AND TESTING A PYTHON MODULE

Follow this sequential 4-step workflow when authoring or refactoring Python modules:

## Step 1: Define Domain Entities and Value Objects

Model domain concepts using Pydantic v2 or dataclasses with `frozen=True`. Declare explicit attributes, default values, and validation constraints.

## Step 2: Establish Abstract Service Interfaces

Define abstract interfaces or structural protocols using `abc.ABC` with `@abstractmethod` or `typing.Protocol`. Decouple core domain logic from external database, network, or filesystem dependencies.

## Step 3: Implement Concrete Services

Author concrete implementations conforming strictly to the abstract interfaces. Incorporate resource management using context managers (`with` / `async with`) and comprehensive error handling.

## Step 4: Author Pytest Test Suites

Create modular Pytest suites featuring isolated fixtures in `conftest.py`, parametrized test cases, and explicit exception assertions using `pytest.raises()`.

---

# MODERN TOOLCHAIN AND TESTING (RUFF AND PYTEST)

## Fast Linting and Formatting with Ruff

Ruff serves as an all-in-one replacement for Flake8, Black, isort, pydocstyle, and bandit, operating 100x faster via Rust-based execution.

1. Automated Formatting: Enforces consistent 88-character line limits, trailing comma handling, and double-quote string normalization.
2. Import Sorting: Automatically groups and orders standard library imports, third-party dependencies, and local modules per PEP 8 guidelines.

## Advanced Pytest Execution Patterns

1. Parametrized Testing: Use `@pytest.mark.parametrize` to execute a single test function across multiple input payloads and boundary edge-cases.
2. Scoped Fixtures: Structure test dependencies in `conftest.py` using appropriate fixture scopes (`function`, `module`, `session`) and explicit type annotations.
3. Exception Assertions: Verify expected failure modes explicitly using `with pytest.raises(ExpectedException):`.
4. Asynchronous Testing: Test async coroutines using `pytest-asyncio` with explicit `@pytest.mark.asyncio` decorators or global `asyncio_mode = "auto"`.

---

# ADVANCED PATTERNS AND CODE EXAMPLES

## a) Complex Domain Entity with Pydantic v2

### INCORRECT / UNTYPED / UNPYTHONIC

```python
# Unsafe mutable model without constraints or immutability checks
class User:
    def __init__(self, user_id, email, age=18, tags=[]):
        self.user_id = user_id
        self.email = email
        self.age = age
        self.tags = tags  # Dangerous mutable default argument
```

### CORRECT / CLEAN / STRICTLY TYPED

```python
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserAccount(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    account_id: str = Field(..., min_length=5, description="Unique account ID")
    email: EmailStr = Field(..., description="Validated user email address")
    balance: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
    tags: tuple[str,...] = Field(default_factory=tuple)

    @field_validator("account_id")
    @classmethod
    def validate_account_id_prefix(cls, value: str) -> str:
        if not value.startswith("ACC-"):
            raise ValueError("Account ID must begin with 'ACC-' prefix")
        return value
```

## b) Async Context Manager Resource Lifecycle

### INCORRECT / UNTYPED / UNPYTHONIC

```python
# Unsafe resource connection without async context manager or cleanup guarantee
class DBConnection:
    async def connect(self):
        print("Connecting")

    async def close(self):
        print("Closing")

async def run_query(db):
    await db.connect()
    # If an error occurs here, db.close() is never called
    res = "data"
    await db.close()
    return res
```

### CORRECT / CLEAN / STRICTLY TYPED

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

class DatabaseSession:
    async def execute_query(self, query: str) -> list[dict[str, object]]:
        return [{"status": "success", "query": query}]

    async def close(self) -> None:
        # Release connection pools cleanly
        pass

@asynccontextmanager
async def get_database_session(connection_string: str) -> AsyncGenerator[DatabaseSession, None]:
    session = DatabaseSession()
    try:
        yield session
    finally:
        await session.close()
```

## c) Dependency Inversion Interface (Protocol & ABC)

### INCORRECT / UNTYPED / UNPYTHONIC

```python
# Tight coupling directly to concrete third-party service
import sendgrid

class NotificationService:
    def __init__(self):
        self.client = sendgrid.SendGridAPIClient(api_key="secret")

    def notify(self, user_id, message):
        self.client.send_email(user_id, message)
```

### CORRECT / CLEAN / STRICTLY TYPED

```python
from typing import Protocol

class NotificationSender(Protocol):
    async def send_notification(self, recipient: str, message: str) -> bool:
        # Send a notification to a given recipient
...

class ConsoleNotificationSender:
    async def send_notification(self, recipient: str, message: str) -> bool:
        print(f"Sending notification to {recipient}: {message}")
        return True

class UserNotifier:
    def __init__(self, sender: NotificationSender) -> None:
        self._sender = sender

    async def alert_user(self, recipient: str, message: str) -> bool:
        return await self._sender.send_notification(recipient, message)
```

## d) Comprehensive Pytest Module with Fixtures

### INCORRECT / UNTYPED / UNPYTHONIC

```python
# Manual setup without fixtures, parametrized tests, or exception verification
def test_user_creation():
    u = User("ACC-12345", "test@example.com")
    assert u.account_id == "ACC-12345"

    try:
        User("INVALID", "bad-email")
        assert False  # Manual failure check
    except Exception:
        assert True
```

### CORRECT / CLEAN / STRICTLY TYPED

```python
import pytest
from pydantic import ValidationError

@pytest.fixture
def valid_account_payload() -> dict[str, str]:
    return {
        "account_id": "ACC-99887",
        "email": "developer@example.com",
    }

@pytest.mark.parametrize(
    ("invalid_id", "invalid_email"),
    [
        ("USR-12345", "developer@example.com"),
        ("ACC-12345", "not-an-email"),
        ("INVALID", "bad-email"),
    ],
)
def test_user_account_validation_failures(invalid_id: str, invalid_email: str) -> None:
    with pytest.raises(ValidationError):
        UserAccount(account_id=invalid_id, email=invalid_email) # type: ignore[call-arg]
```

---

# ANTI-PATTERNS AND PREVENTION CHECKLIST

Avoid these common Python anti-patterns:

## 1. Mutable Default Arguments

- Anti-pattern: Using mutable data structures (`list`, `dict`, `set`) as default values in function definitions (`def process(items=[])`).
- Corrective Action: Use `None` as the default argument value and initialize the mutable object inside the function body.

```python
# INCORRECT
def append_item(value: str, target: list[str] = []) -> list[str]:
    target.append(value)
    return target

# CORRECT
def append_item(value: str, target: list[str] | None = None) -> list[str]:
    if target is None:
        target = []
    target.append(value)
    return target
```

## 2. Bare Exception Handling

- Anti-pattern: Catching arbitrary exceptions with `except:` or `except BaseException:`, which catches system interrupts (`KeyboardInterrupt`, `SystemExit`) and masks bugs.
- Corrective Action: Catch specific exception types (`except ValueError:`) or `except Exception:` when handling general runtime errors.

```python
# INCORRECT
try:
    value = int(user_input)
except:
    value = 0

# CORRECT
try:
    value = int(user_input)
except ValueError:
    value = 0
```

## 3. String-Based Type Comments (Legacy Typing)

- Anti-pattern: Using legacy inline `# type: int` comments or string-wrapped annotations instead of modern Python 3.10+ type hints.
- Corrective Action: Write native inline type annotations using standard type syntax (`var: int | str`).

```python
# INCORRECT
data = []  # type: list[str]

# CORRECT
data: list[str] = []
```

## 4. Overusing Unbounded `**kwargs`

- Anti-pattern: Accepting arbitrary `**kwargs` parameters in service functions instead of defining explicit, typed argument contracts.
- Corrective Action: Declare explicit keyword arguments or encapsulate complex option structures into a typed Pydantic model or Dataclass.

## 5. Unmanaged Resource Lifecycles

- Anti-pattern: Opening files, sockets, or database connections without deterministic cleanup, risking resource leaks on unexpected exceptions.
- Corrective Action: Enclose all resource operations within a `with` or `async with` context manager block.

---

# PRODUCTION TOOLCHAIN CONFIGURATION PRESETS

This `pyproject.toml` preset unifies Ruff linting/formatting, Mypy strict type checking, and Pytest execution settings for modern Python projects:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "python-clean-architecture"
version = "1.0.0"
description = "Production-grade clean architecture Python service"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.10.0",
    "pytest>=8.2.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.4.0",
]

[tool.ruff]
target-version = "py311"
line-length = 88
indent-width = 4

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "ARG",  # flake8-unused-arguments
    "SIM",  # flake8-simplify
]
ignore = ["E501"]

[tool.ruff.lint.isort]
combine-as-imports = true
known-first-party = ["src"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "pydantic.*"
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py", "*_test.py"]
```
