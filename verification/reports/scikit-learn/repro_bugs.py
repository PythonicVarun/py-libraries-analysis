import sys
import time
from sklearn import metrics

print(f"Python version: {sys.version}")

print("\n--- Testing time.clock() ---")
try:
    t = time.clock()
    print(f"time.clock() success: {t}")
except AttributeError as e:
    print(f"time.clock() failed: {e}")
except Exception as e:
    print(f"time.clock() failed with unexpected error: {e}")

print("\n--- Testing sklearn.metrics.jaccard_similarity_score ---")
try:
    # Attempting to access the function directly as the script does
    # Note: The script does 'from sklearn.metrics import jaccard_similarity_score'
    # which is equivalent to getattr(metrics, 'jaccard_similarity_score') check here
    func = getattr(metrics, 'jaccard_similarity_score')
    print("sklearn.metrics.jaccard_similarity_score found")
except AttributeError as e:
    print(f"sklearn.metrics.jaccard_similarity_score failed: {e}")
except Exception as e:
    print(f"sklearn.metrics.jaccard_similarity_score failed with unexpected error: {e}")
