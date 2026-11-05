# Vote-Guard: RFID-Based Voter Verification & Duplicate-Vote Prevention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.14-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![ESP32](https://img.shields.io/badge/Microcontroller-ESP32%20DevKit%20V1-E7352C.svg?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![License](https://img.shields.io/badge/Project-Academic%20PBL--I-555555.svg?style=for-the-badge)](https://silveroakuni.ac.in)

> **Academic Engineering Prototype:** Vote-Guard is an edge-to-cloud electoral verification platform that combines physical RFID smart tokens, a local two-factor demographic credential binding layer (simulating pre-authorized Aadhaar & EPIC voter rolls), and an atomic backend database engine to enforce an **exactly-once voting constraint** across distributed polling kiosks in local testing environments.
>
> *Disclaimer: This project is an educational engineering prototype developed for academic review. It implements local relational database validations and does not interface with live government identity APIs (such as UIDAI Aadhaar or ECI). It is not certified for statutory or governmental elections.*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Project Objectives](#3-project-objectives)
4. [Key Features](#4-key-features)
5. [Technology Stack](#5-technology-stack)
6. [System Architecture](#6-system-architecture)
7. [Project Workflow](#7-project-workflow)
8. [Project Folder Structure](#8-project-folder-structure)
9. [Installation and Setup](#9-installation-and-setup)
10. [Backend Configuration](#10-backend-configuration)
11. [Database Configuration](#11-database-configuration)
12. [ESP32 and RC522 Hardware Setup (Optional)](#12-esp32-and-rc522-hardware-setup-optional)
13. [API Overview](#13-api-overview)
14. [Demo Instructions](#14-demo-instructions)
15. [Security & Architectural Scope](#15-security--architectural-scope)
16. [Current Project Status](#16-current-project-status)
17. [Future Enhancements](#17-future-enhancements)
18. [Contributors & Project Credits](#18-contributors--project-credits)

---

## 1. Project Overview

**Vote-Guard** is a full-stack electoral security and verification prototype engineered as a Problem Based Learning (PBL-I) project. It addresses two core vulnerabilities in conventional electoral operations: **voter impersonation** and **duplicate voting (double voting)** across polling stations.

The platform introduces a multi-tier verification workflow:
- **Physical RFID Smart Tokens:** 13.56 MHz High-Frequency RFID cards/fobs mapped uniquely to individual voter records.
- **Local Two-Factor Demographic Binding (Simulated 2FA KYC):** Maps each physical token to pre-authorized citizen credential records (Aadhaar number and Election Photo Identity Card / EPIC) in a local relational database, simulating a validated government voter roll without requiring external API access.
- **Atomic Verification Engine:** An asynchronous **FastAPI backend** running conditional SQL updates on **MySQL 8.0 (InnoDB)** with row-level write-locks to prevent concurrent duplicate votes.
- **Dual-Channel Hardware & Web Sync:** Real-time visual and acoustic feedback at the polling kiosk via **ESP32 microcontroller actuators** (Green/Yellow/Red LEDs and an active buzzer) synchronized with browser-based operator and administrative dashboards.

---

## 2. Problem Statement

Conventional manual and standalone electronic electoral systems face operational challenges:
1. **Voter Impersonation & Forgery:** Traditional paper voter slips or unverified physical photo cards can be forged or presented by unauthorized proxies.
2. **Cross-Booth Double Voting:** Without synchronized, real-time cross-booth verification, an individual can attempt to cast ballots at multiple physical polling stations.
3. **Time-of-Check to Time-of-Use (TOCTOU) Exploits:** Systems that read a voter's status before writing without atomic database locks are susceptible to race conditions if two kiosks process the same credential at the same millisecond.
4. **Lack of Immediate Edge Feedback:** Polling officers often lack instantaneous audio-visual hardware cues to detect duplicate or unregistered cards directly at the card reader terminal.

---

## 3. Project Objectives

- **Enforce Exactly-Once Invariant:** Mathematically guarantee that every registered voter record transitions from `has_voted = FALSE` to `TRUE` exactly once ($V = 1$), rejecting subsequent attempts ($V > 1$) in both automated test suites and real-time operational testing.
- **Relational Demographic Binding:** Prevent multi-card issuance by enforcing strict database uniqueness constraints across RFID UIDs, simulated Aadhaar numbers, and EPIC codes.
- **Atomic Concurrency Protection:** Eliminate race conditions between kiosks by performing atomic conditional updates (`UPDATE ... WHERE has_voted = FALSE`) backed by MySQL InnoDB exclusive row write-locks.
- **Edge Actuator Feedback:** Provide instant hardware diagnostic signals (Green/Yellow/Red LEDs + Buzzer) at the physical reader and push live scan events to the operator terminal.
- **Application-Level Audit Trail:** Record an append-only log entry for every interaction (vote cast, duplicate attempt, unregistered card presentation) capturing timestamps, client socket IP addresses, and forensic event details.

---

## 4. Key Features

- **Atomic Verification Engine:** Evaluates RFID tags using a single conditional write query in MySQL. If `has_voted` is `FALSE`, the vote is committed in one atomic step; if already `TRUE`, zero rows are modified, safely triggering a duplicate alarm.
- **Simulated 2FA KYC Voter Registration:** Administrative onboarding portal that enforces relational uniqueness constraints across RFID UIDs, Aadhaar numbers, and EPIC codes, simulating a pre-authorized government voter registry.
- **Dual Communication Modes (Edge Hardware):**
  - **Wi-Fi Mode (Primary):** Microcontroller directly transmits JSON payloads over HTTP POST to the FastAPI backend via local wireless LAN.
  - **USB Serial Bridge Mode (Diagnostic / Fallback):** Microcontroller streams card UIDs over USB COM port (115200 baud) for environments utilizing the local Python bridge script or browser Web Serial API.
- **Role-Based Access Control (RBAC):** Protected sessions for **System Administrators** (analytics, voter registry, audit trail, credential management) and **Booth Operators** (live polling terminal).
- **Live Booth Operator Terminal:** Real-time web terminal featuring Web Audio API sound synthesis, card verification status banners, and automatic reset timers between voters.
- **Audit Logging & Turnout Analytics:** Tracks turnout metrics, pending votes, and blocked fraud attempts with interactive visualization powered by Chart.js.

---

## 5. Technology Stack

### Frontend
- **Markup & Structure:** HTML5 (Semantic Structure)
- **Styling:** CSS3 (Custom Responsive Design System, CSS Variables, Status Badges)
- **Client Logic:** Vanilla JavaScript (ES6+, Fetch API, Web Audio API, Web Serial API)
- **Data Visualization:** Chart.js (CDN-hosted analytics charts)

### Backend
- **Framework:** FastAPI (High-performance asynchronous Python web framework)
- **ASGI Web Server:** Uvicorn (Asynchronous server implementation)
- **ORM & Data Mapping:** SQLAlchemy 2.0 (Relational mapping and session management)
- **Validation:** Pydantic (Type enforcement and schema validation)
- **Security & Authentication:** Python Cryptography & Secrets (`hashlib.pbkdf2_hmac` SHA-256 with 100,000 iterations, RFC 7519 HMAC-SHA256 JWT sessions)
- **Environment Management:** Python-Dotenv

### Database
- **Engine:** MySQL 8.0+ (InnoDB storage engine supporting ACID transactions and row-level write-locks)
- **Driver:** PyMySQL (Pure-Python MySQL client)
- **Charset:** `utf8mb4` with `utf8mb4_unicode_ci` collation

### Hardware Integration (Local Prototype Testing)
- **Microcontroller:** ESP32 DevKit V1 (30-pin, Dual-Core 240 MHz, 2.4 GHz 802.11 b/g/n Wi-Fi)
- **RFID Module:** MFRC522 13.56 MHz High-Frequency RFID Transceiver (SPI Interface)
- **Feedback Actuators (Active HIGH):**
  - Green LED (GPIO 25): Verified Voter / Vote Accepted (3 distinct blinks + 150ms tone)
  - Yellow LED (GPIO 26): Unregistered Card Presented (3 blinks + 3 alert chirps)
  - Red LED (GPIO 27): Duplicate Vote Blocked (3 alarm buzzes + rapid red strobe)
  - Active Piezo Buzzer (GPIO 32): Distinct audible alert frequencies

---

## 6. System Architecture

The Vote-Guard system follows a modular edge-to-cloud tiered architecture:

```mermaid
flowchart TD
    subgraph Edge["1. Physical Edge Layer (Polling Booth)"]
        Card["Citizen RFID Smart Card"] -->|13.56 MHz Radio Frequency| Reader["MFRC522 RFID Reader"]
        Reader -->|SPI Bus| MCU["ESP32 Microcontroller"]
        MCU -->|GPIO Output| Actuators["LED Indicators & Buzzer\n(Green / Yellow / Red)"]
    end

    subgraph Network["2. Network & Transport Layer"]
        MCU -->|Wi-Fi HTTP POST /api/vote/verify| API["FastAPI REST API Server\n(:8000)"]
        MCU -.->|Fallback: USB Serial 115200 baud| Bridge["Serial Bridge / Web Serial"]
        Bridge -.-> API
    end

    subgraph Application["3. Application & Security Layer"]
        API --> Auth["Auth & RBAC Router"]
        API --> Voting["Atomic Verification Router"]
        API --> Admin["Admin Operations Router"]
    end

    subgraph Data["4. Persistence Layer (MySQL 8.0)"]
        Voting -->|Row Write-Lock & Transaction| MySQL[("MySQL Relational Schema\n• voters (voter status & UID)\n• voter_credentials (local 2FA registry)\n• admin_users (RBAC accounts)\n• audit_logs (append-only log)")]
    end

    subgraph Presentation["5. Web Presentation Layer"]
        Auth["Authentication Gateway\n(index.html / login.html)"] <-->|REST API| API
        Operator["Operator Terminal\n(operator.html)"] <-->|Polling /api/vote/latest-event| API
        Dashboard["Admin Portal & 2FA Registration\n(admin.html)"] <-->|REST API| API
    end
```

---

## 7. Project Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Voter as Citizen Voter
    actor Operator as Booth Operator
    participant Hardware as ESP32 + RC522 Reader
    participant Server as FastAPI Backend Server
    participant DB as MySQL 8.0 Database

    Note over Voter,DB: Phase 1: Onboarding & Local Demographic Binding
    Operator->>Server: Register Citizen (Aadhaar + EPIC + RFID UID)
    Server->>DB: Check Uniqueness in voter_credentials & Commit Record
    DB-->>Server: Record Committed (has_voted = FALSE)

    Note over Voter,DB: Phase 2: Polling Day Verification & Voting
    Voter->>Hardware: Tap RFID Card on RC522 Reader
    Hardware->>Server: POST /api/vote/verify-and-record { rfid_uid: "XXXXXXXX" }
    
    Server->>DB: Atomic Update: UPDATE voters SET has_voted = TRUE WHERE rfid_uid = UID AND has_voted = FALSE
    
    alt Scenario A: First-Time Vote (Valid)
        DB-->>Server: Rows Affected = 1 (Commit Successful)
        Server->>DB: INSERT INTO audit_logs (status: "SUCCESS", event: "VOTE_ACCEPTED")
        Server-->>Hardware: JSON Response { status: "ACCEPTED", hardware_led: "GREEN" }
        Server-->>Operator: Live Update: "✅ Voter Verified Successfully"
        Hardware->>Hardware: Green LED 3x Blinks + 150ms Confirmation Tone
    else Scenario B: Duplicate Attempt (Fraud Prevented)
        DB-->>Server: Rows Affected = 0 (Condition has_voted = FALSE failed)
        Server->>DB: Query Voter Record -> Voter Found (Already Voted)
        Server->>DB: INSERT INTO audit_logs (status: "WARNING", event: "DUPLICATE_ATTEMPT")
        Server-->>Hardware: JSON Response { status: "ALREADY_VOTED", hardware_led: "RED" }
        Server-->>Operator: Live Alert: "🚨 Duplicate Voting Detected! Vote Blocked"
        Hardware->>Hardware: Red LED Rapid Strobe + 3x Alarm Buzzes
    else Scenario C: Unregistered Card Presented
        DB-->>Server: Voter Not Found in Database
        Server->>DB: INSERT INTO audit_logs (status: "DENIED", event: "UNREGISTERED_CARD")
        Server-->>Hardware: JSON Response { status: "UNREGISTERED", hardware_led: "YELLOW" }
        Server-->>Operator: Live Alert: "❌ Unregistered Card. Access Denied"
        Hardware->>Hardware: Yellow LED 3x Blinks + 3x Error Chirps
    end
```

---

## 8. Project Folder Structure

```text
VOTE-GUARD/
├── index.html                   # Sign In & Authentication Portal (Default landing page)
├── login.html                   # Dedicated Role-Based Login & Signup Gateway (Admin / Operator)
├── operator.html                # Polling Booth Operator Live Terminal (Live sync & event polling)
├── admin.html                   # Central Security Dashboard & 2FA Voter Registration (#voterRegistrationForm)
├── style.css                    # Unified responsive stylesheet
├── script.js                    # Registration client logic & Web Serial handler
├── auth.js                      # Client-side session tokens & route guards
├── operator.js                  # Polling synchronization & audio alerts
├── admin.js                     # Admin dashboard metrics & voter table CRUD
├── run_backend.py               # Root FastAPI launcher script
├── start_vote_guard.bat         # Windows one-click batch launcher
├── serial_bridge.py             # USB Serial-to-HTTP gateway bridge
├── .gitignore                   # Git exclusion rules for secrets, venv & cache
│
├── backend/                     # Python FastAPI Backend
│   ├── .env.example             # Environment configuration template (Copy to .env)
│   ├── requirements.txt         # Pip dependency manifest
│   ├── main.py                  # Direct backend launcher entry point
│   ├── init_db.py               # Database table initializer & seed utility
│   ├── inspect_db.py            # CLI database inspection script
│   ├── clean_dummy_data.py      # Test record cleanup script
│   ├── test_logic.py            # Unit tests for exactly-once voting logic
│   ├── test_lan_vote.py         # LAN network endpoint tests
│   └── app/                     # Core application package
│       ├── __init__.py
│       ├── main.py              # FastAPI app instance, CORS & static mounts
│       ├── database.py          # SQLAlchemy connection engine & session maker
│       ├── models.py            # ORM entities (AdminUser, VoterCredential, Voter, AuditLog)
│       ├── schemas.py           # Pydantic request/response validation schemas
│       ├── auth.py              # Password hashing & JWT validation functions
│       └── routers/             # Modular API controllers
│           ├── __init__.py
│           ├── auth.py          # User authentication endpoints
│           ├── voting.py        # Core voting verification & event polling
│           └── admin.py         # Administrative CRUD & audit logs
│
├── firmware/                    # Embedded Hardware Integration
│   └── vote_guard_esp32/
│       ├── vote_guard_esp32.ino # Arduino C++ firmware for ESP32 + RC522
│       └── config.example.h     # Safe hardware config template (Copy to config.h)
│
├── VOTE-GUARD-Documentation/    # Complete system design specifications & BOM guides
├── Final_Project_Report/        # Final university academic report & verification suite
└── paper/                       # IEEE-formatted academic research paper
```

---

## 9. Installation and Setup

### Prerequisites
- **Python:** Version 3.10 or higher (Python 3.14 compatible).
- **Database Server:** MySQL 8.0 or higher running locally or on your local network.
- **Git:** Installed on your development environment.
- **Arduino IDE (Optional):** Required only if compiling and flashing physical ESP32 hardware.

### Step 1: Clone the Repository
```bash
git clone https://github.com/AtikAnsari/Vote-Guard.git
cd Vote-Guard
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On macOS / Linux:
source .venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

## 10. Backend Configuration

The backend dynamically reads environment variables for its configuration. A safe template `backend/.env.example` is provided in the repository.

1. Navigate to the `backend/` folder and create your local `.env` file:
   ```bash
   # On Windows:
   copy backend\.env.example backend\.env
   # On Linux/macOS:
   cp backend/.env.example backend/.env
   ```

2. Open `backend/.env` in your text editor and update your database credentials:
   ```ini
   # Application Settings
   APP_NAME="VOTE-GUARD Verification API"
   APP_VERSION="1.0.0"
   APP_ENV="development"
   HOST="0.0.0.0"
   PORT=8000
   DEBUG=True

   # MySQL Database Settings (Set to your local MySQL server)
   DB_HOST="127.0.0.1"
   DB_PORT=3306
   DB_USER="root"
   DB_PASSWORD="your_local_mysql_password_here"
   DB_NAME="vote_guard"
   DB_ECHO=False

   # Security Secrets (Session & JWT Token Signing)
   SECRET_KEY="generate-a-secure-random-secret-key-here"
   JWT_SECRET_KEY="your_secure_random_secret_key_here"
   ```

> [!CAUTION]
> The `.env` file contains sensitive local credentials. It is permanently excluded from Git by `.gitignore`. Never commit or publish your `.env` file.

> [!IMPORTANT]
> **JWT Secret Key Security:** Ensure `JWT_SECRET_KEY` is explicitly set in your `.env` file with a strong random string (e.g. generated via `openssl rand -hex 32`). If omitted, the application falls back to an internal default key suitable only for offline local testing; in production, always configure a dedicated secret to prevent token forgery.

---

## 11. Database Configuration

### Step 1: Create the MySQL Database
Log into your MySQL command-line client or MySQL Workbench:
```sql
CREATE DATABASE vote_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 2: Initialize Tables & Seed Accounts
Run the automated initialization script from the project root:
```bash
python backend/init_db.py
```

What `init_db.py` does:
1. Connects to your configured MySQL server.
2. Creates the four relational tables (`admin_users`, `voter_credentials`, `voters`, `audit_logs`) safely with `IF NOT EXISTS`.
3. Seeds initial local development accounts for offline testing:
   - Default Administrator role (`admin`)
   - Default Polling Operator role (`operator`)

> [!IMPORTANT]
> Initial seed accounts are created for local development and demonstration only. For production or networked environments, update these credentials immediately or register new accounts via `login.html`.

### Step 3: Start the Backend Server
Launch the FastAPI server from the project root:
```bash
python run_backend.py
```
*(On Windows, you can also double-click `start_vote_guard.bat`)*

The server will initialize on `http://0.0.0.0:8000` (accessible via `http://localhost:8000` and over your local LAN).

---

## 12. ESP32 and RC522 Hardware Setup (Optional)

> **Note:** Physical hardware is **strictly optional** for reviewing, testing, or exploring Vote-Guard. The entire platform includes a software simulation workflow allowing complete demonstration through the web interface.

If you have physical hardware and want to deploy the embedded edge scanner:

### Component Pinout Mapping

| Component Pin | ESP32 DevKit V1 Pin | Electrical Notes / Safety |
| :--- | :--- | :--- |
| **RC522 3.3V** | **3V3** | **STRICTLY 3.3V.** Never connect to 5V or VIN (damages the RFID chip). |
| **RC522 GND** | **GND** | Common ground with ESP32. |
| **RC522 RST** | **GPIO 4** | Reset control line. |
| **RC522 MISO**| **GPIO 19**| Hardware SPI Master-In Slave-Out. |
| **RC522 MOSI**| **GPIO 23**| Hardware SPI Master-Out Slave-In. |
| **RC522 SCK** | **GPIO 18**| Hardware SPI Clock. |
| **RC522 SDA (SS)** | **GPIO 5** | Hardware SPI Slave Select / Chip Select. |
| **Green LED Anode**| **GPIO 25** | Through 220Ω current-limiting resistor to GND. |
| **Yellow LED Anode**| **GPIO 26**| Through 220Ω current-limiting resistor to GND. |
| **Red LED Anode** | **GPIO 27** | Through 220Ω current-limiting resistor to GND. |
| **Active Buzzer (+)** | **GPIO 32** | Signal pin (Cathode / Negative to GND). |

### Firmware Configuration & Flashing

1. Navigate to `firmware/vote_guard_esp32/`.
2. Copy `config.example.h` to `config.h`:
   ```bash
   cp firmware/vote_guard_esp32/config.example.h firmware/vote_guard_esp32/config.h
   ```
3. Open `config.h` and configure your local Wi-Fi credentials and laptop LAN IP:
   ```c
   #define WIFI_SSID       "YOUR_LOCAL_WIFI_SSID"
   #define WIFI_PASSWORD   "YOUR_LOCAL_WIFI_PASSWORD"
   #define BACKEND_BASE_URL "http://192.168.1.100:8000" // Your laptop's IPv4 address from 'ipconfig'
   ```
4. Open `vote_guard_esp32.ino` in the Arduino IDE.
5. In **Tools > Board**, select **ESP32 Dev Module**.
6. In **Tools > Manage Libraries**, install `MFRC522` by GithubCommunity.
7. Connect your ESP32 via USB and click **Upload**.

---

## 13. API Overview

The FastAPI backend provides structured, self-documenting RESTful endpoints accessible at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

| Method | Endpoint | Access | Description |
| :---: | :--- | :---: | :--- |
| `GET` | `/health` | Public | System health check and live MySQL database connectivity diagnostic. |
| `POST`| `/api/auth/login` | Public | Authenticates users (admin/operator) and returns a signed JWT token with role-based redirect URL. |
| `POST`| `/api/auth/signup` | Public | Registers a new administrative or booth operator user. |
| `GET` | `/api/auth/me` | Authenticated | Returns profile information for the active user session. |
| `POST`| `/api/vote/verify-and-record` | Edge / Operator | Core verification endpoint. Executes atomic conditional write and returns hardware LED feedback directives. |
| `GET` | `/api/vote/latest-event` | Operator | Polling endpoint returning the latest hardware RFID scan event. |
| `GET` | `/api/vote/history` | Operator | Returns the 10 most recent vote verification events for live terminal feed. |
| `GET` | `/api/vote/recorded-rfids` | Operator / Admin | Returns list of RFID UIDs that have already cast votes (used for frontend state synchronization). |
| `GET` | `/api/vote/public-stats` | Public | Returns voter turnout counts and fraud attempt totals. |
| `GET` | `/api/admin/stats` | Admin | Comprehensive analytics (total voters, votes cast, pending, duplicate attempts, available credentials). |
| `GET` | `/api/admin/voters` | Admin | Retrieves all registered voters with individual voting status. |
| `POST`| `/api/admin/voters` | Admin | Registers a voter with local 2FA Aadhaar + EPIC + RFID binding. |
| `GET` | `/api/admin/credentials` | Admin | Lists local pre-authorized citizen credential records. |
| `POST`| `/api/admin/credentials` | Admin | Pre-loads citizen credential records into the local mock registry. |
| `GET` | `/api/admin/audit-logs` | Admin | Retrieves persistent application-level audit log entries. |
| `POST`| `/api/admin/reset-votes` | Admin | Resets voting status to `FALSE` across voters for repeated test/demo cycles without deleting records. |

---

## 14. Demo Instructions

You can demonstrate the complete Vote-Guard verification lifecycle entirely through the web interface without any physical hardware.

> [!NOTE]
> **Simulated Credentials & Hardware-Free Evaluation:** All demo workflows utilize simulated or local data. The platform does not connect to real government databases, and physical hardware is not required to test the complete verification and duplicate-detection pipeline.

### Web Interface Access Points
With the server running on `http://localhost:8000`:
- **Portal Entry / Gateway:** `http://localhost:8000/` or `http://localhost:8000/login.html` (or `index.html`)
- **Booth Operator Terminal:** `http://localhost:8000/operator.html`
- **Admin Security Dashboard & 2FA Voter Registration:** `http://localhost:8000/admin.html`
- **Interactive API Docs:** `http://localhost:8000/docs`

### Step-by-Step Software Simulation Demo

1. **Log In:**
   - Open `http://localhost:8000/login.html` (or `index.html`).
   - Log in using your registered credentials or select your designated role (`admin` or `operator`) to enter the appropriate portal.

2. **Register a Test Voter (Local 2FA Credential Binding):**
   - Navigate to `http://localhost:8000/admin.html` (Admin Security Portal).
   - Locate the **Register New Voter (2FA Binding)** form (`#voterRegistrationForm`) and enter citizen details:
     - Citizen Full Name: `Jane Doe`
     - Aadhaar Number (12 digits): `1234 5678 9012`
     - Election Card / EPIC: `ABC1234567`
     - Physical RFID Tag UID: `A1B2C3D4` *(Enter any 8-character hex string for simulation or click "Tap to Capture")*
   - Click **Verify Credentials & Register RFID UID**. The credential uniqueness is validated against the local database schema and stored with `has_voted = False`.

3. **Simulate First-Time Vote (Valid Vote Accepted):**
   - Open `http://localhost:8000/operator.html` in another tab or window.
   - Use the **Interactive Test Scan** / Web input to trigger verification for UID `A1B2C3D4` *(or use the `/api/vote/verify-and-record` endpoint in Swagger docs)*.
   - **Observed Result:**
     - Status: `ACCEPTED` (Green badge).
     - Message: `✅ Voter Verified Successfully. Vote recorded.`
     - Audio: Single positive confirmation tone.
     - Database: `has_voted` transitions from `FALSE` to `TRUE`, timestamp is recorded.

4. **Simulate Second Vote Attempt (Duplicate Blocked):**
   - Submit the same UID `A1B2C3D4` a second time on the operator terminal.
   - **Observed Result:**
     - Status: `ALREADY_VOTED` (Red alert modal).
     - Message: `🚨 Duplicate Voting Detected! Vote blocked.`
     - Audio: Distinct rapid alert tone.
     - Database: Vote count remains unchanged; an audit log entry with `DUPLICATE_ATTEMPT` is recorded.

5. **Simulate Unregistered Card:**
   - Submit an unassigned UID such as `FFFFFFFF`.
   - **Observed Result:**
     - Status: `UNREGISTERED` (Yellow warning).
     - Message: `❌ Voter is not registered. Access denied.`

6. **Inspect the Audit Trail:**
   - Open `http://localhost:8000/admin.html`.
   - View live voter turnout statistics and inspect the **Audit Trail** table showing timestamps, client socket IPs, and event details.

---

## 15. Security & Architectural Scope

- **Credential Isolation:** Real database passwords, secret keys, and local Wi-Fi credentials are strictly isolated into `.env` and `config.h`, which are prevented from being pushed to version control via `.gitignore`.
- **Atomic Database Write-Locks:** Concurrency protection is achieved at the database engine level. Using a conditional update (`UPDATE voters SET has_voted = TRUE WHERE rfid_uid = :uid AND has_voted = FALSE`), MySQL InnoDB row-level write-locks ensure that only the first incoming request can modify the row, blocking concurrent multi-booth race conditions (TOCTOU).
- **Password Protection:** User passwords are encrypted using one-way PBKDF2-HMAC-SHA256 with 100,000 iterations and cryptographic salting (constant-time verification via `secrets.compare_digest`) before storage in the database.
- **Serial Gateway Protocol:** When operating over USB Serial, the ESP32 firmware transmits ASCII lines containing the scanned card UID string (`[RFID-SCAN] Scanned Card UID: <HEX_UID>`). The Python host bridge (`serial_bridge.py`) extracts this UID, queries `POST /api/vote/verify-and-record`, and writes back single-byte ASCII directives (`'V'` for valid/accepted, `'D'` for duplicate, `'U'` for unregistered) to actuate physical LED and buzzer feedback.
- **Append-Only Application Audit Trail:** Verification events are recorded in an insert-only audit log table at the application layer. While not a cryptographic or blockchain-enforced write-once ledger, the application exposes no modification or deletion endpoints for audit records.
- **Client Socket IP Capture:** The backend records `request.client.host` for forensic tracking, capturing the connecting network socket IP (such as the local LAN IP of the ESP32 or the operator's browser).
- **Simulated National ID Scope:** Aadhaar and EPIC numbers are validated against local database schema constraints as a proof-of-concept. The system does not connect to statutory government verification APIs.
- **Academic Prototype Scope:** Vote-Guard is an educational engineering prototype developed for academic evaluation. It is not certified for statutory or governmental public elections.

---

## 16. Current Project Status

| Feature / Subsystem | Implementation Status | Technical Verification Notes |
| :--- | :---: | :--- |
| **FastAPI REST Backend** | **Fully Implemented** | Modular routing, CORS, and health checks verified in `backend/app/main.py`. |
| **MySQL Relational Schema** | **Fully Implemented** | Normalized models for voters, credentials, users, and logs verified in `backend/app/models.py`. |
| **Exactly-Once Voting Invariant** | **Fully Implemented** | Atomic conditional update verified via `backend/test_logic.py`. |
| **2FA Demographic Binding** | **Implemented (Local Simulation)** | Relational uniqueness constraints enforced in MySQL; does not call external government APIs. |
| **Role-Based Auth (Admin/Operator)** | **Fully Implemented** | PBKDF2-HMAC-SHA256 password hashing and JWT token routing verified in `backend/app/routers/auth.py`. |
| **Live Operator Terminal** | **Fully Implemented** | Real-time polling sync, Web Audio cues, and alert modals active in `operator.js`. |
| **Admin Security Dashboard** | **Fully Implemented** | Statistics, Chart.js turnout charts, and audit trail pagination active in `admin.js`. |
| **ESP32 C++ Firmware** | **Fully Implemented** | Wi-Fi HTTP client, SPI RC522 driver, LED & buzzer routines verified in `vote_guard_esp32.ino`. |
| **Hardware Serial Bridge** | **Fully Implemented** | Standalone Python serial gateway (`serial_bridge.py`) and Web Serial API support ready. |
| **Automated Test Suites** | **Fully Implemented** | `test_logic.py`, `test_lan_vote.py`, `test_server_http.py` passing. |

---

## 17. Future Enhancements

The following features represent conceptual architectural enhancements planned for future research iterations:

- [ ] **Biometric Fingerprint Multi-Factor Authentication:** Adding an optical or capacitive fingerprint scanner (e.g., R307/FPM10A) to the ESP32 node for 3-factor physical verification.
- [ ] **Cryptographic Zero-Knowledge Ballot Receipts:** Implementing verifiable zero-knowledge proofs (zk-SNARKs) allowing citizens to verify their ballot was counted without compromising vote secrecy.
- [ ] **Decentralized Audit Ledger:** Integrating a lightweight distributed ledger (Hyperledger Fabric or private Ethereum) for consensus-driven cross-booth audit logging.
- [ ] **Full WebSocket Push Infrastructure:** Upgrading operator polling to bidirectional WebSockets for sub-millisecond edge event streaming.
- [ ] **Encrypted Offline Edge Storage:** Implementing AES-256 encrypted forward-secure flash buffers on the ESP32 to support temporary operation during network dropouts.

---

## 18. Contributors & Project Credits

This project was engineered and developed as a Problem Based Learning (PBL-I) project under the Department of Computer Science and Engineering, College of Technology, Silver Oak University:

### Student Engineering Team
- **Ansari Mo.Atik** — *Full-Stack Architecture, FastAPI Backend & ESP32 Firmware Development*
- **Shaikh Sakib Ahmed** — *Hardware Integration, RFID Circuitry & Embedded Actuation*
- **Shaikh Sejan** — *Database Architecture, 2FA KYC Schema & Audit Logging*

### Faculty Mentor & Project Advisory
- **Prof. Urmil Mewada** — *Project Guide, Department of Computer Engineering, College of Technology, Silver Oak University*

---

*For technical inquiries or academic review, refer to the detailed documentation located in `VOTE-GUARD-Documentation/` and the research paper in `paper/`.*
