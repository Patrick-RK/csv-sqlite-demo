"""
Seed script — uploads sample_data.csv into the running app.

Usage:
    python scripts/seed_database.py

This sends sample_data.csv to the /upload endpoint so you have
data to play with straight away. Run it after docker compose up.
"""

import json
import urllib.request

BASE = "http://localhost:8001"
CSV_PATH = "data/sample_data.csv"
DATASET_NAME = "sample"


def main():
    print(f"Uploading {CSV_PATH} as dataset '{DATASET_NAME}' ...")

    with open(CSV_PATH, "rb") as f:
        csv_bytes = f.read()

    boundary = "----boundary123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="dataset"\r\n\r\n'
        f"{DATASET_NAME}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{CSV_PATH}"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
    ).encode() + csv_bytes + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{BASE}/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"Done — {result['inserted']} rows inserted into the database.")


if __name__ == "__main__":
    main()
