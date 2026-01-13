# Static Analysis Bug Report (Ty)

This report identifies genuine bugs and potential runtime issues discovered by the `ty` static analysis tool. While many reports are false positives due to SQLAlchemy's dynamic nature, the following items represent actionable improvements or fixes.

## 1. Genuine Bugs & Runtime Risks

### A. Unsafe Result Unwrapping (Null Pointer Risk)
*   **File:** `examples/asyncio/async_orm.py`
*   **Line:** 102
*   **Description:** The code executes `a1 = result.first()` and immediately attempts to assign `a1.data = "new data"`.
*   **Issue:** `result.first()` returns `None` if the query produces no results. Attempting to set an attribute on `None` will raise an `AttributeError` at runtime.
*   **Impact:** High. Although example data is inserted, this pattern promotes unsafe database interaction.

### B. Type Comparison Crash (NoneType Comparison)
*   **File:** `lib/sqlalchemy/dialects/mssql/base.py`
*   **Lines:** 1778, 1787
*   **Description:** The MSSQL type compiler performs the check: `if self.dialect.server_version_info < MS_2008_VERSION:`.
*   **Issue:** If the dialect is used in an "offline" mode (e.g., for SQL generation without a live connection), `server_version_info` may be `None`. In Python 3, comparing `None < tuple` raises a `TypeError`.
*   **Impact:** Medium. Can crash SQL generation for MSSQL when not connected to a server.

### C. Unresolved Global Reference (Execution Order Dependency)
*   **File:** `examples/performance/bulk_inserts.py`
*   **Lines:** 35, 45, etc.
*   **Description:** The script uses `global engine` inside `setup_database` but never declares `engine` at the module level.
*   **Issue:** Static analysis cannot verify the existence or type of `engine`. While the script works when run as a main module because `setup_database` is called first, it violates standard scoping practices.

### D. Unresolved Name in Space Invaders
*   **File:** `examples/space_invaders/space_invaders.py`
*   **Line:** 164
*   **Description:** `_COLOR_PAIRS` is used in the `Glyph.draw` method but is only defined inside the `main()` function scope via a `global` declaration.
*   **Issue:** If any part of the rendering logic is invoked before `main()` reaches the initialization line, it will trigger a `NameError`. It is safer to define `_COLOR_PAIRS = {}` at the module level.
*   **Impact:** Low (Maintenance).

---

## 2. False Positives (Dynamic Typing Artifacts)

The following reports are classified as **False Positives** typical of SQLAlchemy's descriptor-based architecture:

### A. Column vs. Instance Attribute Confusion
*   **File:** `examples/materialized_paths/materialized_paths.py`
*   **Line:** 104 (`len(self.path)`)
*   **Ty Report:** `Expected Sized, found Unknown | Column[str]`
*   **Reason:** Ty sees `self.path` as the `Column` object defined on the class. At runtime, when `move_to` is called on an instance, `self.path` is a string. This is a standard SQLAlchemy pattern that static analyzers often struggle with without specific plugins.

### B. Missing Attributes on Base Classes
*   **File:** `examples/generic_associations/generic_fk.py`
*   **Line:** 151 (`customer.addresses`)
*   **Ty Report:** `Object of type Customer has no attribute addresses`
*   **Reason:** The `addresses` attribute is added dynamically via a relationship or a `declared_attr` mixin. Ty fails to trace the dynamic injection of this attribute.

### C. Shadowing of `Session`
*   **File:** `examples/extending_query/filter_public.py`
*   **Line:** 89
*   **Ty Report:** `Object of type sessionmaker[Session] is not assignable to <class 'Session'>`
*   **Reason:** The code uses `Session = sessionmaker(...)`. Ty interprets `Session` as the class type from the import and views the assignment as an attempt to redefine the type itself rather than creating a factory instance with the same name.
