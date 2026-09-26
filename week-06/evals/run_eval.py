import json
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

API_URL = "http://localhost:8000/normalize"

def run_eval():
    with open(os.path.join(os.path.dirname(__file__), "cases.json"), "r") as f:
        cases = json.load(f)

    passed = 0
    failed = []

    for case in cases:
        response = requests.post(API_URL, json={"title": case["input"]})
        result = response.json()
        actual = result.get("canonical_title")
        expected = case["expected"]

        if actual == expected:
            passed += 1
            print(f"✅ '{case['input']}' → {actual}")
        else:
            failed.append(case)
            print(f"❌ '{case['input']}' → got '{actual}', expected '{expected}'")

    total = len(cases)
    score = f"{passed}/{total}"
    print(f"\nScore: {score} ({round(passed/total*100)}%)")

    if failed:
        print("\nFailed cases:")
        for c in failed:
            print(f"  - {c['input']} (expected {c['expected']})")

if __name__ == "__main__":
    run_eval()