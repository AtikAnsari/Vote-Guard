/**
 * VOTE-GUARD — Administrator Console Controller
 * Comprehensive Voter Registration with 2FA KYC Credential Verification
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
if (user.role !== "admin") {
    // If an operator accidentally lands on admin page, redirect them to operator page
    window.location.href = "operator.html";
}

document.getElementById("adminNameDisplay").textContent = user.full_name || user.username || "Administrator";

// DOM Elements
const logoutBtn = document.getElementById("logoutBtn");
const systemStatusText = document.getElementById("systemStatusText");
const demoAdminBanner = document.getElementById("demoAdminBanner");
const demoResetStorageBtn = document.getElementById("demoResetStorageBtn");

// Activate Demo Mode Banner if in Demo Mode
if (IS_DEMO && demoAdminBanner) {
    demoAdminBanner.style.display = "block";
}

if (demoResetStorageBtn) {
    demoResetStorageBtn.addEventListener("click", () => {
        if (confirm("Reset all demo data (voters, 2FA KYC credentials, and audit logs) to pristine default state?")) {
            if (window.VoteGuardMock) {
                window.VoteGuardMock.resetAllData();
                loadAllAdminData();
                alert("All demo storage data has been restored to default seeds.");
            }
        }
    });
}

const totalVoters = document.getElementById("totalVoters");
const votesRecorded = document.getElementById("votesRecorded");
const pendingVotes = document.getElementById("pendingVotes");
const fraudAttempts = document.getElementById("fraudAttempts");

const voterRegistrationForm = document.getElementById("voterRegistrationForm");
const regRfidUid = document.getElementById("regRfidUid");
const regVoterName = document.getElementById("regVoterName");
const regAadhar = document.getElementById("regAadhar");
const regEpic = document.getElementById("regEpic");
const regPhone = document.getElementById("regPhone");
const submitRegBtn = document.getElementById("submitRegBtn");
const regAlertBox = document.getElementById("regAlertBox");
const tapToFillBtn = document.getElementById("tapToFillBtn");

const credAvailableCount = document.getElementById("credAvailableCount");
const credentialsTableBody = document.getElementById("credentialsTableBody");
const votersTableBody = document.getElementById("votersTableBody");
const recordedVotersTable = document.getElementById("recordedVotersTable");
const recordedCount = document.getElementById("recordedCount");
const auditTableBody = document.getElementById("auditTableBody");

const refreshVotersBtn = document.getElementById("refreshVotersBtn");
const refreshAuditBtn = document.getElementById("refreshAuditBtn");
const resetVotesBtn = document.getElementById("resetVotesBtn");
const themeSelect = document.getElementById("themeSelect");

let cachedCredentials = [];


// ================= LOGOUT =================

logoutBtn.addEventListener("click", () => {
    sessionStorage.clear();
    window.location.href = "login.html";
});


// ================= DATA LOADING =================

async function loadAllAdminData() {
    // Public Demo Mode interceptor: read from local mock engine
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const stats = window.VoteGuardMock.getStats();
            totalVoters.textContent = stats.total_voters;
            votesRecorded.textContent = stats.votes_recorded;
            pendingVotes.textContent = stats.pending_votes;
            fraudAttempts.textContent = stats.fraud_attempts;
            systemStatusText.textContent = "Mock Storage Active";
            systemStatusText.style.color = "#16a34a";

            cachedCredentials = window.VoteGuardMock.getCredentials();
            renderCredentialsTable(cachedCredentials);

            const voters = window.VoteGuardMock.getVoters();
            renderVotersTable(voters);

            const rfids = window.VoteGuardMock.getRecordedRfids();
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

            const logs = window.VoteGuardMock.getAuditLogs();
            renderAuditTable(logs);
        } catch (err) {
            console.error("Demo admin data loading failed:", err);
            systemStatusText.textContent = "Demo Storage Error";
            systemStatusText.style.color = "#dc2626";
        }
        return;
    }

    // Full-Stack Mode: Connect to live FastAPI backend
    const authHeader = { "Authorization": `Bearer ${token}` };

    try {
        // 1. Stats
        const statsRes = await fetch(`${API_BASE}/api/admin/stats`, { headers: authHeader });
        if (statsRes.ok) {
            const stats = await statsRes.json();
            totalVoters.textContent = stats.total_voters;
            votesRecorded.textContent = stats.votes_recorded;
            pendingVotes.textContent = stats.pending_votes;
            fraudAttempts.textContent = stats.fraud_attempts;
            systemStatusText.textContent = "MySQL Online (Port 3306)";
            systemStatusText.style.color = "#16a34a";
        }

        // 2. Credentials
        const credRes = await fetch(`${API_BASE}/api/admin/credentials`, { headers: authHeader });
        if (credRes.ok) {
            cachedCredentials = await credRes.json();
            renderCredentialsTable(cachedCredentials);
        }

        // 3. Registered Voters
        const votersRes = await fetch(`${API_BASE}/api/admin/voters`, { headers: authHeader });
        if (votersRes.ok) {
            const voters = await votersRes.json();
            renderVotersTable(voters);
        }

        // 4. Recorded Voted Cards
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

        // 5. Audit Logs
        const auditRes = await fetch(`${API_BASE}/api/admin/audit-logs`, { headers: authHeader });
        if (auditRes.ok) {
            const logs = await auditRes.json();
            renderAuditTable(logs);
        }

    } catch (err) {
        console.error("Admin data loading failed:", err);
        systemStatusText.textContent = "Offline / Connection Error";
        systemStatusText.style.color = "#dc2626";
    }
}


// ================= RENDERING ROUTINES =================

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

voterRegistrationForm.addEventListener("submit", async (e) => {
    e.preventDefault();
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

    // Public Demo Mode interceptor: register in local mock storage
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const newVoter = window.VoteGuardMock.registerVoter(payload);
            regAlertBox.className = "alert-box alert-success";
            regAlertBox.innerHTML = `<strong>✅ 2FA Voter Successfully Bound & Registered!</strong><br>Citizen <strong>${newVoter.name}</strong> (${newVoter.voter_code}) is now linked to RFID UID <code>${newVoter.rfid_uid}</code>.`;
            regAlertBox.style.display = "block";

            voterRegistrationForm.reset();
            await loadAllAdminData();
        } catch (err) {
            regAlertBox.className = "alert-box alert-error";
            if (err.status === 409) {
                regAlertBox.innerHTML = `<strong>🚨 2FA Security Conflict Blocked:</strong><br>${err.message}`;
            } else {
                regAlertBox.innerHTML = `<strong>Error:</strong> ${err.message}`;
            }
            regAlertBox.style.display = "block";
        } finally {
            submitRegBtn.disabled = false;
            submitRegBtn.textContent = "🛡️ Verify Credentials & Register RFID UID";
        }
        return;
    }

    // Full-Stack Mode: Connect to live FastAPI backend
    try {
        const response = await fetch(`${API_BASE}/api/admin/voters`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        let data = {};
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
            data = await response.json().catch(() => ({}));
        } else {
            const rawText = await response.text().catch(() => "");
            data = { detail: rawText || `Server returned HTTP ${response.status}` };
        }

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
        await loadAllAdminData();
    } catch (err) {
        regAlertBox.className = "alert-box alert-error";
        regAlertBox.innerHTML = `<strong>Error:</strong> ${err.message}`;
        regAlertBox.style.display = "block";
    } finally {
        submitRegBtn.disabled = false;
        submitRegBtn.textContent = "🛡️ Verify Credentials & Register RFID UID";
    }
});


// ================= AUTO-CAPTURE RFID TAP FROM READER =================

let isListeningForCard = false;
let captureStartEventId = 0;
let captureInterval = null;

if (tapToFillBtn) {
    tapToFillBtn.addEventListener("click", async () => {
        // Public Demo Mode interceptor: capture latest event or sample unassigned tag
        if (IS_DEMO && window.VoteGuardMock) {
            const latest = window.VoteGuardMock.getLatestEvent();
            const captured = (latest && latest.rfid_uid) ? latest.rfid_uid : "E4D3C2B1";
            regRfidUid.value = captured;
            tapToFillBtn.textContent = `✓ Captured: ${captured}`;
            tapToFillBtn.style.background = "#dcfce7";
            setTimeout(() => {
                tapToFillBtn.textContent = "📡 Tap to Capture";
                tapToFillBtn.style.background = "";
            }, 3000);
            return;
        }

        if (isListeningForCard) {
            clearInterval(captureInterval);
            isListeningForCard = false;
            tapToFillBtn.textContent = "📡 Tap to Capture";
            tapToFillBtn.style.background = "";
            return;
        }

        try {
            const initRes = await fetch(`${API_BASE}/api/vote/latest-event`);
            const initData = await initRes.json();
            captureStartEventId = initData.event_id || 0;

            isListeningForCard = true;
            tapToFillBtn.textContent = "⌛ Tap Card on Reader Now...";
            tapToFillBtn.style.background = "#fef08a";

            captureInterval = setInterval(async () => {
                try {
                    const pollRes = await fetch(`${API_BASE}/api/vote/latest-event`);
                    const pollData = await pollRes.json();
                    if (pollData.event_id > captureStartEventId && pollData.rfid_uid) {
                        clearInterval(captureInterval);
                        isListeningForCard = false;
                        regRfidUid.value = pollData.rfid_uid;
                        tapToFillBtn.textContent = `✓ Captured: ${pollData.rfid_uid}`;
                        tapToFillBtn.style.background = "#dcfce7";
                        setTimeout(() => {
                            tapToFillBtn.textContent = "📡 Tap to Capture";
                            tapToFillBtn.style.background = "";
                        }, 4000);
                    }
                } catch (e) {}
            }, 500);

        } catch (err) {
            console.warn("Could not start card capture listener:", err);
        }
    });
}


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

refreshVotersBtn.addEventListener("click", loadAllAdminData);
refreshAuditBtn.addEventListener("click", loadAllAdminData);

resetVotesBtn.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to reset all voting statuses to 'Not Voted' for testing? Registered voters and KYC credentials will be preserved.")) {
        return;
    }

    // Public Demo Mode interceptor: reset local mock storage ONLY (NEVER calls backend)
    if (IS_DEMO && window.VoteGuardMock) {
        window.VoteGuardMock.resetVotes();
        alert("All demo voting flags have been reset to 'Not Voted'.");
        await loadAllAdminData();
        return;
    }

    // Full-Stack Mode: Connect to live FastAPI backend
    try {
        const res = await fetch(`${API_BASE}/api/admin/reset-votes`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            alert("All voting flags have been reset to 'Not Voted'.");
            await loadAllAdminData();
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

applyTheme(getSavedTheme(), false);
loadAllAdminData();

// Live background poll every 4 seconds to sync counts and audit logs
setInterval(loadAllAdminData, 4000);

