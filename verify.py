#!/usr/bin/env python3
"""Verify every Opus file in index.json returns HTTP 200."""
import json, urllib.request, sys, concurrent.futures
from pathlib import Path

INDEX = Path(__file__).parent / "index.json"

def check(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except: return False

def main():
    data = json.loads(INDEX.read_text())
    files = data.get("files", [])
    print(f"Verifying {len(files)} Opus files in {data['library']}...")
    ok = 0; fail = 0; failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(check, f["url"]): f for f in files}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            if fut.result(): ok += 1
            else: fail += 1; failed.append(futures[fut]["file"])
            if i % 100 == 0: print(f"  {i}/{len(files)}: ok={ok} fail={fail}", flush=True)
    print(f"\nResult: {ok} ok, {fail} fail out of {len(files)}")
    if failed:
        print("\nFailed files (first 20):")
        for f in failed[:20]: print(f"  - {f}")
        sys.exit(1)

if __name__ == "__main__": main()
