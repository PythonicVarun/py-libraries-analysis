# Wrapt Bug Report

This document outlines genuine bugs and quality issues identified in the `wrapt` codebase based on static analysis and runtime verification.

## 1. Missing Dependency in Benchmarks

**File:** `docs/benchmarks.py`
**Line:** 2

### Code Snippet
```python
import wrapt  # https://pypi.python.org/pypi/wrapt
import decorator  # https://pypi.python.org/pypi/decorator
```

### Description
The `docs/benchmarks.py` script imports the `decorator` library, but this package is not listed in `pyproject.toml`, `setup.py`, or `docs/requirements.txt`. Consequently, attempting to run this benchmark script results in a `ModuleNotFoundError: No module named 'decorator'`, rendering the benchmark unusable without manual intervention.

---

## 2. Incorrect Default Type in Importer

**File:** `src/wrapt/importer.py`
**Line:** 144

### Code Snippet
```python
    with _post_import_hooks_lock:
        hooks = _post_import_hooks.pop(name, ())
```

### Description
The `_post_import_hooks` dictionary manages lists of hook callbacks. When retrieving and removing hooks for a specific module using `.pop()`, the default value is specified as a tuple `()` instead of an empty list `[]`.

While iterating over the result works for both types, this is a type safety violation because the variable `hooks` is expected to be a `List` (consistent with the dictionary values). If future code were to attempt list-specific operations (e.g., modification) on this return value, it would fail. To maintain type consistency, the default value should be `[]`.

---

## 3. Unresolved Attribute on `synchronized` Function

**File:** `src/wrapt/decorators.py`
**Line:** 487

### Code Snippet
```python
            # meta lock on this wrapper itself, to control the
            # creation and assignment of the lock attribute against
            # the context.

            with synchronized._synchronized_meta_lock:
                # We need to check again for whether the lock we want
```

### Description
The code attaches a custom attribute, `_synchronized_meta_lock`, to the `synchronized` function object at the end of the file (Line 523). While valid in dynamic Python, static type checkers (like `ty` / `mypy`) flag this as an error because the standard `function` type does not possess this attribute.

This requires explicit type casting or a `type: ignore` directive at the usage site to inform the static analyzer that the attribute is guaranteed to exist at runtime.
