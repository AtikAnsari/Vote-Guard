/**
 * VOTE-GUARD — Authentication & Gateway Controller
 * Handles Login, Registration, and Role-Based Redirection
 */

const API_BASE = (window.location.hostname && (window.location.port === "8000")) 
    ? window.location.origin 
    : "http://127.0.0.1:8000";

// Centralized Demo Mode Detection
const IS_DEMO = window.VoteGuardMock ? window.VoteGuardMock.isDemoMode() : false;

// DOM Elements
const demoModeBanner = document.getElementById("demoModeBanner");
const tabLoginBtn = document.getElementById("tabLoginBtn");
const tabSignupBtn = document.getElementById("tabSignupBtn");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");

const fillAdminBtn = document.getElementById("fillAdminBtn");
const fillOperatorBtn = document.getElementById("fillOperatorBtn");

const loginUsername = document.getElementById("loginUsername");
const loginPassword = document.getElementById("loginPassword");
const loginSubmitBtn = document.getElementById("loginSubmitBtn");
const loginAlert = document.getElementById("loginAlert");

const signupFullName = document.getElementById("signupFullName");
const signupUsername = document.getElementById("signupUsername");
const signupPassword = document.getElementById("signupPassword");
const signupRole = document.getElementById("signupRole");
const signupSubmitBtn = document.getElementById("signupSubmitBtn");
const signupAlert = document.getElementById("signupAlert");
const themeSelect = document.getElementById("themeSelect");

// Display Demo Banner if running in Public Demo Mode
if (IS_DEMO && demoModeBanner) {
    demoModeBanner.style.display = "block";
}


// ================= TAB SWITCHING =================

tabLoginBtn.addEventListener("click", () => {
    tabLoginBtn.classList.add("active");
    tabSignupBtn.classList.remove("active");
    loginForm.style.display = "block";
    signupForm.style.display = "none";
});

tabSignupBtn.addEventListener("click", () => {
    tabSignupBtn.classList.add("active");
    tabLoginBtn.classList.remove("active");
    signupForm.style.display = "block";
    loginForm.style.display = "none";
});


// ================= QUICK-FILL PRECONFIGURED LOGINS =================

fillAdminBtn.addEventListener("click", () => {
    tabLoginBtn.click();
    loginUsername.value = "admin";
    loginPassword.value = "admin123";
    loginAlert.style.display = "none";
});

fillOperatorBtn.addEventListener("click", () => {
    tabLoginBtn.click();
    loginUsername.value = "operator";
    loginPassword.value = "operator123";
    loginAlert.style.display = "none";
});


// ================= SIGN IN HANDLER =================

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginAlert.style.display = "none";
    loginSubmitBtn.disabled = true;
    loginSubmitBtn.textContent = "Authenticating...";

    const username = loginUsername.value.trim();
    const password = loginPassword.value;

    // Public Demo Mode interceptor
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const data = window.VoteGuardMock.login(username, password);
            window.location.href = data.redirect_url || (data.role === "admin" ? "admin.html" : "operator.html");
            return;
        } catch (err) {
            loginAlert.textContent = `❌ ${err.message}`;
            loginAlert.style.display = "block";
            loginSubmitBtn.disabled = false;
            loginSubmitBtn.textContent = "Sign In & Enter Dashboard →";
            return;
        }
    }

    // Full-Stack Mode: Connect to live FastAPI backend
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed. Please check your credentials.");
        }

        // Store session tokens
        sessionStorage.setItem("voteGuardToken", data.access_token);
        sessionStorage.setItem("voteGuardUser", JSON.stringify({
            username: data.username,
            full_name: data.full_name,
            role: data.role
        }));

        // Dedicated redirection based on user role
        window.location.href = data.redirect_url || (data.role === "admin" ? "admin.html" : "operator.html");

    } catch (err) {
        if (err.message && err.message.toLowerCase().includes("fetch")) {
            loginAlert.textContent = "❌ Cannot connect to backend at http://127.0.0.1:8000. Start the server by running: python main.py in backend folder.";
        } else {
            loginAlert.textContent = `❌ ${err.message}`;
        }
        loginAlert.style.display = "block";
    } finally {
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.textContent = "Sign In & Enter Dashboard →";
    }
});


// ================= SIGN UP HANDLER =================

signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    signupAlert.style.display = "none";
    signupSubmitBtn.disabled = true;
    signupSubmitBtn.textContent = "Creating Account...";

    const payload = {
        full_name: signupFullName.value.trim(),
        username: signupUsername.value.trim().toLowerCase(),
        password: signupPassword.value,
        role: signupRole.value
    };

    // Public Demo Mode interceptor
    if (IS_DEMO && window.VoteGuardMock) {
        try {
            const data = window.VoteGuardMock.signup(payload);
            window.location.href = data.redirect_url || (data.role === "admin" ? "admin.html" : "operator.html");
            return;
        } catch (err) {
            signupAlert.textContent = `❌ ${err.message}`;
            signupAlert.style.display = "block";
            signupSubmitBtn.disabled = false;
            signupSubmitBtn.textContent = "Create Account & Continue →";
            return;
        }
    }

    // Full-Stack Mode: Connect to live FastAPI backend
    try {
        const response = await fetch(`${API_BASE}/api/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to create account.");
        }

        // Store session tokens
        sessionStorage.setItem("voteGuardToken", data.access_token);
        sessionStorage.setItem("voteGuardUser", JSON.stringify({
            username: data.username,
            full_name: data.full_name,
            role: data.role
        }));

        // Dedicated redirection based on user role
        window.location.href = data.redirect_url || (data.role === "admin" ? "admin.html" : "operator.html");

    } catch (err) {
        signupAlert.textContent = `❌ ${err.message}`;
        signupAlert.style.display = "block";
    } finally {
        signupSubmitBtn.disabled = false;
        signupSubmitBtn.textContent = "Create Account & Continue →";
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

