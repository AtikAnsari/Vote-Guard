# Vote-Guard: Research Validation and Traceability Checklist

This document provides a strict, verifiable engineering traceability matrix connecting every academic claim made in the research paper to concrete implementation code, empirical test runs, and explicit system boundaries.

---

## 1. Technical Claims vs. Codebase Implementation Traceability

| Academic Claim / Architecture Requirement | Implementation Evidence (Repository File & Function) | Verification Status | Notes / Ground Truth |
| :--- | :--- | :--- | :--- |
| **Edge Hardware RFID Transceiver** | `firmware/vote_guard_esp32/vote_guard_esp32.ino`<br>Lines 16–22: `MFRC522 rfid(SS_PIN, RST_PIN)`<br>SPI Bus: SCK(18), MISO(19), MOSI(23), SS(5), RST(4) | **VERIFIED** | Physical ISO/IEC 14443A card UID extraction via hardware SPI interface. |
| **Edge Diagnostic Actuator State Mapping** | `firmware/vote_guard_esp32/vote_guard_esp32.ino`<br>Lines 25–28: Pins Green(25), Yellow(26), Red(27), Buzzer(32)<br>Lines 135–182: `handleActuatorPattern(status, led_code)` | **VERIFIED** | Active-high outputs. Green: 3 blinks + 1 tone. Yellow: 3 blinks + 3 warning tones. Red: 4 rapid strobes + 3 error buzzes. |
| **Wi-Fi Station Network Transport** | `firmware/vote_guard_esp32/vote_guard_esp32.ino`<br>Lines 85–130: `connectWiFi()`<br>`config.h`: `WIFI_SSID`, `WIFI_PASS`, `BACKEND_URL` | **VERIFIED** | Station mode (802.11 b/g/n). Tested with assigned IP `192.168.1.27` connecting to laptop backend at `192.168.1.9:8000`. |
| **Zero-Decision Untrusted Edge Principle** | `firmware/vote_guard_esp32/vote_guard_esp32.ino`<br>Lines 195–260: `verifyRFIDWithBackend()` | **VERIFIED** | ESP32 stores zero voter lists, zero tally logic, and zero citizen identity. Acts purely as an I/O sensor/actuator peripheral. |
| **Authoritative REST Verification Router** | `backend/routers/vote.py`<br>Lines 24–105: `@router.post("/verify")`<br>Schema: `RFIDVerifyRequest(rfid_uid: str)` | **VERIFIED** | Centralized FastAPI endpoint handling validation, state transition, and event broadcasting. |
| **Atomic Single-Vote Concurrency Enforcer** | `backend/routers/vote.py`<br>Lines 62–79: Conditional update statement<br>`UPDATE voters SET has_voted = 1, voted_at = :now WHERE rfid_uid = :uid AND has_voted = 0` | **VERIFIED** | Evaluates `rowcount`. If 1, vote accepted. If 0 (and voter exists), rejected as duplicate (`ALREADY_VOTED`). |
| **Two-Factor KYC Demographics Binding** | `backend/routers/admin.py`<br>Lines 85–140: `@router.post("/voters")`<br>`backend/models.py`: `VoterCredential` & `Voter` | **VERIFIED** | Multi-table constraints: `aadhaar_num` (12 digits, Unique), `epic_card_id` (Unique), `assigned_rfid_uid` (Unique), foreign key in `voters`. |
| **Non-Repudiable Audit Logging** | `backend/routers/vote.py` & `backend/routers/admin.py`<br>`backend/models.py`: `AuditLog`<br>Table: `audit_logs` | **VERIFIED** | Records `event_type`, `rfid_uid`, `status`, `details`, `operator_id`, `ip_address`, and `created_at`. |
| **Role-Based Access Control (RBAC)** | `backend/auth.py` & `backend/routers/auth.py`<br>`models.py`: `AdminUser`<br>Roles: `admin` (full KYC & reset), `operator` (view-only) | **VERIFIED** | Password hashing via `bcrypt` / `passlib`. Session-based token authorization for protected endpoints. |
| **Dual-Channel Operator Web Synchronization** | `operator.html` & `operator.js`<br>Lines 45–90 in `operator.js`: Long-polling interval (500ms)<br>Endpoint: `/api/vote/latest-event` | **VERIFIED** | Mirrors edge LED and buzzer state in browser within <100ms of backend event resolution. |

---

## 2. Empirical Test Runs and Live Verification Evidence

The following test suites were executed live on the Vote-Guard hardware and backend stack:

### Test Run 1: Unregistered RFID Tag
- **Input Tag UID:** `E24B10A9` (Physical MIFARE card not in database)
- **API Request:** `POST /api/vote/verify` with payload `{"rfid_uid": "E24B10A9"}`
- **HTTP Response Code:** `200 OK`
- **Response JSON:** `{"status": "UNREGISTERED", "hardware_led": "YELLOW", "voter_name": null, "message": "RFID Tag is not registered"}`
- **Hardware Actuation:** Yellow LED blinks 3 times (150ms on / 150ms off); active buzzer sounds 3 warning beeps (2.4 kHz).
- **Web Interface:** Operator portal displays amber warning banner: `"VOTER ID NOT REGISTERED"`.
- **Database Outcome:** Zero rows modified in `voters`; rejection event recorded in `audit_logs`.

### Test Run 2: Fresh Registered Citizen Vote
- **Input Tag UID:** `71411605` (Assigned to registered citizen: Shaikh Noman, Aadhaar: `333445679876`, EPIC: `ABC3456789`)
- **Initial DB State:** `has_voted = 0`, `voted_at = NULL`
- **API Request:** `POST /api/vote/verify` with payload `{"rfid_uid": "71411605"}`
- **HTTP Response Code:** `200 OK`
- **Response JSON:** `{"status": "ACCEPTED", "hardware_led": "GREEN", "voter_name": "Shaikh Noman", "message": "Vote successfully cast"}`
- **Hardware Actuation:** Green LED blinks 3 times (200ms on / 100ms off); active buzzer emits 1 confirmation tone (600ms).
- **Web Interface:** Operator portal displays emerald success card with citizen demographics: `"Shaikh Noman - VOTE RECORDED"`.
- **Database Outcome:** `voters.has_voted` updated to `1`; `voted_at` updated to `2026-10-29 17:15:32`; audit log row inserted with `status: ACCEPTED`.

### Test Run 3: Duplicate Voting Attempt (Same Tag Re-Scanned)
- **Input Tag UID:** `71411605` (Re-presented immediately to RC522 reader)
- **Current DB State:** `has_voted = 1`
- **API Request:** `POST /api/vote/verify` with payload `{"rfid_uid": "71411605"}`
- **Conditional SQL:** `UPDATE voters SET has_voted = 1 ... WHERE rfid_uid = '71411605' AND has_voted = 0` $\rightarrow$ `rows_affected = 0`
- **HTTP Response Code:** `200 OK`
- **Response JSON:** `{"status": "ALREADY_VOTED", "hardware_led": "RED", "voter_name": "Shaikh Noman", "message": "Voter has already cast their ballot"}`
- **Hardware Actuation:** Red LED emits 4 rapid strobe flashes (80ms on / 80ms off); active buzzer fires 3 alarm buzzes.
- **Web Interface:** Operator portal displays crimson warning alert: `"DUPLICATE VOTE BLOCKED - Voter has already cast ballot"`.
- **Database Outcome:** `voters.has_voted` remains `1`; timestamp unchanged; security exception logged in `audit_logs` with `event_type: DUPLICATE_VOTE_BLOCKED`.

---

## 3. Explicit Security Boundaries and Prototype Limitations

In adherence to strict academic honesty, the research paper explicitly delineates what the prototype achieves versus existing production gaps:

1. **RFID UID Physical Cloning Vulnerability:**
   - *Limitation:* The RC522 reader extracts only the 4-byte / 7-byte factory Unique Identifier (UID) from ISO/IEC 14443 Type A cards. Low-cost programmable "magic cards" (UID changeable tags) and handheld transceivers (Proxmark3) can clone this identifier over-the-air.
   - *Paper Treatment:* Explicitly acknowledged in Section VIII. Stated as the primary justification for 2FA KYC binding and biometric expansion.

2. **Plaintext HTTP on Local Wi-Fi Network:**
   - *Limitation:* The current prototype communicates over HTTP over standard 802.11 b/g/n Wi-Fi without TLS 1.3 encryption, making packets vulnerable to local eavesdropping (packet sniffing via Wireshark) or ARP spoofing on a compromised router.
   - *Paper Treatment:* Documented in Section VIII as an engineering prototype constraint. Production requirements (HTTPS with certificate pinning, TLS 1.3, 802.11i WPA3 Enterprise) are detailed as prerequisite deployment controls.

3. **Absence of Microcontroller Hardware Cryptographic Engine (HSM):**
   - *Limitation:* The ESP32 does not use a hardware secure element (e.g., ATECC608A) or cryptographic challenge-response authentication with the RFID card.
   - *Paper Treatment:* Clarified in Sections V and VIII. The paper notes that Vote-Guard relies on architectural defense-in-depth at the backend rather than claiming physical smartcard tamper-resistance.

4. **Non-Certified Prototype Status:**
   - *Limitation:* The system is a university laboratory prototype designed for voter identity verification and duplicate prevention. It is not an end-to-end voting machine (EVM), does not contain electronic ballot tallying hardware, and is not certified under national election commission standards.
   - *Paper Treatment:* Emphasized in Section I, Section VIII, and Section X to avoid over-claiming.

---

## 4. Pending Experiments and Future Empirical Extensions

The following items are designated in the paper as future empirical extensions rather than fabricated data:

- **Large-Scale Concurrency Stress Testing:** Formal Apache JMeter / Locust stress testing simulating $\ge 200$ concurrent edge polling booths submitting simultaneous validation requests to measure database lock contention and throughput saturation.
- **TLS 1.3 Latency Overhead Quantification:** Benchmarking the exact handshake latency overhead introduced when upgrading ESP32 HTTP client to HTTPS with TLS 1.3 mTLS certificates.
- **Biometric Fingerprint False Acceptance / False Rejection (FAR/FRR) Evaluation:** Quantifying template matching accuracy when integrating an optical fingerprint module (e.g., AS608 / R307) into the ESP32 SPI/UART bus alongside the RC522.

