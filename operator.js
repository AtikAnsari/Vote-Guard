/**
 * VOTE-GUARD — Operator Terminal Controller
 * Directly connects to the physical ESP32 + RC522 RFID Receiver
 * Supports both Web Serial (USB Cable) and Wi-Fi HTTP direct polling.
 */

const API_BASE = (window.location.hostname && (window.location.port === "8000")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";

// Centralized Demo Mode Detection
const IS_DEMO = window.VoteGuardMock ? window.VoteGuardMock.isDemoMode() : false;

// Auth verification
const token = sessionStorage.getItem("voteGuardToken");
const userStr = sessionStorage.getItem("voteGuardUser");

if (!token || !userStr) {
    window.location.href = "login.html";
}

const user = JSON.parse(userStr || "{}");
document.getElementById("operatorNameDisplay").textContent = user.full_name || user.username || "Operator";

// DOM Elements
const logoutBtn = document.getElementById("logoutBtn");
const connectSerialBtn = document.getElementById("connectSerialBtn");
const receiverStatusDot = document.getElementById("receiverStatusDot");
const receiverStatusText = document.getElementById("receiverStatusText");

const operatorResultCard = document.getElementById("operatorResultCard");
const stateIcon = document.getElementById("stateIcon");
const stateTitle = document.getElementById("stateTitle");
const stateDesc = document.getElementById("stateDesc");

const ledGreen = document.getElementById("ledGreen");
const ledYellow = document.getElementById("ledYellow");
const ledRed = document.getElementById("ledRed");
const buzzerIndicator = document.getElementById("buzzerIndicator");
const themeSelect = document.getElementById("themeSelect");

// Demo Simulator DOM Elements
const demoOperatorBanner = document.getElementById("demoOperatorBanner");
const demoSimulatorCard = document.getElementById("demoSimulatorCard");
const simValidCardBtn = document.getElementById("simValidCardBtn");
const simDuplicateCardBtn = document.getElementById("simDuplicateCardBtn");
const simUnregisteredCardBtn = document.getElementById("simUnregisteredCardBtn");
const simCustomUid = document.getElementById("simCustomUid");
const simCustomUidBtn = document.getElementById("simCustomUidBtn");
const resetDemoVotesBtn = document.getElementById("resetDemoVotesBtn");

let lastEventId = 0;
let resetTimer = null;
let serialPort = null;
let serialWriter = null;
let isSerialReading = false;

// Activate Demo Mode UI if running in Demo Mode
if (IS_DEMO) {
    if (demoOperatorBanner) demoOperatorBanner.style.display = "block";
    if (demoSimulatorCard) demoSimulatorCard.style.display = "block";
    receiverStatusDot.className = "status-dot status-dot-connected";
    receiverStatusText.textContent = "Demo Simulator Online";
    receiverStatusText.style.color = "#16a34a";
}


// ================= LOGOUT =================

logoutBtn.addEventListener("click", () => {
    sessionStorage.clear();
    window.location.href = "login.html";
});


// ================= OPERATOR DISPLAY CONTROLLER =================

function setOperatorDisplay(status, ledColor, data = {}) {
    clearTimeout(resetTimer);

    // Reset card classes
    operatorResultCard.classList.remove("state-idle", "state-green", "state-yellow", "state-red");

    // Reset hardware lamps
    ledGreen.classList.remove("active");
    ledYellow.classList.remove("active");
    ledRed.classList.remove("active");
    buzzerIndicator.classList.remove("beep");

    // 1. GREEN — VOTE IS DONE
    if (ledColor === "GREEN" || status === "ACCEPTED") {
        operatorResultCard.classList.add("state-green");
        stateIcon.textContent = "✅";
        stateTitle.textContent = "VOTE IS DONE & RECORDED";
        stateDesc.textContent = data.voter_name 
            ? `Citizen: ${data.voter_name} (Voter ID: ${data.voter_code}) — Vote Successfully Registered!`
            : "Vote has been accepted and recorded.";

        ledGreen.classList.add("active");
        buzzerIndicator.textContent = "🔊 1 SHORT BEEP (200ms) — VOTE DONE";
        buzzerIndicator.classList.add("beep");

        // Send 'V' to physical ESP32 over serial
        sendSerialCommand("V");
    }
    // 2. YELLOW — VOTER ID IS NOT REGISTERED
    else if (ledColor === "YELLOW" || status === "UNREGISTERED") {
        operatorResultCard.classList.add("state-yellow");
        stateIcon.textContent = "⚠️";
        stateTitle.textContent = "VOTER ID IS NOT REGISTERED";
        stateDesc.textContent = data.rfid_uid
            ? `Access Denied: RFID Tag UID '${data.rfid_uid}' is not registered in the electoral roll.`
            : "Access Denied: RFID tag is not registered in the electoral roll.";

        ledYellow.classList.add("active");
        buzzerIndicator.textContent = "⚠️ 3 RAPID WARNING CHIRPS — UNREGISTERED";
        buzzerIndicator.classList.add("beep");

        // Send 'U' to physical ESP32 over serial
        sendSerialCommand("U");
    }
    // 3. RED — DUPLICATE VOTE ATTEMPT BLOCKED
    else if (ledColor === "RED" || status === "ALREADY_VOTED") {
        operatorResultCard.classList.add("state-red");
        stateIcon.textContent = "🚨";
        stateTitle.textContent = "DUPLICATE VOTE ATTEMPT BLOCKED";
        stateDesc.textContent = data.voter_name
            ? `ALREADY VOTED! Citizen ${data.voter_name} has already cast their vote. Multiple voting is strictly prohibited.`
            : "Duplicate Voting Detected! Voter has already voted.";

        ledRed.classList.add("active");
        buzzerIndicator.textContent = "🚨 2 LONG WARNING BEEPS — DUPLICATE BLOCKED";
        buzzerIndicator.classList.add("beep");

        // Send 'D' to physical ESP32 over serial
        sendSerialCommand("D");
    }

    // Auto-return to standby after 4.5 seconds for next card scan
    resetTimer = setTimeout(() => {
        resetOperatorDisplay();
    }, 4500);
}

function resetOperatorDisplay() {
    operatorResultCard.classList.remove("state-green", "state-yellow", "state-red");
    operatorResultCard.classList.add("state-idle");
    stateIcon.textContent = "📡";
    stateTitle.textContent = "Ready for Voter RFID Card";
    stateDesc.textContent = "Waiting for physical RFID scan from DevKit V1 receiver... Tap voter card on scanner.";

    ledGreen.classList.remove("active");
    ledYellow.classList.remove("active");
    ledRed.classList.remove("active");
    buzzerIndicator.classList.remove("beep");
    buzzerIndicator.textContent = "🔊 BUZZER IDLE";
}


// ================= WEB SERIAL (USB COM PORT) INTEGRATION =================

async function connectSerialPort() {
    if (!("serial" in navigator)) {
        alert("Web Serial API is not supported in this browser. Please use Chrome, Edge, or Opera to connect directly to the ESP32 USB cable, or use Wi-Fi HTTP mode.");
        return;
    }

    try {
        serialPort = await navigator.serial.requestPort();
        await serialPort.open({ baudRate: 115200 });

        connectSerialBtn.textContent = "🔌 ESP32 Connected (COM Port)";
        connectSerialBtn.style.background = "#16a34a";
        receiverStatusDot.className = "status-dot status-dot-connected";
        receiverStatusText.textContent = "USB Serial Online (115200)";
        receiverStatusText.style.color = "#16a34a";

        // Setup writer
        const textEncoder = new TextEncoderStream();
        const writableStreamClosed = textEncoder.readable.pipeTo(serialPort.writable);
        serialWriter = textEncoder.writable.getWriter();

        // Start reading loop
        readSerialLoop();

    } catch (err) {
        console.warn("Serial connection aborted or failed:", err.message);
    }
}

let lastHardwareScannedUid = "";
let lastHardwareScanTime = 0;

async function readSerialLoop() {
    isSerialReading = true;
    const textDecoder = new TextDecoderStream();
    const readableStreamClosed = serialPort.readable.pipeTo(textDecoder.writable);
    const reader = textDecoder.readable.getReader();

    let buffer = "";

    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            if (value) {
                buffer += value;
                const lines = buffer.split("\n");
                buffer = lines.pop(); // keep last incomplete chunk

                for (let line of lines) {
                    line = line.trim();
                    if (!line) continue;

                    // Filter out diagnostic, parser, HTTP trace, and JSON echo lines from ESP32 serial stream
                    if (
                        line.startsWith("[HTTP-") ||
                        line.startsWith("[PARSER") ||
                        line.startsWith("[ACTUATOR") ||
                        line.startsWith("[SELF-TEST") ||
                        line.startsWith("[WIFI") ||
                        line.startsWith("==") ||
                        line.startsWith("--") ||
                        line.includes("Payload") ||
                        line.includes("Raw Response") ||
                        line.includes("{") ||
                        line.includes("}")
                    ) {
                        continue;
                    }

                    let extractedUid = null;

                    // Format 1: "[RFID-SCAN] Scanned Card UID: 71411605"
                    if (/scanned\s*card\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i.test(line)) {
                        const m = line.match(/scanned\s*card\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i);
                        if (m && m[1]) {
                            extractedUid = m[1].replace(/[\s:-]/g, "").toUpperCase();
                        }
                    } 
                    // Format 2: "Card UID: 8A 4F 12 3B"
                    else if (/^\s*card\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i.test(line)) {
                        const m = line.match(/^\s*card\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i);
                        if (m && m[1]) {
                            extractedUid = m[1].replace(/[\s:-]/g, "").toUpperCase();
                        }
                    } 
                    // Format 3: "UID: 8A4F123B"
                    else if (/^\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i.test(line)) {
                        const m = line.match(/^\s*uid\s*:\s*([0-9a-fA-F\s:-]+)/i);
                        if (m && m[1]) {
                            extractedUid = m[1].replace(/[\s:-]/g, "").toUpperCase();
                        }
                    } 
                    // Format 4: Raw hex string like "71411605"
                    else {
                        const clean = line.replace(/[\s:-]/g, "");
                        if (/^[0-9A-Fa-f]{8,14}$/.test(clean)) {
                            extractedUid = clean.toUpperCase();
                        }
                    }

                    if (extractedUid) {
                        const nowMs = Date.now();
                        // Debounce identical scans within 3.5 seconds
                        if (extractedUid === lastHardwareScannedUid && (nowMs - lastHardwareScanTime < 3500)) {
                            console.log(`[DEBOUNCE] Ignoring duplicate serial bounce for UID ${extractedUid}`);
                            continue;
                        }
                        lastHardwareScannedUid = extractedUid;
                        lastHardwareScanTime = nowMs;

                        console.log("Hardware Scanned RFID UID:", extractedUid);
                        executeCardVerification(extractedUid);
                    }
                }
            }
        }
    } catch (err) {
        console.error("Serial reading error:", err);
    } finally {
        reader.releaseLock();
    }
}

async function sendSerialCommand(cmdChar) {
    if (serialWriter) {
        try {
            await serialWriter.write(cmdChar + "\n");
            console.log(`[SERIAL] Transmitted command '${cmdChar}' to ESP32`);
        } catch (err) {
            console.warn("Error sending serial command:", err);
        }
    }
}

connectSerialBtn.addEventListener("click", () => {
    if (IS_DEMO) {
        alert("In Public Demo Mode, ESP32 DevKit V1 and RC522 RFID reader are simulated in-browser. Use the RFID Hardware Simulator buttons below!");
        return;
    }
    connectSerialPort();
});


// ================= CARD VERIFICATION EXECUTION =================

function executeCardVerification(rfid_uid) {
    const cleanUid = (rfid_uid || "").trim().toUpperCase();
    if (!cleanUid) return;

    // Public Demo Mode interceptor: use client-side mock engine
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const data = window.VoteGuardMock.verifyAndRecord(cleanUid);
            if (data.event_id) {
                lastEventId = Math.max(lastEventId, data.event_id);
            }
            setOperatorDisplay(data.status, data.hardware_led, data);
            window.VoteGuardMock.playBuzzerSound(data.hardware_led);
        } catch (err) {
            setOperatorDisplay("ERROR", "YELLOW", { rfid_uid: cleanUid });
        }
        return;
    }

    // Full-Stack Mode: Post to live FastAPI endpoint
    verifyCardFromHardware(cleanUid);
}

async function verifyCardFromHardware(rfid_uid) {
    try {
        const res = await fetch(`${API_BASE}/api/vote/verify-and-record`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rfid_uid: rfid_uid })
        });

        const data = await res.json();
        if (data.event_id) {
            lastEventId = Math.max(lastEventId, data.event_id);
        }
        setOperatorDisplay(data.status, data.hardware_led, data);
    } catch (err) {
        setOperatorDisplay("ERROR", "YELLOW", { rfid_uid: rfid_uid });
    }
}


// ================= WIRE DEMO HARDWARE SIMULATOR =================

if (IS_DEMO) {
    if (simValidCardBtn) {
        simValidCardBtn.addEventListener("click", () => executeCardVerification("71411605"));
    }
    if (simDuplicateCardBtn) {
        simDuplicateCardBtn.addEventListener("click", () => executeCardVerification("B2C3D4E5"));
    }
    if (simUnregisteredCardBtn) {
        simUnregisteredCardBtn.addEventListener("click", () => executeCardVerification("99AABBCC"));
    }
    if (simCustomUidBtn && simCustomUid) {
        simCustomUidBtn.addEventListener("click", () => {
            const val = simCustomUid.value.trim().toUpperCase();
            if (!val) {
                alert("Please enter a custom RFID UID to test.");
                return;
            }
            executeCardVerification(val);
        });
        simCustomUid.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                simCustomUidBtn.click();
            }
        });
    }
    if (resetDemoVotesBtn) {
        resetDemoVotesBtn.addEventListener("click", () => {
            if (window.VoteGuardMock) {
                window.VoteGuardMock.resetVotes();
                resetOperatorDisplay();
                alert("Demo voting flags have been reset to 'Not Voted'. You can now test voting again with Aman Patel or Rajesh Kumar!");
            }
        });
    }
}


// ================= LIVE WIRELESS / WI-FI RECEIVER LISTENER =================

let isInitialPoll = true;

async function pollReceiverEvents() {
    // In Public Demo Mode, check local mock engine state without HTTP requests
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const data = window.VoteGuardMock.getLatestEvent();
            if (data && data.event_id > lastEventId) {
                lastEventId = data.event_id;
                setOperatorDisplay(data.status, data.hardware_led, data);
                window.VoteGuardMock.playBuzzerSound(data.hardware_led);
            }
        } catch (e) {}
        return;
    }

    // Full-Stack Mode: Poll FastAPI backend for physical ESP32 Wi-Fi scans
    try {
        const response = await fetch(`${API_BASE}/api/vote/latest-event`);
        if (response.ok) {
            const data = await response.json();
            if (!serialPort) {
                receiverStatusDot.className = "status-dot status-dot-connected";
                receiverStatusText.textContent = "Wi-Fi Hardware Active";
                receiverStatusText.style.color = "#16a34a";
            }

            // Sync initial state without replay of stale past events
            if (isInitialPoll) {
                isInitialPoll = false;
                lastEventId = data.event_id || 0;
                const eventAgeMs = data.timestamp ? (Date.now() - new Date(data.timestamp).getTime()) : Infinity;
                if (data.event_id > 0 && eventAgeMs < 4000) {
                    setOperatorDisplay(data.status, data.hardware_led, data);
                }
                return;
            }

            // If a new RFID scan occurred from hardware receiver (via Wi-Fi or backend)
            if (data.event_id > lastEventId) {
                lastEventId = data.event_id;
                setOperatorDisplay(data.status, data.hardware_led, data);
            }
        }
    } catch (err) {
        if (!serialPort) {
            receiverStatusText.textContent = "Backend Offline";
            receiverStatusText.style.color = "#dc2626";
        }
    }
}

// Poll receiver every 500ms
setInterval(pollReceiverEvents, 500);


// ================= THEME CONTROLLER =================

const THEME_STORAGE_KEY = "voteGuardTheme";
const systemThemeQuery = window.matchMedia("(prefers-color-scheme: dark)");

function getSavedTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY) || "light";
}

function applyTheme(theme, persist = true) {
    const selectedTheme = (theme === "dark" || theme === "system" || theme === "light") ? theme : "light";
    if (persist) localStorage.setItem(THEME_STORAGE_KEY, selectedTheme);
    if (themeSelect && themeSelect.value !== selectedTheme) themeSelect.value = selectedTheme;

    let isDark = false;
    if (selectedTheme === "dark") isDark = true;
    else if (selectedTheme === "system") isDark = systemThemeQuery.matches;

    if (isDark) {
        document.documentElement.setAttribute("data-theme", "dark");
        document.body.classList.add("dark-theme");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
        document.body.classList.remove("dark-theme");
    }
}

if (themeSelect) {
    themeSelect.addEventListener("change", function () {
        applyTheme(this.value, true);
    });
}

applyTheme(getSavedTheme(), false);
