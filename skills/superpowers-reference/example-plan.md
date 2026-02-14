# Implementation Plan: Email Validation for User Registration

**Goal:** Add email format validation to the user registration module so invalid emails are rejected before account creation.

**Architecture:** Single-module change — add a validator function, then integrate it into the existing registration endpoint.

**Tech Stack:** Python, pytest

**Execution:** Implement each task using strict RED-GREEN-REFACTOR. Do not proceed to the next task until all tests pass.

---

## Task 1: Create email validator function

**Files:** `validators.py` (create), `test_validators.py` (create)

### Step 1 — RED: Write failing test

```python
# test_validators.py
from validators import validate_email

def test_valid_email_accepted():
    assert validate_email("user@example.com") is True

def test_missing_at_sign_rejected():
    assert validate_email("userexample.com") is False

def test_missing_domain_rejected():
    assert validate_email("user@") is False
```

```bash
pytest test_validators.py -v
```

Expected output:
```
FAILED test_validators.py::test_valid_email_accepted - ModuleNotFoundError
```

### Step 2 — GREEN: Minimal implementation

```python
# validators.py
import re

def validate_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))
```

```bash
pytest test_validators.py -v
```

Expected output:
```
test_validators.py::test_valid_email_accepted PASSED
test_validators.py::test_missing_at_sign_rejected PASSED
test_validators.py::test_missing_domain_rejected PASSED
```

### Step 3 — REFACTOR: None needed

Code is already minimal and clear.

### Step 4 — Full suite check

```bash
pytest -v
```

All tests pass, no regressions.

### Step 5 — Commit

```bash
git add validators.py test_validators.py
git commit -m "feat: add email format validator with tests"
```

---

## Task 2: Integrate validator into registration endpoint

**Files:** `registration.py` (modify), `test_registration.py` (modify)

### Step 1 — RED: Write failing test

```python
# test_registration.py (add to existing tests)
from registration import register_user

def test_register_rejects_invalid_email():
    result = register_user(name="Alice", email="not-an-email")
    assert result["success"] is False
    assert "email" in result["error"].lower()
```

```bash
pytest test_registration.py::test_register_rejects_invalid_email -v
```

Expected output:
```
FAILED test_registration.py::test_register_rejects_invalid_email - AssertionError
```

The test fails because `register_user` does not yet check email format.

### Step 2 — GREEN: Minimal implementation

```python
# registration.py (modify existing function)
from validators import validate_email

def register_user(name: str, email: str) -> dict:
    if not validate_email(email):
        return {"success": False, "error": "Invalid email format"}
    # ... existing registration logic unchanged ...
    return {"success": True, "user_id": create_account(name, email)}
```

```bash
pytest test_registration.py::test_register_rejects_invalid_email -v
```

Expected output:
```
test_registration.py::test_register_rejects_invalid_email PASSED
```

### Step 3 — REFACTOR: None needed

Integration is a single guard clause — already clean.

### Step 4 — Full suite check

```bash
pytest -v
```

All tests pass, no regressions.

### Step 5 — Commit

```bash
git add registration.py test_registration.py
git commit -m "feat: reject invalid emails during registration"
```
