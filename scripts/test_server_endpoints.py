"""
End-to-end test for the CSV → SQLite demo.

Runs against the live Docker container on localhost:8001.
Start the app first:  docker compose up --build -d
Then run:             python test_app.py
"""

import requests

BASE = "http://localhost:8001"
CSV_PATH = "data/sample_data.csv"


def main():
    print("=" * 50)
    print("CSV → SQLite Demo Test")
    print("=" * 50)

    # 1. Homepage loads
    print("\n[1] GET / (homepage) ...", end=" ")
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200
    assert "csv" in r.text.lower()
    print(f"OK  (HTTP {r.status_code})")

    # 2. Upload CSV
    print("[2] POST /upload (sample.csv) ...", end=" ")
    with open(CSV_PATH, "rb") as f:
        r = requests.post(
            f"{BASE}/upload",
            files={"file": ("sample.csv", f, "text/csv")},
            data={"dataset": "test_run"},
        )
    assert r.status_code == 200
    body = r.json()
    assert body["inserted"] == 30
    print(f"OK  (inserted {body['inserted']} rows)")

    # 3. List datasets
    print("[3] GET /datasets ...", end=" ")
    r = requests.get(f"{BASE}/datasets")
    assert r.status_code == 200
    datasets = r.json()
    assert "test_run" in datasets
    print(f"OK  (datasets: {datasets})")

    # 4. Get single dataset
    print("[4] GET /datasets/test_run ...", end=" ")
    r = requests.get(f"{BASE}/datasets/test_run")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) >= 30
    assert rows[0]["date"] == "2026-01-01"
    print(f"OK  ({len(rows)} rows, first date: {rows[0]['date']})")

    # 5. Export CSV
    print("[5] GET /export ...", end=" ")
    r = requests.get(f"{BASE}/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/csv; charset=utf-8"
    lines = r.text.strip().splitlines()
    assert lines[0] == "dataset,date,temp_c,humidity"
    assert len(lines) > 1
    print(f"OK  ({len(lines) - 1} data rows in CSV)")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()
