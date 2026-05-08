"""
End-to-end test for the CSV → SQLite demo.

Runs against the live Docker container on localhost:8001.
Start the app first:  docker compose up --build -d
Then run:             python scripts/test_server_endpoints.py
"""

import json
import urllib.request

BASE = "http://localhost:8001"
CSV_PATH = "data/sample_data.csv"


def get(path):
    resp = urllib.request.urlopen(f"{BASE}{path}")
    return resp


def main():
    print("=" * 50)
    print("CSV → SQLite Demo Test")
    print("=" * 50)

    # 1. Homepage loads
    print("\n[1] GET / (homepage) ...", end=" ")
    r = get("/")
    assert r.status == 200
    body = r.read().decode()
    assert "csv" in body.lower()
    print(f"OK  (HTTP {r.status})")

    # 2. Upload CSV
    print("[2] POST /upload (sample_data.csv) ...", end=" ")
    with open(CSV_PATH, "rb") as f:
        csv_bytes = f.read()
    boundary = "----boundary123"
    payload = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="dataset"\r\n\r\n'
        f"test_run\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="sample_data.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
    ).encode() + csv_bytes + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{BASE}/upload",
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    r = urllib.request.urlopen(req)
    result = json.loads(r.read())
    assert result["inserted"] == 30
    print(f"OK  (inserted {result['inserted']} rows)")

    # 3. List datasets
    print("[3] GET /datasets ...", end=" ")
    r = get("/datasets")
    datasets = json.loads(r.read())
    assert "test_run" in datasets
    print(f"OK  (datasets: {datasets})")

    # 4. Get single dataset
    print("[4] GET /datasets/test_run ...", end=" ")
    r = get("/datasets/test_run")
    rows = json.loads(r.read())
    assert len(rows) >= 30
    assert rows[0]["date"] == "2026-01-01"
    print(f"OK  ({len(rows)} rows, first date: {rows[0]['date']})")

    # 5. Export CSV
    print("[5] GET /export ...", end=" ")
    r = get("/export")
    assert r.headers["content-type"] == "text/csv; charset=utf-8"
    lines = r.read().decode().strip().splitlines()
    assert lines[0] == "dataset,date,temp_c,humidity"
    assert len(lines) > 1
    print(f"OK  ({len(lines) - 1} data rows in CSV)")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()
