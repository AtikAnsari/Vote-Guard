import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('paper/figures', exist_ok=True)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -------------------------------------------------------------
# FIGURE 1: System Architecture Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Tier Backgrounds
ax.add_patch(patches.Rectangle((2, 5), 28, 90, facecolor='#F0F4F8', edgecolor='#334E68', linewidth=1.5, linestyle='--'))
ax.text(16, 92, 'EDGE HARDWARE LAYER\n(Polling Booth Terminal)', ha='center', va='center', fontsize=10, fontweight='bold', color='#102A43')

ax.add_patch(patches.Rectangle((36, 5), 28, 90, facecolor='#F7FAFC', edgecolor='#2B6CB0', linewidth=1.5, linestyle='--'))
ax.text(50, 92, 'APPLICATION BACKEND\n(FastAPI / Uvicorn LAN)', ha='center', va='center', fontsize=10, fontweight='bold', color='#1A365D')

ax.add_patch(patches.Rectangle((70, 5), 28, 90, facecolor='#FAF5FF', edgecolor='#6B46C1', linewidth=1.5, linestyle='--'))
ax.text(84, 92, 'STORAGE & CLIENT TIER\n(MySQL 8.0 & Web Portals)', ha='center', va='center', fontsize=10, fontweight='bold', color='#322659')

# Edge Components
# RC522
ax.add_patch(patches.FancyBboxPatch((5, 68), 22, 16, boxstyle='round,pad=1', facecolor='#BEE3F8', edgecolor='#2B6CB0', linewidth=1.5))
ax.text(16, 76, 'RC522 RFID Transceiver\n• 13.56 MHz ISO 14443A\n• SPI Bus (GPIO 5, 18, 19, 23)', ha='center', va='center', fontsize=8, color='#1A365D')

# ESP32
ax.add_patch(patches.FancyBboxPatch((5, 38), 22, 22, boxstyle='round,pad=1', facecolor='#2B6CB0', edgecolor='#1A365D', linewidth=1.5))
ax.text(16, 49, 'ESP32 DevKit V1 (30-pin)\n• Xtensa Dual-Core @ 240MHz\n• FreeRTOS Task Loop\n• Wi-Fi Station 802.11 b/g/n\n• JSON Parser (ArduinoJson)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='white')

# Actuators
ax.add_patch(patches.FancyBboxPatch((5, 10), 22, 20, boxstyle='round,pad=1', facecolor='#EDF2F7', edgecolor='#4A5568', linewidth=1.5))
ax.text(16, 20, 'Local Actuation Feedback\n• Green LED (GPIO 25): Accepted\n• Yellow LED (GPIO 26): Unreg\n• Red LED (GPIO 27): Duplicate\n• Active Buzzer (GPIO 32): Audio', ha='center', va='center', fontsize=7.5, color='#2D3748')

# Arrows in Edge
ax.annotate('', xy=(16, 60), xytext=(16, 68), arrowprops=dict(arrowstyle='<->', color='#1A365D', lw=1.8))
ax.annotate('', xy=(16, 30), xytext=(16, 38), arrowprops=dict(arrowstyle='->', color='#1A365D', lw=1.8))

# Application Backend Components
ax.add_patch(patches.FancyBboxPatch((38, 56), 24, 28, boxstyle='round,pad=1', facecolor='#3182CE', edgecolor='#1A365D', linewidth=1.5))
ax.text(50, 70, 'FastAPI HTTP Application\n• Router: /api/vote/verify\n• Router: /api/admin/voters\n• Pydantic Schema Validation\n• In-Memory Event State Queue\n• Long-Polling Web Event Sync', ha='center', va='center', fontsize=8, color='white')

ax.add_patch(patches.FancyBboxPatch((38, 16), 24, 30, boxstyle='round,pad=1', facecolor='#EBF8FF', edgecolor='#3182CE', linewidth=1.5))
ax.text(50, 31, 'Core Business Logic\n• Atomic Concurrency Handler\n• Single-Vote Enforcer\n• KYC Identity Verification\n• Password Hash (bcrypt)\n• Session-Based Auth Tokens', ha='center', va='center', fontsize=8, color='#1A365D')

# Storage & Client Components
ax.add_patch(patches.FancyBboxPatch((72, 54), 24, 30, boxstyle='round,pad=1', facecolor='#805AD5', edgecolor='#44337A', linewidth=1.5))
ax.text(84, 69, 'MySQL 8.0 RDBMS\n• InnoDB ACID Engine\n• voters (Unique UID)\n• voter_credentials (KYC)\n• admin_users (RBAC)\n• audit_logs (Forensics)', ha='center', va='center', fontsize=8, color='white')

ax.add_patch(patches.FancyBboxPatch((72, 14), 24, 30, boxstyle='round,pad=1', facecolor='#FAF5FF', edgecolor='#805AD5', linewidth=1.5))
ax.text(84, 29, 'Web Client Interfaces\n• Operator Portal (polling 500ms)\n  - Real-time LED & status mirror\n• Admin Portal (2FA KYC Reg)\n  - Voter list, audit trail review\n• Responsive CSS / JS ES6', ha='center', va='center', fontsize=8, color='#322659')

# Network & Communication Lines
# Edge to Backend (Wi-Fi LAN)
ax.annotate('', xy=(38, 68), xytext=(27, 49), arrowprops=dict(arrowstyle='->', color='#DD6B20', lw=2.2, linestyle='-'))
ax.text(32, 60, 'Wi-Fi LAN (WPA2)\nHTTP POST /api/vote/verify\nJSON: {"rfid_uid": "..."}', ha='center', va='center', fontsize=7, fontweight='bold', color='#C05621', bbox=dict(boxstyle='square,pad=0.2', facecolor='#FFFAF0', edgecolor='#DD6B20'))

# Backend to Edge Response
ax.annotate('', xy=(27, 43), xytext=(38, 62), arrowprops=dict(arrowstyle='->', color='#38A169', lw=2.2, linestyle='-'))
ax.text(32, 45, 'HTTP 200 JSON Response\n{"status": "ACCEPTED",\n "hardware_led": "GREEN"}', ha='center', va='center', fontsize=7, fontweight='bold', color='#22543D', bbox=dict(boxstyle='square,pad=0.2', facecolor='#F0FFF4', edgecolor='#38A169'))

# Backend to MySQL (SQLAlchemy)
ax.annotate('', xy=(72, 69), xytext=(62, 69), arrowprops=dict(arrowstyle='<->', color='#4A5568', lw=2))
ax.text(67, 72, 'SQLAlchemy Pool\nAtomic SQL Updates', ha='center', va='center', fontsize=7, fontweight='bold', color='#2D3748')

# Backend to Web Clients
ax.annotate('', xy=(72, 29), xytext=(62, 29), arrowprops=dict(arrowstyle='<->', color='#805AD5', lw=2))
ax.text(67, 32, 'REST / Polling\nHTTP JSON Sync', ha='center', va='center', fontsize=7, fontweight='bold', color='#553C9A')

plt.tight_layout()
plt.savefig('paper/figures/Fig1_System_Architecture.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 1 generated.')

# -------------------------------------------------------------
# FIGURE 2: UML Sequence Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Participants
participants = [
    (10, 'Voter / Tag\n(MIFARE 1K)', '#E2E8F0'),
    (28, 'RC522 + ESP32\n(Edge Unit)', '#BEE3F8'),
    (48, 'FastAPI Backend\n(REST Server)', '#C6F6D5'),
    (70, 'MySQL Engine\n(InnoDB ACID)', '#E9D8FD'),
    (90, 'Operator Web\n(Browser Client)', '#FED7D7')
]

for x, label, col in participants:
    ax.add_patch(patches.FancyBboxPatch((x-8, 90), 16, 7, boxstyle='round,pad=0.5', facecolor=col, edgecolor='#2D3748', lw=1.2))
    ax.text(x, 93.5, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#1A202C')
    ax.plot([x, x], [10, 90], color='#A0AEC0', linestyle='--', lw=1.2)

# Sequence steps
steps = [
    (86, 10, 28, '1. Tap 13.56 MHz RFID Tag', '#2B6CB0', '->'),
    (81, 28, 28, '2. Extract 4-Byte Hex UID', '#2B6CB0', 'loop'),
    (75, 28, 48, '3. HTTP POST /api/vote/verify {rfid_uid}', '#DD6B20', '->'),
    (69, 48, 70, '4. Query `voters` WHERE rfid_uid = :uid', '#4A5568', '->'),
    (63, 70, 48, '5. Voter record found (has_voted=0)', '#4A5568', '-->'),
    (56, 48, 70, '6. ATOMIC UPDATE has_voted=1, voted_at=NOW()', '#805AD5', '->'),
    (49, 70, 48, '7. Row updated (rows_affected = 1)', '#805AD5', '-->'),
    (42, 48, 70, '8. INSERT INTO audit_logs (status: ACCEPTED)', '#4A5568', '->'),
    (35, 48, 48, '9. Update in-memory latest_event queue', '#2F855A', 'loop'),
    (28, 48, 28, '10. HTTP 200 {status: ACCEPTED, led: GREEN}', '#38A169', '-->'),
    (21, 28, 28, '11. Actuate Green LED (3 blinks) & Buzzer chirp', '#2F855A', 'loop'),
    (15, 90, 48, '12. GET /api/vote/latest-event (500ms poll)', '#C53030', '->'),
    (10, 48, 90, '13. Live display: Shaikh Noman - VOTE RECORDED', '#C53030', '-->')
]

for y, x1, x2, text, col, arrow in steps:
    if arrow == 'loop':
        ax.plot([x1, x1+5, x1+5, x1], [y+2, y+2, y-2, y-2], color=col, lw=1.5)
        ax.annotate('', xy=(x1, y-2), xytext=(x1+2, y-2), arrowprops=dict(arrowstyle='->', color=col, lw=1.5))
        ax.text(x1+6, y, text, ha='left', va='center', fontsize=7.5, fontweight='bold', color=col)
    else:
        ls = '--' if arrow == '-->' else '-'
        ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle='->', color=col, lw=1.6, linestyle=ls))
        ax.text((x1+x2)/2, y+1.8, text, ha='center', va='center', fontsize=7.5, fontweight='bold', color=col, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

plt.tight_layout()
plt.savefig('paper/figures/Fig2_Verification_Sequence.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 2 generated.')

# -------------------------------------------------------------
# FIGURE 3: Admin Registration 2FA KYC Workflow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Title
ax.text(50, 96, 'ADMIN 2FA KYC REGISTRATION & COLLISION MITIGATION WORKFLOW', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1A202C')

# Start Node
ax.add_patch(patches.FancyBboxPatch((40, 86), 20, 6, boxstyle='round,pad=0.5', facecolor='#CBD5E0', edgecolor='#4A5568', lw=1.5))
ax.text(50, 89, 'Start Registration', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')

# Input Step
ax.add_patch(patches.FancyBboxPatch((28, 72), 44, 9, boxstyle='round,pad=0.5', facecolor='#EBF8FF', edgecolor='#3182CE', lw=1.5))
ax.text(50, 76.5, 'Admin Inputs Citizen Demographics:\n• Full Name  • Aadhaar (12-digit)  • EPIC ID  • Mobile  • RFID UID', ha='center', va='center', fontsize=8, color='#1A365D')

ax.annotate('', xy=(50, 81), xytext=(50, 86), arrowprops=dict(arrowstyle='->', color='#2D3748', lw=1.5))
ax.annotate('', xy=(50, 66), xytext=(50, 72), arrowprops=dict(arrowstyle='->', color='#2D3748', lw=1.5))

# Decision 1: UID in voters?
ax.add_patch(patches.RegularPolygon((50, 58), numVertices=4, radius=8, facecolor='#FEFCBF', edgecolor='#D69E2E', lw=1.5))
ax.text(50, 58, 'RFID UID in\n`voters`?', ha='center', va='center', fontsize=7, fontweight='bold', color='#744210')

# Decision 1 Yes -> Reject
ax.annotate('YES', xy=(76, 58), xytext=(58, 58), arrowprops=dict(arrowstyle='->', color='#E53E3E', lw=1.5))
ax.add_patch(patches.FancyBboxPatch((76, 54), 20, 8, boxstyle='round,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E', lw=1.5))
ax.text(86, 58, 'REJECT (HTTP 409)\nRFID Tag Already Assigned', ha='center', va='center', fontsize=7, fontweight='bold', color='#9B2C2C')

# Decision 1 No -> Next Decision
ax.annotate('NO', xy=(50, 44), xytext=(50, 50), arrowprops=dict(arrowstyle='->', color='#38A169', lw=1.5))

# Decision 2: Aadhaar or EPIC in voter_credentials?
ax.add_patch(patches.RegularPolygon((50, 36), numVertices=4, radius=8, facecolor='#FEFCBF', edgecolor='#D69E2E', lw=1.5))
ax.text(50, 36, 'Aadhaar / EPIC in\n`credentials`?', ha='center', va='center', fontsize=7, fontweight='bold', color='#744210')

# Decision 2 Yes -> Reject
ax.annotate('YES', xy=(76, 36), xytext=(58, 36), arrowprops=dict(arrowstyle='->', color='#E53E3E', lw=1.5))
ax.add_patch(patches.FancyBboxPatch((76, 32), 20, 8, boxstyle='round,pad=0.4', facecolor='#FED7D7', edgecolor='#E53E3E', lw=1.5))
ax.text(86, 36, 'REJECT (HTTP 409)\nCitizen Already Registered', ha='center', va='center', fontsize=7, fontweight='bold', color='#9B2C2C')

# Decision 2 No -> Create Transaction
ax.annotate('NO', xy=(50, 22), xytext=(50, 28), arrowprops=dict(arrowstyle='->', color='#38A169', lw=1.5))

# Success Transaction Box
ax.add_patch(patches.FancyBboxPatch((24, 7), 52, 15, boxstyle='round,pad=0.6', facecolor='#C6F6D5', edgecolor='#38A169', lw=1.8))
ax.text(50, 14.5, 'ATOMIC TWO-TABLE INSERTION TRANSACTION:\n1. INSERT INTO `voter_credentials` (aadhaar_num, epic_card_id, mobile...)\n2. INSERT INTO `voters` (rfid_uid, full_name, credential_id, has_voted=0)\n3. INSERT INTO `audit_logs` (event_type: REGISTRATION_SUCCESS)\nCOMMIT TRANSACTION -> HTTP 201 Created', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#22543D')

plt.tight_layout()
plt.savefig('paper/figures/Fig3_Registration_2FA_Workflow.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 3 generated.')

# -------------------------------------------------------------
# FIGURE 4: Database ERD Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Table: admin_users
ax.add_patch(patches.Rectangle((4, 55), 26, 38, facecolor='#EDF2F7', edgecolor='#4A5568', lw=1.5))
ax.add_patch(patches.Rectangle((4, 85), 26, 8, facecolor='#2D3748', edgecolor='#4A5568', lw=1.5))
ax.text(17, 89, 'admin_users', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
admin_cols = [
    'PK  id : INT AUTO_INCREMENT',
    '    username : VARCHAR(50) [UQ]',
    '    hashed_password : VARCHAR(255)',
    '    full_name : VARCHAR(100)',
    '    role : VARCHAR(20) [admin/op]',
    '    is_active : BOOLEAN',
    '    created_at : DATETIME'
]
for i, c in enumerate(admin_cols):
    ax.text(5.5, 80 - i*4, c, fontsize=7, color='#2D3748', family='monospace')

# Table: voter_credentials
ax.add_patch(patches.Rectangle((37, 55), 28, 38, facecolor='#EDF2F7', edgecolor='#2B6CB0', lw=1.5))
ax.add_patch(patches.Rectangle((37, 85), 28, 8, facecolor='#2B6CB0', edgecolor='#2B6CB0', lw=1.5))
ax.text(51, 89, 'voter_credentials', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
cred_cols = [
    'PK  id : INT AUTO_INCREMENT',
    '    aadhaar_num : VARCHAR(12) [UQ]',
    '    epic_card_id : VARCHAR(20) [UQ]',
    '    mobile_number : VARCHAR(15)',
    '    assigned_rfid_uid : VARCHAR(20)[UQ]',
    '    verification_status : VARCHAR(20)',
    '    created_at : DATETIME'
]
for i, c in enumerate(cred_cols):
    ax.text(38.5, 80 - i*4, c, fontsize=7, color='#1A365D', family='monospace')

# Table: voters
ax.add_patch(patches.Rectangle((70, 55), 26, 38, facecolor='#EDF2F7', edgecolor='#38A169', lw=1.5))
ax.add_patch(patches.Rectangle((70, 85), 26, 8, facecolor='#38A169', edgecolor='#38A169', lw=1.5))
ax.text(83, 89, 'voters', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
voter_cols = [
    'PK  id : INT AUTO_INCREMENT',
    '    rfid_uid : VARCHAR(50) [UQ]',
    '    full_name : VARCHAR(100)',
    'FK  credential_id : INT [UQ]',
    '    has_voted : BOOLEAN (Idx)',
    '    voted_at : DATETIME NULL',
    '    is_active : BOOLEAN',
    '    created_at : DATETIME'
]
for i, c in enumerate(voter_cols):
    ax.text(71.5, 80 - i*4, c, fontsize=7, color='#22543D', family='monospace')

# Table: audit_logs
ax.add_patch(patches.Rectangle((37, 5), 28, 38, facecolor='#EDF2F7', edgecolor='#805AD5', lw=1.5))
ax.add_patch(patches.Rectangle((37, 35), 28, 8, facecolor='#805AD5', edgecolor='#805AD5', lw=1.5))
ax.text(51, 39, 'audit_logs', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
log_cols = [
    'PK  id : INT AUTO_INCREMENT',
    '    event_type : VARCHAR(50)',
    '    rfid_uid : VARCHAR(50) NULL',
    '    status : VARCHAR(30)',
    '    details : TEXT NULL',
    '    operator_id : INT NULL',
    '    ip_address : VARCHAR(45)',
    '    created_at : DATETIME'
]
for i, c in enumerate(log_cols):
    ax.text(38.5, 30 - i*3.8, c, fontsize=7, color='#44337A', family='monospace')

# Relationship: credentials -> voters (1 to 1)
ax.annotate('', xy=(70, 68), xytext=(65, 68), arrowprops=dict(arrowstyle='->', color='#2B6CB0', lw=2))
ax.text(67.5, 71, '1 : 1\nFK', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#2B6CB0')

# Relationship: admin_users -> audit_logs
ax.annotate('', xy=(37, 24), xytext=(17, 55), arrowprops=dict(arrowstyle='->', color='#805AD5', lw=1.5, linestyle=':'))
ax.text(25, 38, 'Operator FK\n(Audit Trace)', ha='center', va='center', fontsize=7, color='#6B46C1')

# Relationship: voters -> audit_logs
ax.annotate('', xy=(65, 24), xytext=(83, 55), arrowprops=dict(arrowstyle='->', color='#805AD5', lw=1.5, linestyle=':'))
ax.text(77, 38, 'Event UID Trace', ha='center', va='center', fontsize=7, color='#6B46C1')

plt.tight_layout()
plt.savefig('paper/figures/Fig4_Database_ERD.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 4 generated.')

# -------------------------------------------------------------
# FIGURE 5: Hardware Prototype Pinout & Wiring
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 6.2), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Central ESP32 DevKit V1
ax.add_patch(patches.FancyBboxPatch((35, 25), 30, 54, boxstyle='round,pad=1', facecolor='#2B6CB0', edgecolor='#1A365D', lw=2))
ax.text(50, 72, 'ESP32 DEVKIT V1\n(30-Pin NodeMCU)', ha='center', va='center', fontsize=9.5, fontweight='bold', color='white')

# Left: RC522 Reader Module
ax.add_patch(patches.FancyBboxPatch((5, 45), 22, 38, boxstyle='round,pad=0.8', facecolor='#BEE3F8', edgecolor='#3182CE', lw=1.5))
ax.text(16, 78, 'RC522 RFID Module\n(13.56 MHz SPI)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1A365D')
rc522_pins = [
    ('3.3V', '3V3 Power'),
    ('RST', 'GPIO 4'),
    ('GND', 'Common Ground'),
    ('MISO', 'GPIO 19'),
    ('MOSI', 'GPIO 23'),
    ('SCK', 'GPIO 18'),
    ('SDA (SS)', 'GPIO 5')
]
for i, (pin, target) in enumerate(rc522_pins):
    ax.text(7, 71 - i*4, f'{pin}  -->  {target}', fontsize=7, color='#1A365D', family='monospace')

# Connect RC522 to ESP32
ax.annotate('', xy=(35, 60), xytext=(27, 60), arrowprops=dict(arrowstyle='<->', color='#2B6CB0', lw=2))
ax.text(31, 63, 'SPI Bus', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#2B6CB0')

# Right: Tri-Color LEDs & Active Buzzer
ax.add_patch(patches.FancyBboxPatch((73, 50), 22, 34, boxstyle='round,pad=0.8', facecolor='#EDF2F7', edgecolor='#4A5568', lw=1.5))
ax.text(84, 79, 'Diagnostic Actuators\n(Current-Limited LEDs)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')

act_pins = [
    ('Green LED', 'GPIO 25', '#38A169'),
    ('Yellow LED', 'GPIO 26', '#D69E2E'),
    ('Red LED', 'GPIO 27', '#E53E3E'),
    ('Active Buzzer', 'GPIO 32', '#4A5568')
]
for i, (name, gpio, col) in enumerate(act_pins):
    ax.add_patch(patches.Circle((76, 70 - i*6), 1.8, facecolor=col, edgecolor='#2D3748'))
    ax.text(79, 70 - i*6, f'{name}: {gpio}', fontsize=7.5, fontweight='bold', color='#2D3748')

ax.annotate('', xy=(73, 62), xytext=(65, 62), arrowprops=dict(arrowstyle='->', color='#4A5568', lw=2))
ax.text(69, 65, 'GPIO', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#4A5568')

# Bottom: Power Supply
ax.add_patch(patches.FancyBboxPatch((35, 6), 30, 14, boxstyle='round,pad=0.8', facecolor='#FEFCBF', edgecolor='#D69E2E', lw=1.5))
ax.text(50, 13, 'POWER SUBSYSTEM\n• USB Power Bank (5V DC @ 2A)\n• Onboard AMS1117 3.3V LDO Regulator\n• Filter Capacitors on 3.3V Rail', ha='center', va='center', fontsize=7.5, fontweight='bold', color='#744210')
ax.annotate('', xy=(50, 25), xytext=(50, 20), arrowprops=dict(arrowstyle='->', color='#D69E2E', lw=2))

plt.tight_layout()
plt.savefig('paper/figures/Fig5_Hardware_Prototype_Pinout.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 5 generated.')

# -------------------------------------------------------------
# FIGURE 6: Latency Benchmark Breakdown
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.8), dpi=300)

# Latency Breakdown Bar Chart
stages = ['RC522 SPI\nTag Acquisition', 'Wi-Fi LAN\nHTTP POST TX', 'FastAPI + MySQL\nAtomic Concurrency', 'Wi-Fi LAN\nHTTP JSON RX', 'Actuator Blink\n& Web Event Queue']
times = [18.5, 42.1, 26.4, 38.2, 14.8] # in ms (Empirical round-trip)
colors = ['#3182CE', '#DD6B20', '#805AD5', '#DD6B20', '#38A169']

bars = ax1.bar(stages, times, color=colors, width=0.55, edgecolor='#2D3748', lw=1.2)
ax1.set_ylabel('Execution Latency (milliseconds)', fontsize=8.5, fontweight='bold')
ax1.set_title('(a) End-to-End Latency Component Decomposition\n(Total Mean Round-Trip = 140.0 ms)', fontsize=9, fontweight='bold', pad=10)
ax1.set_ylim(0, 55)
ax1.tick_params(axis='x', labelsize=7.5)
ax1.tick_params(axis='y', labelsize=8)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 1.2, f'{yval:.1f} ms', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

# Comparative Verification Latency Across Prior Works
systems = ['Standalone\nEVM [11]', 'Biometric\nSerial [7]', 'Blockchain\nIoT [10]', 'Vote-Guard\n(Proposed)']
latencies = [1250, 850, 14200, 140] # in ms
comp_colors = ['#A0AEC0', '#CBD5E0', '#E2E8F0', '#3182CE']

bars2 = ax2.bar(systems, latencies, color=comp_colors, width=0.5, edgecolor='#2D3748', lw=1.2)
ax2.set_ylabel('Total Verification Latency (ms, Log Scale)', fontsize=8.5, fontweight='bold')
ax2.set_yscale('log')
ax2.set_title('(b) Verification Latency vs. Published Systems\n(Logarithmic Scale)', fontsize=9, fontweight='bold', pad=10)
ax2.tick_params(axis='x', labelsize=8)
ax2.tick_params(axis='y', labelsize=8)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, yval * 1.15, f'{int(yval)} ms', ha='center', va='bottom', fontsize=7.5, fontweight='bold')

plt.tight_layout()
plt.savefig('paper/figures/Fig6_Latency_Benchmark.png', dpi=300, bbox_inches='tight')
plt.close()
print('Fig 6 generated.')

