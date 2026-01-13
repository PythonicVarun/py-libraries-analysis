# Ty Error Analysis Report

This document outlines genuine bugs identified in the codebase based on static analysis by Ty and subsequent verification.

## 1. Unsafe Assertion on `__file__` Attribute

*   **File:** `_distutils_hack/__init__.py`
*   **Line:** 76
*   **Code Snippet:**
    ```python
    assert '_distutils' in core.__file__, core.__file__
    ```
*   **Description:**
    The code asserts that the string `'_distutils'` is present in `core.__file__`. However, in certain Python environments (such as frozen applications, namespace packages, or when using custom loaders), the `__file__` attribute of a module can be `None`. Attempting to use the `in` operator on `None` raises a `TypeError` (crash) rather than the intended `AssertionError` (failure). This makes the check brittle and prone to unexpected termination in edge cases.

## 2. Liskov Substitution Principle Violation in `ZipProvider`

*   **File:** `pkg_resources/__init__.py`
*   **Lines:**
    *   Base definition (`NullProvider`): ~1753
    *   Override (`ZipProvider`): ~2158
*   **Code Snippet:**
    ```python
    # Base class (NullProvider)
    def _has(self, path) -> bool:
        ...

    # Subclass (ZipProvider)
    def _has(self, fspath) -> bool:
        ...
    ```
*   **Description:**
    The `ZipProvider` class overrides the `_has` method of its parent `NullProvider` (via `EggProvider`) but renames the positional argument from `path` to `fspath`. This violates the Liskov Substitution Principle. If a user or internal function calls this method using the keyword argument defined in the base class (e.g., `provider._has(path="...")`), it will fail with a `TypeError: _has() got an unexpected keyword argument 'path'` when the instance is a `ZipProvider`. This breaks polymorphism for the provider interface.
