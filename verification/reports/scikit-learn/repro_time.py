import sys
import time

print(f"Python version: {sys.version}")

print("\n--- Testing time.clock() ---")
try:
    t = time.clock()
    print(f"time.clock() success: {t}")
except AttributeError as e:
    print(f"time.clock() failed: {e}")
except Exception as e:
    print(f"time.clock() failed with unexpected error: {e}")
