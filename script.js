/**
 * VOTE-GUARD — Voting Security & Verification System
 * Single-Focus Operator Mode + Synchronized Green/Yellow/Red LED Directives
 */

// ================= CONFIGURATION & API BASE =================

const API_BASE = (window.location.hostname && (window.location.port === "8000")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";

// Persistent state
let currentAuthToken = sessionStorage.getItem("voteGuardAdminToken") || null;
let currentAdminProfile = JSON.parse(sessionStorage.getItem("voteGuardAdminUser") || "null");
let cachedCredentials = [];
let operatorResetTimer = null;


// ================= DOM ELEMENTS =================

// Auth & Nav
const currentRoleBadge = document.getElementById("currentRoleBadge");
const adminNameDisplay = document.getElementById("adminNameDisplay");
const adminLoginBtn = document.getElementById("adminLoginBtn");
const adminLogoutBtn = document.getElementById("adminLogoutBtn");
const tabVotingStation = document.getElementById("tabVotingStation");
const tabAdminPortal = document.getElementById("tabAdminPortal");
const votingStationView = document.getElementById("votingStationView");
const adminPortalView = document.getElementById("adminPortalView");
const pageHeadingTitle = document.getElementById("pageHeadingTitle");
const pageHeadingDesc = document.getElementById("pageHeadingDesc");
const systemStatusText = document.getElementById("systemStatusText");

// Operator Terminal Single-Focus Elements
const voterInput = document.getElementById("voterInput");
const verifyBtn = document.getElementById("verifyBtn");
const operatorResultCard = document.getElementById("operatorResultCard");
const stateIcon = document.getElementById("stateIcon");
const stateTitle = document.getElementById("stateTitle");
const stateDesc = document.getElementById("stateDesc");

// Synchronized LED & Buzzer elements
const ledGreen = document.getElementById("ledGreen");
const ledYellow = document.getElementById("ledYellow");
const ledRed = document.getElementById("ledRed");
const buzzerIndicator = document.getElementById("buzzerIndicator");

// Admin Portal elements
const totalVoters = document.getElementById("totalVoters");
const votesRecorded = document.getElementById("votesRecorded");
const pendingVotes = document.getElementById("pendingVotes");
const fraudAttempts = document.getElementById("fraudAttempts");
const recordedVotersTable = document.getElementById("recordedVotersTable");
const recordedCount = document.getElementById("recordedCount");
const quickCredSelect = document.getElementById("quickCredSelect");
const voterRegistrationForm = document.getElementById("voterRegistrationForm");
const regRfidUid = document.getElementById("regRfidUid");
const regVoterName = document.getElementById("regVoterName");
const regAadhar = document.getElementById("regAadhar");
const regEpic = document.getElementById("regEpic");
const regPhone = document.getElementById("regPhone");
const submitRegBtn = document.getElementById("submitRegBtn");
const regAlertBox = document.getElementById("regAlertBox");
const credAvailableCount = document.getElementById("credAvailableCount");
const credentialsTableBody = document.getElementById("credentialsTableBody");
const votersTableBody = document.getElementById("votersTableBody");
const refreshVotersBtn = document.getElementById("refreshVotersBtn");
const auditTableBody = document.getElementById("auditTableBody");
const refreshAuditBtn = document.getElementById("refreshAuditBtn");
const resetVotesBtn = document.getElementById("resetVotesBtn");

// Login Modal
const loginModal = document.getElementById("loginModal");
const closeLoginModal = document.getElementById("closeLoginModal");
const adminLoginForm = document.getElementById("adminLoginForm");
const loginUsername = document.getElementById("loginUsername");
const loginPassword = document.getElementById("loginPassword");
const loginError = document.getElementById("loginError");
const themeSelect = document.getElementById("themeSelect");


// ================= AUTHENTICATION & RBAC =================

function updateAuthUI() {
    if (currentAuthToken && currentAdminProfile) {
        // ADMIN MODE
        currentRoleBadge.className = "role-badge role-badge-admin";
        currentRoleBadge.innerHTML = "🛡️ Role: Administrator";
        adminNameDisplay.textContent = currentAdminProfile.full_name || currentAdminProfile.username;
        adminNameDisplay.style.display = "inline";

        adminLoginBtn.style.display = "none";
        adminLogoutBtn.style.display = "inline-block";
        tabAdminPortal.style.display = "flex";
    } else {
        // OPERATOR MODE
        currentRoleBadge.className = "role-badge role-badge-kiosk";
        currentRoleBadge.innerHTML = "🖥️ Operator Mode";
        adminNameDisplay.style.display = "none";

        adminLoginBtn.style.display = "inline-block";
        adminLogoutBtn.style.display = "none";
        tabAdminPortal.style.display = "none";

        // Return to operator view if currently on admin tab
        switchTab("votingStation");
    }
}

async function loginAdmin(username, password) {
    loginError.style.display = "none";
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed.");
        }

        currentAuthToken = data.access_token;
        currentAdminProfile = {
            username: data.username,
            full_name: data.full_name,
            role: data.role
        };

        sessionStorage.setItem("voteGuardAdminToken", currentAuthToken);
        sessionStorage.setItem("voteGuardAdminUser", JSON.stringify(currentAdminProfile));

        loginModal.classList.remove("open");
        adminLoginForm.reset();
        updateAuthUI();
        switchTab("adminPortal");
        loadAdminData();
    } catch (err) {
        loginError.textContent = err.message;
        loginError.style.display = "block";
    }
}

function logoutAdmin() {
    currentAuthToken = null;
    currentAdminProfile = null;
    sessionStorage.removeItem("voteGuardAdminToken");
    sessionStorage.removeItem("voteGuardAdminUser");
    updateAuthUI();
    switchTab("votingStation");
}


// ================= TAB NAVIGATION =================

function switchTab(tab) {
    if (tab === "adminPortal" && currentAuthToken) {
        tabVotingStation.classList.remove("active");
        tabAdminPortal.classList.add("active");
        votingStationView.style.display = "none";
        adminPortalView.style.display = "block";
        pageHeadingTitle.textContent = "Admin Security & 2FA Console";
        pageHeadingDesc = "Centralized Voter Management, 2FA KYC Credential Registry & Tamper-Evident Audit Logs";
        loadAdminData();
    } else {
        tabVotingStation.classList.add("active");
        tabAdminPortal.classList.remove("active");
        votingStationView.style.display = "block";
        adminPortalView.style.display = "none";
        pageHeadingTitle.textContent = "Polling Booth Operator Terminal";
        pageHeadingDesc.textContent = "Booth #01 — Live Voter RFID Verification & Duplicate Detection";
        if (voterInput) voterInput.focus();
    }
}

tabVotingStation.addEventListener("click", () => switchTab("votingStation"));
tabAdminPortal.addEventListener("click", () => switchTab("adminPortal"));

adminLoginBtn.addEventListener("click", () => loginModal.classList.add("open"));
closeLoginModal.addEventListener("click", () => loginModal.classList.remove("open"));
window.addEventListener("click", (e) => {
    if (e.target === loginModal) loginModal.classList.remove("open");
});

adminLogoutBtn.addEventListener("click", logoutAdmin);

adminLoginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    loginAdmin(loginUsername.value.trim(), loginPassword.value);
});


// ================= OPERATOR VERIFICATION & LED SYNCHRONIZATION =================

function setOperatorDisplay(status, ledColor, data = {}) {
    clearTimeout(operatorResetTimer);

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
    }
    // 2. YELLOW — VOTER ID IS NOT REGISTERED
    else if (ledColor === "YELLOW" || status === "UNREGISTERED") {
        operatorResultCard.classList.add("state-yellow");
        stateIcon.textContent = "⚠️";
        stateTitle.textContent = "VOTER ID IS NOT REGISTERED";
        stateDesc.textContent = "Access Denied: RFID tag is not registered in the electoral roll. Please verify voter identity.";

        ledYellow.classList.add("active");
        buzzerIndicator.textContent = "⚠️ 3 RAPID WARNING CHIRPS — UNREGISTERED";
        buzzerIndicator.classList.add("beep");
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
    }

    // Auto-return to standby after 4.5 seconds for next voter
    operatorResetTimer = setTimeout(() => {
        resetOperatorDisplay();
    }, 4500);
}

function resetOperatorDisplay() {
    operatorResultCard.classList.remove("state-green", "state-yellow", "state-red");
    operatorResultCard.classList.add("state-idle");
    stateIcon.textContent = "📡";
    stateTitle.textContent = "Ready for Voter RFID Card";
    stateDesc.textContent = "Scan or tap the voter's RFID card on the reader to verify.";

    ledGreen.classList.remove("active");
    ledYellow.classList.remove("active");
    ledRed.classList.remove("active");
    buzzerIndicator.classList.remove("beep");
    buzzerIndicator.textContent = "🔊 BUZZER IDLE";

    if (voterInput) {
        voterInput.value = "";
        voterInput.focus();
    }
}

async function verifyVoter() {
    const input = voterInput.value.trim().toUpperCase();
    if (!input) {
        voterInput.focus();
        return;
    }

    verifyBtn.disabled = true;
    verifyBtn.textContent = "...";

    try {
        const res = await fetch(`${API_BASE}/api/vote/verify-and-record`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rfid_uid: input })
        });

        const data = await res.json();
        setOperatorDisplay(data.status, data.hardware_led, data);
        voterInput.value = "";
    } catch (err) {
        setOperatorDisplay("ERROR", "YELLOW", { voter_name: `Network Error: ${err.message}` });
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = "Verify";
    }
}

verifyBtn.addEventListener("click", verifyVoter);
voterInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") verifyVoter();
});


// ================= ADMIN PORTAL OPERATIONS =================

async function loadAdminData() {
    if (!currentAuthToken) return;

    try {
        const authHeader = { "Authorization": `Bearer ${currentAuthToken}` };

        // 1. Fetch Stats
        const statsRes = await fetch(`${API_BASE}/api/admin/stats`, { headers: authHeader });
        if (statsRes.ok) {
            const stats = await statsRes.json();
            totalVoters.textContent = stats.total_voters;
            votesRecorded.textContent = stats.votes_recorded;
            pendingVotes.textContent = stats.pending_votes;
            fraudAttempts.textContent = stats.fraud_attempts;
            systemStatusText.textContent = "MySQL Online (Port 3306)";
        }

        // 2. Fetch Credentials
        const credRes = await fetch(`${API_BASE}/api/admin/credentials`, { headers: authHeader });
        if (credRes.ok) {
            cachedCredentials = await credRes.json();
            renderCredentialsTable(cachedCredentials);
            populateQuickSelect(cachedCredentials);
        }

        // 3. Fetch Registered Voters
        const votersRes = await fetch(`${API_BASE}/api/admin/voters`, { headers: authHeader });
        if (votersRes.ok) {
            const voters = await votersRes.json();
            renderVotersTable(voters);
        }

        // 4. Fetch Recorded Voted RFIDs
        const rfidsRes = await fetch(`${API_BASE}/api/vote/recorded-rfids`);
        if (rfidsRes.ok) {
            const rfids = await rfidsRes.json();
            recordedCount.textContent = `${rfids.length} Voter${rfids.length !== 1 ? "s" : ""}`;
            if (rfids.length === 0) {
                recordedVotersTable.innerHTML = `<div class="no-recorded">No votes recorded yet.</div>`;
            } else {
                recordedVotersTable.innerHTML = "";
                rfids.forEach(uid => {
                    const item = document.createElement("div");
                    item.className = "recorded-rfid";
                    item.textContent = uid;
                    recordedVotersTable.appendChild(item);
                });
            }
        }

        // 5. Fetch Audit Logs
        const auditRes = await fetch(`${API_BASE}/api/admin/audit-logs`, { headers: authHeader });
        if (auditRes.ok) {
            const logs = await auditRes.json();
            renderAuditTable(logs);
        }
    } catch (err) {
        console.error("Admin data loading error:", err);
    }
}

function renderCredentialsTable(credentials) {
    const unassigned = credentials.filter(c => !c.is_assigned).length;
    credAvailableCount.textContent = `${unassigned} Unassigned`;

    if (credentials.length === 0) {
        credentialsTableBody.innerHTML = `<tr><td colspan="4" class="empty-row">No credentials found in database.</td></tr>`;
        return;
    }

    credentialsTableBody.innerHTML = "";
    credentials.forEach(c => {
        const row = document.createElement("tr");
        const aadharMasked = `XXXX-XXXX-${c.aadhar_number.slice(-4)}`;
        const statusHtml = c.is_assigned
            ? `<span class="badge-pill badge-assigned">Assigned: ${c.assigned_rfid_uid}</span>`
            : `<span class="badge-pill badge-unassigned">✓ Ready for Binding</span>`;

        row.innerHTML = `
            <td><strong>${c.full_name}</strong></td>
            <td><code>${aadharMasked}</code></td>
            <td><span class="code-pill">${c.epic_number}</span></td>
            <td>${statusHtml}</td>
        `;
        credentialsTableBody.appendChild(row);
    });
}

function populateQuickSelect(credentials) {
    quickCredSelect.innerHTML = `<option value="">-- Select an unassigned citizen profile --</option>`;
    const unassigned = credentials.filter(c => !c.is_assigned);

    unassigned.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.full_name} | EPIC: ${c.epic_number} | Aadhaar: ...${c.aadhar_number.slice(-4)}`;
        quickCredSelect.appendChild(opt);
    });
}

quickCredSelect.addEventListener("change", () => {
    const selectedId = parseInt(quickCredSelect.value);
    if (!selectedId) return;

    const cred = cachedCredentials.find(c => c.id === selectedId);
    if (cred) {
        regVoterName.value = cred.full_name;
        regAadhar.value = cred.aadhar_number;
        regEpic.value = cred.epic_number;
        regPhone.value = cred.phone_number || "";
        regAlertBox.style.display = "none";
    }
});

voterRegistrationForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentAuthToken) return;

    submitRegBtn.disabled = true;
    submitRegBtn.textContent = "Verifying 2FA & Registering...";
    regAlertBox.style.display = "none";

    const payload = {
        rfid_uid: regRfidUid.value.trim().toUpperCase(),
        name: regVoterName.value.trim(),
        aadhar_number: regAadhar.value.trim(),
        epic_number: regEpic.value.trim().toUpperCase(),
        phone_number: regPhone.value.trim() || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/admin/voters`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentAuthToken}`
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.status === 409) {
            regAlertBox.className = "alert-box alert-error";
            regAlertBox.innerHTML = `<strong>🚨 2FA Security Conflict Blocked:</strong><br>${data.detail}`;
            regAlertBox.style.display = "block";
            return;
        }

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed.");
        }

        regAlertBox.className = "alert-box alert-success";
        regAlertBox.innerHTML = `<strong>✅ 2FA Voter Successfully Bound & Registered!</strong><br>Citizen <strong>${data.name}</strong> (${data.voter_code}) is now linked to RFID UID <code>${data.rfid_uid}</code>.`;
        regAlertBox.style.display = "block";

        voterRegistrationForm.reset();
        await loadAdminData();
    } catch (err) {
        regAlertBox.className = "alert-box alert-error";
        regAlertBox.innerHTML = `<strong>Error:</strong> ${err.message}`;
        regAlertBox.style.display = "block";
    } finally {
        submitRegBtn.disabled = false;
        submitRegBtn.textContent = "🛡️ Verify Credentials & Register RFID UID";
    }
});

function renderVotersTable(voters) {
    if (voters.length === 0) {
        votersTableBody.innerHTML = `<tr><td colspan="6" class="empty-row">No registered voters yet.</td></tr>`;
        return;
    }

    votersTableBody.innerHTML = "";
    voters.forEach(v => {
        const row = document.createElement("tr");
        const aadharMasked = `XXXX-XXXX-${v.aadhar_number.slice(-4)}`;
        const statusHtml = v.has_voted
            ? `<span class="badge-pill badge-voted">✓ Voted</span>`
            : `<span class="badge-pill badge-notvoted">Pending</span>`;
        const votedTime = v.voted_at ? new Date(v.voted_at).toLocaleString() : "—";

        row.innerHTML = `
            <td><strong>${v.voter_code}</strong></td>
            <td>${v.name}</td>
            <td><code>${aadharMasked}</code></td>
            <td><span class="code-pill">${v.rfid_uid}</span></td>
            <td>${statusHtml}</td>
            <td>${votedTime}</td>
        `;
        votersTableBody.appendChild(row);
    });
}

function renderAuditTable(logs) {
    if (logs.length === 0) {
        auditTableBody.innerHTML = `<tr><td colspan="6" class="empty-row">No audit records logged yet.</td></tr>`;
        return;
    }

    auditTableBody.innerHTML = "";
    logs.forEach(l => {
        const row = document.createElement("tr");
        let statusBadge = `<span class="badge-pill badge-assigned">${l.status}</span>`;
        if (l.status === "SUCCESS") statusBadge = `<span class="badge-pill badge-unassigned">${l.status}</span>`;
        else if (l.status === "WARNING" || l.status === "DENIED") statusBadge = `<span class="badge-pill badge-notvoted">${l.status}</span>`;

        const timeStr = new Date(l.timestamp).toLocaleTimeString();

        row.innerHTML = `
            <td>#${l.id}</td>
            <td><code>${l.event_type}</code></td>
            <td>${l.rfid_uid ? `<span class="code-pill">${l.rfid_uid}</span>` : "—"}</td>
            <td>${statusBadge}</td>
            <td style="font-size: 13px;">${l.details}</td>
            <td>${timeStr}</td>
        `;
        auditTableBody.appendChild(row);
    });
}

refreshVotersBtn.addEventListener("click", loadAdminData);
refreshAuditBtn.addEventListener("click", loadAdminData);

resetVotesBtn.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to reset all voting statuses to 'Not Voted' for testing? Registered voters and credentials will be preserved.")) {
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/admin/reset-votes`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${currentAuthToken}` }
        });
        if (res.ok) {
            alert("All voting flags have been reset to 'Not Voted'.");
            await loadAdminData();
        }
    } catch (err) {
        alert(`Reset failed: ${err.message}`);
    }
});


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


// ================= INITIALIZATION =================

applyTheme(getSavedTheme(), false);
updateAuthUI();

// Auto-focus scanner input
if (voterInput) {
    voterInput.focus();
}

// Live polling every 4 seconds to sync admin dashboard if active
setInterval(() => {
    if (currentAuthToken && adminPortalView.style.display !== "none") {
        loadAdminData();
    }
}, 4000);
