# Bug Report: Unhandled Environment Variable in Conan Recipe

## Summary
A potential runtime crash was identified in the Conan recipe for Apache Arrow. The script attempts to use the result of `os.environ.get("ARROW_HOME")` directly in `os.path.join()` without verifying that the environment variable is set.

## Affected File and Lines
**File:** `ci/conan/all/conanfile.py`
**Lines:** 290–302

## Technical Details
In the `source()` method of the `ArrowConan` class, the following logic is used to handle local development builds:

```python
290:            top_level = os.environ.get("ARROW_HOME")
291:            shutil.copytree(os.path.join(top_level, "cpp"),
292:                            os.path.join(self.source_folder, "cpp"))
293:            shutil.copytree(os.path.join(top_level, "format"),
...
301:                shutil.copy(os.path.join(top_level, top_level_file),
302:                            self.source_folder)
```

### Problem
`os.environ.get("ARROW_HOME")` returns `None` if the `ARROW_HOME` environment variable is not defined. The `os.path.join()` function does not accept `NoneType` as an argument.

### Impact
If a user attempts to run this specific code path (e.g., when building a version not present in `conandata.yml`) without having `ARROW_HOME` defined, the execution will terminate with a `TypeError`:
`TypeError: expected str, bytes or os.PathLike object, not NoneType`

## Reproduction
The following Python snippet reproduces the error:

```python
import os
import shutil

# Ensure the variable is unset
if "ARROW_HOME" in os.environ:
    del os.environ["ARROW_HOME"]

top_level = os.environ.get("ARROW_HOME")
# This call raises TypeError
os.path.join(top_level, "cpp")
```

## Recommended Fix
Add a check to ensure `top_level` is valid or provide a fallback. If the environment variable is mandatory for this code path, a descriptive error message should be raised:

```python
top_level = os.environ.get("ARROW_HOME")
if not top_level:
    raise ConanException("ARROW_HOME environment variable must be set when building from local source.")
```
