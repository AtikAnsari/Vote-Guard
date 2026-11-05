/**
 * VOTE-GUARD — Operator Terminal Controller
 * Directly connects to the physical ESP32 + RC522 RFID Receiver
 * Supports both Web Serial (USB Cable) and Wi-Fi HTTP direct polling.
 */

const API_BASE = (window.location.hostname && (window.location.port === "8000")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";

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

let lastEventId = 0;
let resetTimer = null;
let serialPort = null;
let serialWriter = null;
let isSerialReading = false;


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
                        verifyCardFromHardware(extractedUid);
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

connectSerialBtn.addEventListener("click", connectSerialPort);


// ================= CARD VERIFICATION EXECUTION =================

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


// ================= LIVE WIRELESS / WI-FI RECEIVER LISTENER =================

let isInitialPoll = true;

async function pollReceiverEvents() {
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
