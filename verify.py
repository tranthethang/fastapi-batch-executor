# verify.py - Verification for fastapi-batch-executor
import os

import requests
from dotenv import load_dotenv

load_dotenv()
APP_PORT = os.getenv("APP_PORT", "60062")
BASE_URL = f"http://127.0.0.1:{APP_PORT}"
HEALTH_URL = f"{BASE_URL}/health"
EXECUTE_URL = f"{BASE_URL}/batch/run"


def run_verification():
    print("=== FASTAPI BATCH EXECUTOR VERIFICATION ===")

    # Test 1: Health Check
    print(f"[*] Testing connection to {HEALTH_URL}...")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        response.raise_for_status()
        print(f"[+] Server is UP: {response.json()}")
    except Exception as e:
        print(f"[-] CRITICAL: Server is DOWN or unreachable: {str(e)}")
        return

    # Test 2: Reachability & Schema Validation (Intentional 422)
    print(f"[*] Testing reachability (sending empty payload)...")
    try:
        response = requests.post(EXECUTE_URL, json={}, timeout=5)
        if response.status_code == 422:
            print(f"[+] Endpoint {EXECUTE_URL} is reachable and validating schema.")
        else:
            print(f"[!] Endpoint returned unexpected status {response.status_code}")
    except Exception as e:
        print(f"[-] Test failed: {str(e)}")

    # Test 3: Actual Sync Execution (Minimal valid payload)
    print(f"[*] Testing minimal valid sync execution...")
    valid_payload = {
        "project_id": "test-project",
        "mode": "sync",
        "global_files": [],
        "tasks": [{"task_id": "task-1", "prompt": "Say hello world"}],
    }
    try:
        response = requests.post(EXECUTE_URL, json=valid_payload, timeout=10)
        if response.status_code == 200:
            print(f"[+] Sync execution successful: {response.json()}")
        elif response.status_code == 500:
            print(
                f"[!] Endpoint reached but failed with 500 (likely missing API keys): {response.text}"
            )
        else:
            print(
                f"[!] Endpoint returned status {response.status_code}: {response.text}"
            )
    except Exception as e:
        print(f"[-] Test failed: {str(e)}")


if __name__ == "__main__":
    run_verification()
