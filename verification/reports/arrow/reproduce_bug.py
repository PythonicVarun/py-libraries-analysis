import os
import shutil
import tempfile

def reproduce():
    # Simulate the environment where ARROW_HOME is missing
    # We ensure ARROW_HOME is not set for this test
    if "ARROW_HOME" in os.environ:
        del os.environ["ARROW_HOME"]
    
    # This mirrors ci/conan/all/conanfile.py:290
    top_level = os.environ.get("ARROW_HOME")
    print(f"top_level is: {top_level}")
    
    try:
        # This mirrors the bug in ci/conan/all/conanfile.py:291
        # os.path.join(top_level, "cpp")
        result = os.path.join(top_level, "cpp")
        print(f"Result: {result}")
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {type(e).__name__}: {e}")
    else:
        print("Did not catch TypeError! (Unexpected)")

if __name__ == "__main__":
    reproduce()
