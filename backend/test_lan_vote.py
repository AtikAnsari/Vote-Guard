"""
Full Suite Test for Vote-Guard over LAN IPv4 interface.
Tests:
1. UNREGISTERED Card -> YELLOW
2. ACCEPTED Vote (Fresh/Reset Voter) -> GREEN
3. DUPLICATE Vote Attempt (Same Voter again) -> RED
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import urllib.request
import json
from pathlib import Path

import os
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.database import engine
from sqlalchemy import text

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")

def send_vote(uid, label):
    url = f"{BASE_URL}/api/vote/verify-and-record"
    payload = json.dumps({"rfid_uid": uid}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode())
        print(f"\n[{label}]")
        print(f"  HTTP Code    : {res.status}")
        print(f"  Parsed Status: {data.get('status')}")
        print(f"  Hardware LED : {data.get('hardware_led')}")
        print(f"  Message      : {data.get('message')}")
        print(f"  Voter Name   : {data.get('voter_name')}")
        return data

if __name__ == "__main__":
    print(f"--- Running API verification on {BASE_URL} ---")

    # Step A: Reset has_voted to False for registered voter 71411605
    with engine.begin() as conn:
        conn.execute(text("UPDATE voters SET has_voted = 0, voted_at = NULL WHERE rfid_uid = '71411605'"))

    # Test 1: Fresh registered voter -> EXPECT ACCEPTED / GREEN
    d1 = send_vote("71411605", "TEST 1: FRESH REGISTERED VOTER FIRST TAP")
    assert d1.get("status") == "ACCEPTED"
    assert d1.get("hardware_led") == "GREEN"

    # Test 2: Same voter second tap -> EXPECT ALREADY_VOTED / RED
    d2 = send_vote("71411605", "TEST 2: SAME VOTER SECOND TAP (DUPLICATE BLOCKED)")
    assert d2.get("status") == "ALREADY_VOTED"
    assert d2.get("hardware_led") == "RED"

    # Test 3: Unregistered RFID tag -> EXPECT UNREGISTERED / YELLOW
    d3 = send_vote("UNKNOWN_TAG_7777", "TEST 3: UNREGISTERED RFID TAG")
    assert d3.get("status") == "UNREGISTERED"
    assert d3.get("hardware_led") == "YELLOW"

    print("\n==============================================")
    print("ALL 3 PATHS (GREEN / RED / YELLOW) PASSED 100%!")
    print("==============================================")
