import subprocess
import sys
import os

TEST_FRUITS = [5, 15, 30]
def run_case(fruits):
    print(f"\n=== Test with {fruits} fruits ===")
    script = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.call([sys.executable, script, "--fruits", str(fruits)])

if __name__ == "__main__":
    for f in TEST_FRUITS:
        run_case(f)
