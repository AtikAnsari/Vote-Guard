/**
 * VOTE-GUARD — Public Demo Mock Engine
 * Self-contained in-browser simulation layer for GitHub Pages & static demonstrations.
 * Simulates FastAPI endpoints, MySQL database, and ESP32 + RC522 RFID hardware.
 * 
 * Storage Namespace:
 * - voteGuard_demo_voters
 * - voteGuard_demo_credentials
 * - voteGuard_demo_users
 * - voteGuard_demo_audit
 * - voteGuard_demo_latestEvent
 */

(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.VoteGuardMock = factory();
    }
}(typeof self !== 'undefined' ? self : this, function () {

    // ================= STORAGE KEYS =================
    const STORAGE_KEYS = {
        VOTERS: "voteGuard_demo_voters",
        CREDENTIALS: "voteGuard_demo_credentials",
        USERS: "voteGuard_demo_users",
        AUDIT: "voteGuard_demo_audit",
        LATEST_EVENT: "voteGuard_demo_latestEvent"
    };

    // ================= SYNTHETIC DEFAULT SEED DATA =================
    // Pure fictional identities for safe public demonstration
    const DEFAULT_CREDENTIALS = [
        {
            id: 1,
            full_name: "Aman Patel",
            aadhar_number: "234567890123",
            epic_number: "VGD1000001",
            is_assigned: true,
            assigned_rfid_uid: "71411605",
            assigned_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            id: 2,
            full_name: "Priya Sharma",
            aadhar_number: "345678901234",
            epic_number: "VGD1000002",
            is_assigned: true,
            assigned_rfid_uid: "8A4F123B",
            assigned_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            id: 3,
            full_name: "Rajesh Kumar",
            aadhar_number: "456789012345",
            epic_number: "VGD1000003",
            is_assigned: true,
            assigned_rfid_uid: "B2C3D4E5",
            assigned_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
            id: 4,
            full_name: "Sunita Devi",
            aadhar_number: "567890123456",
            epic_number: "VGD1000004",
            is_assigned: false,
            assigned_rfid_uid: null,
            assigned_at: null
        },
        {
            id: 5,
            full_name: "Vikram Singh",
            aadhar_number: "678901234567",
            epic_number: "VGD1000005",
            is_assigned: false,
            assigned_rfid_uid: null,
            assigned_at: null
        }
    ];

    const DEFAULT_VOTERS = [
        {
            id: 1,
            voter_code: "VTR-001",
            name: "Aman Patel",
            aadhar_number: "234567890123",
            epic_number: "VGD1000001",
            rfid_uid: "71411605",
            has_voted: false,
            voted_at: null,
            created_at: new Date(Date.now() - 7200000).toISOString()
        },
        {
            id: 2,
            voter_code: "VTR-002",
            name: "Priya Sharma",
            aadhar_number: "345678901234",
            epic_number: "VGD1000002",
            rfid_uid: "8A4F123B",
            has_voted: false,
            voted_at: null,
            created_at: new Date(Date.now() - 7200000).toISOString()
        },
        {
            id: 3,
            voter_code: "VTR-003",
            name: "Rajesh Kumar",
            aadhar_number: "456789012345",
            epic_number: "VGD1000003",
            rfid_uid: "B2C3D4E5",
            has_voted: true,
            voted_at: new Date(Date.now() - 1800000).toISOString(),
            created_at: new Date(Date.now() - 7200000).toISOString()
        }
    ];

    const DEFAULT_USERS = [
        {
            username: "admin",
            password: "admin123",
            full_name: "Demo Administrator",
            role: "admin"
        },
        {
            username: "operator",
            password: "operator123",
            full_name: "Demo Polling Officer",
            role: "operator"
        }
    ];

    const DEFAULT_AUDIT = [
        {
            id: 1,
            event_type: "SYSTEM_INIT",
            rfid_uid: null,
            status: "SUCCESS",
            details: "Vote-Guard public demo environment initialized. Synthetic 2FA KYC and voters active.",
            timestamp: new Date(Date.now() - 3600000).toISOString()
        },
        {
            id: 2,
            event_type: "VOTE_ACCEPTED",
            rfid_uid: "B2C3D4E5",
            status: "SUCCESS",
            details: "Vote recorded for Rajesh Kumar (VTR-003) with UID B2C3D4E5",
            timestamp: new Date(Date.now() - 1800000).toISOString()
        }
    ];

    const DEFAULT_LATEST_EVENT = {
        event_id: 2,
        status: "ACCEPTED",
        hardware_led: "GREEN",
        message: "✅ Voter Verified Successfully. Vote recorded.",
        voter_name: "Rajesh Kumar",
        voter_code: "VTR-003",
        rfid_uid: "B2C3D4E5",
        timestamp: new Date(Date.now() - 1800000).toISOString()
    };

    // ================= HELPER UTILITIES =================

    function safeGet(key, defaultVal) {
        try {
            const raw = localStorage.getItem(key);
            if (!raw) return defaultVal;
            return JSON.parse(raw);
        } catch (e) {
            console.warn(`[VoteGuardMock] Corrupted localStorage for ${key}, falling back to default.`);
            return defaultVal;
        }
    }

    function safeSet(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error(`[VoteGuardMock] Failed to persist ${key}:`, e);
        }
    }

    // ================= INITIALIZATION =================

    function init() {
        if (!localStorage.getItem(STORAGE_KEYS.CREDENTIALS)) {
            safeSet(STORAGE_KEYS.CREDENTIALS, DEFAULT_CREDENTIALS);
        }
        if (!localStorage.getItem(STORAGE_KEYS.VOTERS)) {
            safeSet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        }
        if (!localStorage.getItem(STORAGE_KEYS.USERS)) {
            safeSet(STORAGE_KEYS.USERS, DEFAULT_USERS);
        }
        if (!localStorage.getItem(STORAGE_KEYS.AUDIT)) {
            safeSet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);
        }
        if (!localStorage.getItem(STORAGE_KEYS.LATEST_EVENT)) {
            safeSet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
        }
    }

    function resetAllData() {
        safeSet(STORAGE_KEYS.CREDENTIALS, DEFAULT_CREDENTIALS);
        safeSet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        safeSet(STORAGE_KEYS.USERS, DEFAULT_USERS);
        safeSet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);
        safeSet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
        console.log("[VoteGuardMock] All demo localStorage data reset to pristine seed state.");
    }

    // ================= CENTRALIZED DEMO DETECTION =================

    function isDemoMode() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            // Explicit override via query parameters
            if (urlParams.get("demo") === "true") return true;
            if (urlParams.get("demo") === "false") return false;

            // GitHub Pages production hosting URL
            if (window.location.hostname && window.location.hostname.toLowerCase().includes("github.io")) {
                return true;
            }

            // Explicit session flag from previous login in demo mode
            if (sessionStorage.getItem("voteGuard_is_demo") === "true") {
                return true;
            }

            // Otherwise, default to full-stack mode (e.g. localhost:8000 or local server)
            return false;
        } catch (e) {
            return false;
        }
    }

    // ================= AUTHENTICATION =================

    function login(username, password) {
        init();
        const users = safeGet(STORAGE_KEYS.USERS, DEFAULT_USERS);
        const cleanUser = (username || "").trim().toLowerCase();
        const found = users.find(u => u.username.toLowerCase() === cleanUser && u.password === password);

        if (!found) {
            throw new Error("Invalid demo username or password. Use admin / admin123 or operator / operator123.");
        }

        const token = `demo-token-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        const userObj = {
            username: found.username,
            full_name: found.full_name,
            role: found.role
        };

        // Mark session as demo
        sessionStorage.setItem("voteGuard_is_demo", "true");
        sessionStorage.setItem("voteGuardToken", token);
        sessionStorage.setItem("voteGuardUser", JSON.stringify(userObj));

        const redirectUrl = found.role === "admin" ? "admin.html" : "operator.html";

        return {
            access_token: token,
            token_type: "bearer",
            username: found.username,
            full_name: found.full_name,
            role: found.role,
            redirect_url: redirectUrl
        };
    }

    function signup(userObj) {
        init();
        const users = safeGet(STORAGE_KEYS.USERS, DEFAULT_USERS);
        const cleanUsername = (userObj.username || "").trim().toLowerCase();

        if (!cleanUsername || !userObj.password || !userObj.full_name) {
            throw new Error("All fields are required.");
        }

        if (users.some(u => u.username.toLowerCase() === cleanUsername)) {
            throw new Error(`Username '${cleanUsername}' is already taken in the demo registry.`);
        }

        const newUser = {
            username: cleanUsername,
            password: userObj.password,
            full_name: userObj.full_name.trim(),
            role: userObj.role || "operator"
        };

        users.push(newUser);
        safeSet(STORAGE_KEYS.USERS, users);

        return login(newUser.username, newUser.password);
    }

    // ================= OPERATOR RFID VERIFICATION =================

    function verifyAndRecord(rfid_uid) {
        init();
        const cleanUid = (rfid_uid || "").replace(/[\s:-]/g, "").toUpperCase();
        if (!cleanUid) {
            throw new Error("RFID UID cannot be empty.");
        }

        const voters = safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        const audit = safeGet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);
        const now = new Date();
        const nowIso = now.toISOString();

        // Check if UID is in voters table
        const voterIndex = voters.findIndex(v => v.rfid_uid === cleanUid);

        // 1. UNREGISTERED CARD
        if (voterIndex === -1) {
            const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
            audit.push({
                id: nextAuditId,
                event_type: "UNREGISTERED_CARD",
                rfid_uid: cleanUid,
                voter_id: null,
                status: "DENIED",
                details: `Unregistered RFID card presented: ${cleanUid}`,
                timestamp: nowIso
            });
            safeSet(STORAGE_KEYS.AUDIT, audit);

            const latestEvent = safeGet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
            const nextEventId = (latestEvent.event_id || 0) + 1;
            const eventPayload = {
                event_id: nextEventId,
                status: "UNREGISTERED",
                hardware_led: "YELLOW",
                message: "⚠️ Voter ID is Not Registered. Access Denied.",
                rfid_uid: cleanUid,
                timestamp: nowIso
            };
            safeSet(STORAGE_KEYS.LATEST_EVENT, eventPayload);

            return eventPayload;
        }

        const voter = voters[voterIndex];

        // 2. ALREADY VOTED (DUPLICATE ATTEMPT)
        if (voter.has_voted) {
            const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
            audit.push({
                id: nextAuditId,
                event_type: "DUPLICATE_ATTEMPT",
                rfid_uid: cleanUid,
                voter_id: voter.id,
                status: "WARNING",
                details: `Duplicate vote attempt blocked for ${voter.name} (${voter.voter_code}) with UID ${cleanUid}`,
                timestamp: nowIso
            });
            safeSet(STORAGE_KEYS.AUDIT, audit);

            const latestEvent = safeGet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
            const nextEventId = (latestEvent.event_id || 0) + 1;
            const eventPayload = {
                event_id: nextEventId,
                status: "ALREADY_VOTED",
                hardware_led: "RED",
                message: "🚨 Duplicate Voting Detected! Vote blocked.",
                voter_name: voter.name,
                voter_code: voter.voter_code,
                rfid_uid: cleanUid,
                timestamp: voter.voted_at || nowIso
            };
            safeSet(STORAGE_KEYS.LATEST_EVENT, eventPayload);

            return eventPayload;
        }

        // 3. VOTE ACCEPTED (VOTE IS DONE)
        voter.has_voted = true;
        voter.voted_at = nowIso;
        voters[voterIndex] = voter;
        safeSet(STORAGE_KEYS.VOTERS, voters);

        const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
        audit.push({
            id: nextAuditId,
            event_type: "VOTE_ACCEPTED",
            rfid_uid: cleanUid,
            voter_id: voter.id,
            status: "SUCCESS",
            details: `Vote recorded for ${voter.name} (${voter.voter_code}) with UID ${cleanUid}`,
            timestamp: nowIso
        });
        safeSet(STORAGE_KEYS.AUDIT, audit);

        const latestEvent = safeGet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
        const nextEventId = (latestEvent.event_id || 0) + 1;
        const eventPayload = {
            event_id: nextEventId,
            status: "ACCEPTED",
            hardware_led: "GREEN",
            message: "✅ Voter Verified Successfully. Vote recorded.",
            voter_name: voter.name,
            voter_code: voter.voter_code,
            rfid_uid: cleanUid,
            timestamp: nowIso
        };
        safeSet(STORAGE_KEYS.LATEST_EVENT, eventPayload);

        return eventPayload;
    }

    function getLatestEvent() {
        init();
        return safeGet(STORAGE_KEYS.LATEST_EVENT, DEFAULT_LATEST_EVENT);
    }

    // ================= ADMIN DATA & REGISTRATION =================

    function getStats() {
        init();
        const voters = safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        const credentials = safeGet(STORAGE_KEYS.CREDENTIALS, DEFAULT_CREDENTIALS);
        const audit = safeGet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);

        const total = voters.length;
        const voted = voters.filter(v => v.has_voted).length;
        const pending = total - voted;
        const fraud = audit.filter(a => a.event_type === "DUPLICATE_ATTEMPT").length;
        const availableCreds = credentials.filter(c => !c.is_assigned).length;

        return {
            total_voters: total,
            votes_recorded: voted,
            pending_votes: pending,
            fraud_attempts: fraud,
            available_credentials: availableCreds
        };
    }

    function getCredentials() {
        init();
        return safeGet(STORAGE_KEYS.CREDENTIALS, DEFAULT_CREDENTIALS);
    }

    function getVoters() {
        init();
        return safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
    }

    function getRecordedRfids() {
        init();
        const voters = safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        return voters.filter(v => v.has_voted).map(v => v.rfid_uid);
    }

    function getAuditLogs() {
        init();
        const audit = safeGet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);
        // Return latest logs first
        return audit.slice().reverse();
    }

    function registerVoter(payload) {
        init();
        const cleanUid = (payload.rfid_uid || "").replace(/[\s:-]/g, "").toUpperCase();
        const cleanAadhar = (payload.aadhar_number || "").replace(/[\s-]/g, "").trim();
        const cleanEpic = (payload.epic_number || "").trim().toUpperCase();
        const cleanName = (payload.name || "").trim();

        if (!cleanUid || !cleanAadhar || !cleanEpic || !cleanName) {
            throw new Error("All fields marked with * are required.");
        }

        const voters = safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        const credentials = safeGet(STORAGE_KEYS.CREDENTIALS, DEFAULT_CREDENTIALS);
        const audit = safeGet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);

        // 1. Check if RFID UID is already in voters
        const existingVoterByUid = voters.find(v => v.rfid_uid === cleanUid);
        if (existingVoterByUid) {
            const err = new Error(`RFID Conflict: Tag '${cleanUid}' is ALREADY registered to voter '${existingVoterByUid.name}' (${existingVoterByUid.voter_code})!`);
            err.status = 409;
            throw err;
        }

        // 2. Check if RFID UID is assigned in credentials
        const existingCredByUid = credentials.find(c => c.assigned_rfid_uid === cleanUid);
        if (existingCredByUid) {
            const err = new Error(`RFID Conflict: Tag '${cleanUid}' is ALREADY assigned to citizen '${existingCredByUid.full_name}' (EPIC: ${existingCredByUid.epic_number})!`);
            err.status = 409;
            throw err;
        }

        // 3. Check if EPIC is already used in voters
        const existingVoterByCode = voters.find(v => v.voter_code === cleanEpic || v.epic_number === cleanEpic);
        if (existingVoterByCode) {
            const err = new Error(`Election Card Conflict: Card '${cleanEpic}' is already registered to '${existingVoterByCode.name}' with UID '${existingVoterByCode.rfid_uid}'!`);
            err.status = 409;
            throw err;
        }

        // 4. Check 2FA Credentials table
        const credIndex = credentials.findIndex(c => 
            c.aadhar_number === cleanAadhar || c.epic_number === cleanEpic
        );

        const nowIso = new Date().toISOString();

        if (credIndex !== -1) {
            const cred = credentials[credIndex];
            if (cred.is_assigned && cred.assigned_rfid_uid) {
                // Log rejected registration
                const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
                audit.push({
                    id: nextAuditId,
                    event_type: "REGISTRATION_REJECTED",
                    rfid_uid: cleanUid,
                    status: "DENIED",
                    details: `2FA Conflict: Aadhaar/EPIC already assigned to UID '${cred.assigned_rfid_uid}' (Voter: ${cred.full_name})`,
                    timestamp: nowIso
                });
                safeSet(STORAGE_KEYS.AUDIT, audit);

                const err = new Error(`2FA Conflict: These credentials (Aadhaar: ${cleanAadhar.slice(-4)} / EPIC: ${cleanEpic}) are ALREADY used and assigned to RFID UID '${cred.assigned_rfid_uid}' (Voter: ${cred.full_name}). Multiple UIDs cannot be assigned to the same citizen credentials!`);
                err.status = 409;
                throw err;
            } else {
                // Bind existing credential
                cred.is_assigned = true;
                cred.assigned_rfid_uid = cleanUid;
                cred.assigned_at = nowIso;
                if (!cred.full_name && cleanName) cred.full_name = cleanName;
                credentials[credIndex] = cred;
            }
        } else {
            // Create new synthetic credential
            const newCredId = credentials.length > 0 ? Math.max(...credentials.map(c => c.id)) + 1 : 1;
            credentials.push({
                id: newCredId,
                full_name: cleanName,
                aadhar_number: cleanAadhar,
                epic_number: cleanEpic,
                is_assigned: true,
                assigned_rfid_uid: cleanUid,
                assigned_at: nowIso
            });
        }
        safeSet(STORAGE_KEYS.CREDENTIALS, credentials);

        // Add to voters directory
        const nextVoterId = voters.length > 0 ? Math.max(...voters.map(v => v.id)) + 1 : 1;
        const newVoter = {
            id: nextVoterId,
            voter_code: `VTR-${String(nextVoterId).padStart(3, "0")}`,
            name: cleanName,
            aadhar_number: cleanAadhar,
            epic_number: cleanEpic,
            rfid_uid: cleanUid,
            has_voted: false,
            voted_at: null,
            created_at: nowIso
        };
        voters.push(newVoter);
        safeSet(STORAGE_KEYS.VOTERS, voters);

        // Audit log
        const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
        audit.push({
            id: nextAuditId,
            event_type: "VOTER_REGISTERED",
            rfid_uid: cleanUid,
            status: "SUCCESS",
            details: `Registered voter ${newVoter.name} (${newVoter.voter_code}) with 2FA Aadhaar XXXX-XXXX-${cleanAadhar.slice(-4)} and UID ${cleanUid}`,
            timestamp: nowIso
        });
        safeSet(STORAGE_KEYS.AUDIT, audit);

        return newVoter;
    }

    function resetVotes() {
        init();
        const voters = safeGet(STORAGE_KEYS.VOTERS, DEFAULT_VOTERS);
        const audit = safeGet(STORAGE_KEYS.AUDIT, DEFAULT_AUDIT);
        const nowIso = new Date().toISOString();

        voters.forEach(v => {
            v.has_voted = false;
            v.voted_at = null;
        });
        safeSet(STORAGE_KEYS.VOTERS, voters);

        const nextAuditId = audit.length > 0 ? Math.max(...audit.map(a => a.id)) + 1 : 1;
        audit.push({
            id: nextAuditId,
            event_type: "VOTING_RESET",
            rfid_uid: null,
            status: "WARNING",
            details: "Demo voting flags reset to 'Not Voted' for testing. Voter records and 2FA KYC preserved.",
            timestamp: nowIso
        });
        safeSet(STORAGE_KEYS.AUDIT, audit);

        return { success: true, message: "All voting statuses reset to 'Not Voted'." };
    }

    // ================= WEB AUDIO BUZZER SIMULATOR =================

    function playBuzzerSound(type) {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            const ctx = new AudioContext();
            if (ctx.state === "suspended") {
                ctx.resume();
            }

            if (type === "GREEN" || type === "ACCEPTED") {
                // Short high beep (880Hz, 200ms)
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(880, ctx.currentTime);
                gain.gain.setValueAtTime(0.15, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.2);
            } else if (type === "RED" || type === "ALREADY_VOTED") {
                // 2 Long warning buzzes (320Hz, 300ms each)
                [0, 0.4].forEach(delay => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = "sawtooth";
                    osc.frequency.setValueAtTime(320, ctx.currentTime + delay);
                    gain.gain.setValueAtTime(0.2, ctx.currentTime + delay);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.3);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + delay);
                    osc.stop(ctx.currentTime + delay + 0.3);
                });
            } else if (type === "YELLOW" || type === "UNREGISTERED") {
                // 3 Rapid warning chirps (600Hz, 80ms each)
                [0, 0.15, 0.3].forEach(delay => {
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = "triangle";
                    osc.frequency.setValueAtTime(600, ctx.currentTime + delay);
                    gain.gain.setValueAtTime(0.18, ctx.currentTime + delay);
                    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.09);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start(ctx.currentTime + delay);
                    osc.stop(ctx.currentTime + delay + 0.09);
                });
            }
        } catch (e) {
            // Autoplay policy or uninitialized audio context
            console.warn("[VoteGuardMock] Web Audio playback skipped:", e.message);
        }
    }

    // Auto-init storage on load
    init();

    return {
        isDemoMode,
        init,
        resetAllData,
        login,
        signup,
        verifyAndRecord,
        getLatestEvent,
        getStats,
        getCredentials,
        getVoters,
        getRecordedRfids,
        getAuditLogs,
        registerVoter,
        resetVotes,
        playBuzzerSound
    };
}));

