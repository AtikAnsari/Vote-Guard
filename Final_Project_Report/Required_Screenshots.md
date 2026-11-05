# Required & Included Screenshots Checklist

This document tracks all frontend and system screenshots used in the Vote-Guard B.Tech Final Project Report.

---

## 1. Verified & Embedded Screenshots

The following screenshots were provided and integrated into **Chapter 4 (Implementation)**, **Chapter 5 (Testing & Results)**, and **Annexure G**:

| Figure No. | Image File | Description / Functionality | Chapter / Section | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Figure 4.5** | `01_login_security_portal.jpg` | **Vote-Guard Security Portal (Login & Access Gate):** Shows role selection (System Administrator vs. Polling Operator), pre-configured test credentials autofill, and secure session authentication. | Section 4.7 / Annexure G | **EMBEDDED** |
| **Figure 4.6** | `02_operator_terminal.png` | **Polling Booth Operator Terminal:** Shows live hardware receiver synchronization, active Wi-Fi connection indicator, idle status ("Ready for Voter RFID Card"), and tri-color LED / buzzer status indicators. | Section 4.7 / Annexure G | **EMBEDDED** |
| **Figure 4.7** | `03_admin_kyc_security.png` | **Admin Security & 2FA KYC Credential Registry:** Shows centralized voter management, real-time statistics cards (Total Voters, Votes Recorded, Pending, Fraud Attempts Blocked = 23), and 2FA credential binding interface. | Section 4.7 / Annexure G | **EMBEDDED** |
| **Figure 4.8** | `04_registration_form.png` | **Voter 2FA Credential Registration Form:** Shows physical RFID UID capture, citizen demographic input (Full Name, 12-digit Aadhaar, EPIC Card ID, Mobile Number), and collision detection feedback. | Section 4.5 / Annexure G | **EMBEDDED** |

---

## 2. Optional Supplementary Screenshots (For Viva / Demo)

If desired, the following optional runtime captures can be taken from your browser during a live demonstration and inserted into the editable `.docx` file:

1. **Accepted Vote Screen:** Operator Terminal displaying the emerald card: `"Shaikh Noman - VOTE RECORDED"`.
2. **Duplicate Vote Alert Screen:** Operator Terminal displaying the crimson alert: `"🚨 DUPLICATE VOTE BLOCKED - Voter has already cast ballot"`.
3. **Unregistered Card Screen:** Operator Terminal displaying the amber warning banner: `"❌ VOTER ID NOT REGISTERED"`.
4. **MySQL Workbench / phpMyAdmin Evidence:** Table view of `voters` showing `has_voted = 1` and `voted_at` timestamp.

