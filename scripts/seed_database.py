"""
Seed script — uploads sample.csv into the running app.

Usage:
    python seed.py

This sends sample.csv to the /upload endpoint so you have
data to play with straight away. Run it after docker compose up.
"""

import requests

BASE = "http://localhost:8001"
CSV_PATH = "data/sample_data.csv"
DATASET_NAME = "sample"


def main():
    print(f"Uploading {CSV_PATH} as dataset '{DATASET_NAME}' ...")

    with open(CSV_PATH, "rb") as f:
        r = requests.post(
            f"{BASE}/upload",
            files={"file": (CSV_PATH, f, "text/csv")},
            data={"dataset": DATASET_NAME},
        )

    if r.status_code == 200:
        count = r.json()["inserted"]
        print(f"Done — {count} rows inserted into the database.")
    else:
        print(f"Error: HTTP {r.status_code}")
        print(r.text)


if __name__ == "__main__":
    main()
