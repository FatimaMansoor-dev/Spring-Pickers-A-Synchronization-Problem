import subprocess
import sys
import os

def run_case(fruits):
    print(f"\n=== Test with {fruits} fruits ===")
    script = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.call([sys.executable, script, "--fruits", str(fruits)])

if __name__ == "__main__":
    for f in [5, 15, 30]:
        run_case(f)
