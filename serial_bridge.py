"""
VOTE-GUARD USB Serial Bridge
Connects to the ESP32 DevKit V1 USB COM port (e.g. COM5 @ 115200 baud).
Automatically reads 'UID:XXXXXXXX' from the hardware reader, verifies it against
the local FastAPI backend, and writes back the LED feedback command ('V', 'D', 'U').
"""

import sys
import time
import json
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api/vote/verify-and-record"
HEALTH_URL = "http://127.0.0.1:8000/health"


def check_backend_health():
    try:
        req = urllib.request.Request(HEALTH_URL)
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                return True
    except Exception:
        pass
    return False


def find_serial_ports():
    try:
        import serial.tools.list_ports
        return serial.tools.list_ports.comports()
    except ImportError:
        return []


def main():
    print("=" * 65)
    print("       VOTE-GUARD: ESP32 Hardware USB Serial Bridge")
    print("=" * 65)

    try:
        import serial
        import serial.tools.list_ports
    except ImportError:
        print("[!] 'pyserial' is not installed.")
        print("    Install it with: pip install pyserial")
        print("    (Note: You can also use the browser's built-in Web Serial button")
        print("     directly in operator.html without installing anything!)")
        return

    # Check backend
    if check_backend_health():
        print("[OK] FastAPI Backend is ONLINE at http://127.0.0.1:8000")
    else:
        print("[!] WARNING: Backend at http://127.0.0.1:8000 not responding.")
        print("    Make sure your FastAPI server is running in another terminal:")
        print("    Command: python main.py")

    # Detect COM ports
    com_list = find_serial_ports()
    if not com_list:
        print("[!] No USB COM ports detected. Please connect your ESP32 via USB cable.")
        return

    print("\nDetected COM Ports:")
    preferred_port = None
    for p in com_list:
        desc = p.description or ""
        print(f"  - {p.device}: {desc}")
        if any(keyword in desc.upper() for keyword in ["CP210", "USB", "CH340", "UART"]):
            if not preferred_port:
                preferred_port = p.device

    # Port selection priority: CLI argument -> Preferred USB/CP210x -> First available
    if len(sys.argv) > 1 and sys.argv[1].upper().startswith("COM"):
        com_port = sys.argv[1].upper()
    elif preferred_port:
        com_port = preferred_port
    else:
        com_port = com_list[0].device

    print(f"\n--> Selected Port: {com_port} @ 115200 baud")

    try:
        ser = serial.Serial(com_port, 115200, timeout=1)
        ser.reset_input_buffer()
        time.sleep(1.5)  # Allow ESP32 serial stabilization
        print(f"[OK] Successfully connected to {com_port}!")
        print("=" * 65)
        print(" READY: Tap any physical RFID tag/card on the RC522 scanner")
        print(" Press Ctrl+C to exit")
        print("=" * 65)

        import re
        while True:
            raw_line = ser.readline()
            if not raw_line:
                continue

            line = raw_line.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            # Check if this line is an ESP32 log or greeting
            if line.startswith("[") or "VOTE-GUARD" in line or "Pin" in line:
                print(f"{line}")
                continue

            extracted_uid = None

            # Pattern 1: Explicit tag/uid prefix (e.g. "UID: 8A 4F 12 3B" or "UID:8A4F123B")
            match = re.search(r"(?:uid|card|tag)\s*:?\s*([0-9a-fA-F]{2}[\s:-]*){4,7}", line, re.I)
            if match:
                clean = re.sub(r"[^0-9a-fA-F]", "", match.group(0)).upper()
                if 8 <= len(clean) <= 14:
                    extracted_uid = clean

            # Pattern 2: Raw hex stream
            if not extracted_uid:
                clean = re.sub(r"[^0-9a-fA-F]", "", line).upper()
                if 8 <= len(clean) <= 14:
                    extracted_uid = clean

            if extracted_uid:
                rfid_uid = extracted_uid
                timestamp = time.strftime("%H:%M:%S")
                print(f"\n[{timestamp}] [HARDWARE TAP] Scanned RFID UID: {rfid_uid}")

                # Call Vote-Guard Backend API
                payload = json.dumps({"rfid_uid": rfid_uid}).encode("utf-8")
                req = urllib.request.Request(
                    API_URL,
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )

                try:
                    with urllib.request.urlopen(req, timeout=5) as response:
                        res = json.loads(response.read().decode("utf-8"))
                        status = res.get("status")
                        led = res.get("hardware_led")
                        voter_name = res.get("voter_name")
                        msg = res.get("message")

                        if status == "ACCEPTED":
                            print(f"  [RESULT: ACCEPTED] -> Sending 'V' -> Solid GREEN LED (2s) | 1 Beep")
                            print(f"  -> Citizen: {voter_name} ({res.get('voter_code')})")
                            print(f"  -> {msg}")
                            ser.write(b"V\n")
                            ser.flush()

                        elif status == "ALREADY_VOTED":
                            print(f"  [RESULT: BLOCKED] -> Sending 'D' -> Strobing RED LED (3s) | 3 Alarms")
                            print(f"  -> Citizen: {voter_name} has ALREADY voted!")
                            print(f"  -> {msg}")
                            ser.write(b"D\n")
                            ser.flush()

                        elif status == "UNREGISTERED":
                            print(f"  [RESULT: UNREGISTERED] -> Sending 'U' -> Solid YELLOW LED (2s) | 2 Chirps")
                            print(f"  -> UID '{rfid_uid}' not registered in electoral roll.")
                            print(f"  -> {msg}")
                            ser.write(b"U\n")
                            ser.flush()

                        else:
                            print(f"  [RESULT: {status}] -> {msg}")
                            ser.write(b"U\n")
                            ser.flush()

                except urllib.error.HTTPError as he:
                    try:
                        err_data = json.loads(he.read().decode("utf-8"))
                        err_msg = err_data.get("detail", str(he))
                    except Exception:
                        err_msg = str(he)
                    print(f"  [HTTP ERROR] {he.code}: {err_msg}")
                    ser.write(b"U\n")
                    ser.flush()

                except Exception as e:
                    print(f"  [CONNECTION ERROR] Backend API request failed: {e}")
                    print("  -> Ensure backend is running: python main.py")
                    ser.write(b"U\n")
                    ser.flush()

    except PermissionError:
        print("\n" + "!" * 65)
        print(f"[!] PERMISSION ERROR: Access to {com_port} is DENIED.")
        print("!" * 65)
        print("This means another program currently has exclusive control of the port:")
        print("  1. Is Arduino IDE Serial Monitor open? -> CLOSE IT.")
        print("  2. Did you click 'Connect Hardware Reader' in operator.html? -> Disconnect it.")
        print("  3. Is another terminal window running serial_bridge.py? -> Close it.")
        print(f"Once free, re-run: python serial_bridge.py")
        print("!" * 65)

    except KeyboardInterrupt:
        print("\n[STOPPED] Serial bridge stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")


if __name__ == "__main__":
    main()
