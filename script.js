

/* ====== REGISTERED VOTERS =======*/

const defaultVoters = [
    {
        voterId: "V001",
        name: "Rahul Sharma",
        rfid: "RFID001",
        status: "Not Voted"
    },
    {
        voterId: "V002",
        name: "Aman Patel",
        rfid: "RFID002",
        status: "Voted"
    },
    {
        voterId: "V003",
        name: "Priya Shah",
        rfid: "RFID003",
        status: "Not Voted"
    },
    {
        voterId: "V004",
        name: "Arjun Mehta",
        rfid: "RFID004",
        status: "Not Voted"
    },
    {
        voterId: "V005",
        name: "Neha Patel",
        rfid: "RFID005",
        status: "Not Voted"
    },
    {
        voterId: "V006",
        name: "Atik Ansari",
        rfid: "RFID006",
        status: "Voted"
    },
    
];


/* ================= LOAD VOTER DATA ================= */

let voters = JSON.parse(
    localStorage.getItem("voteGuardVoters")
);

if (!voters) {
    voters = JSON.parse(
        JSON.stringify(defaultVoters)
    );

    localStorage.setItem(
        "voteGuardVoters",
        JSON.stringify(voters)
    );
}


/* ================= FRAUD ATTEMPTS ================= */

let fraudAttempts =
    parseInt(localStorage.getItem("voteGuardFraudAttempts")) || 0;


/* ================= ACTIVITY DATA ================= */

let activities =
    JSON.parse(localStorage.getItem("voteGuardActivities")) || [];


/* ================= DOM ELEMENTS ================= */

const voterInput = document.getElementById("voterInput");

const verifyBtn = document.getElementById("verifyBtn");

const verificationMessage =
    document.getElementById("verificationMessage");

const totalVoters =
    document.getElementById("totalVoters");

const votesRecorded =
    document.getElementById("votesRecorded");

const pendingVotes =
    document.getElementById("pendingVotes");

const fraudAttemptsElement =
    document.getElementById("fraudAttempts");

const activityTable =
    document.getElementById("activityTable");

const resetBtn =
    document.getElementById("resetBtn");

const recordedVotersTable =
    document.getElementById("recordedVotersTable");

const recordedCount =
    document.getElementById("recordedCount");


/* ================= UPDATE DASHBOARD ================= */

/* ================= UPDATE DASHBOARD ================= */

function updateDashboard() {

    const total = voters.length;

    const voted = voters.filter(
        voter => voter.status === "Voted"
    ).length;

    const pending = total - voted;


    totalVoters.textContent = total;

    votesRecorded.textContent = voted;

    pendingVotes.textContent = pending;

    fraudAttemptsElement.textContent = fraudAttempts;


    /* Update recorded voters */

    displayRecordedVoters();
}

/* ================= SAVE DATA ================= */

function saveData() {

    localStorage.setItem(
        "voteGuardVoters",
        JSON.stringify(voters)
    );

    localStorage.setItem(
        "voteGuardFraudAttempts",
        fraudAttempts
    );

    localStorage.setItem(
        "voteGuardActivities",
        JSON.stringify(activities)
    );
}


/* ================= TIME ================= */

function getCurrentTime() {

    const now = new Date();

    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


/* ================= ADD ACTIVITY ================= */

function addActivity(
    voterId,
    name,
    rfid,
    status,
    verification
) {

    activities.unshift({

        voterId: voterId,

        name: name,

        rfid: rfid,

        status: status,

        verification: verification,

        time: getCurrentTime()
    });


    /* Keep only latest 10 records */

    if (activities.length > 10) {

        activities = activities.slice(0, 10);

    }


    saveData();

    displayActivities();
}


/* ================= DISPLAY ACTIVITIES ================= */

function displayActivities() {

    activityTable.innerHTML = "";


    if (activities.length === 0) {

        activityTable.innerHTML = `
            <tr>
                <td colspan="6" class="empty-row">
                    No verification activity yet.
                </td>
            </tr>
        `;

        return;
    }


    activities.forEach(activity => {

        const row = document.createElement("tr");


        let statusClass = "";

        if (activity.verification === "Valid") {

            statusClass = "valid-status";

        }
        else if (activity.verification === "Duplicate") {

            statusClass = "duplicate-status";

        }
        else {

            statusClass = "unregistered-status";

        }


        row.innerHTML = `

            <td>${activity.voterId}</td>

            <td>${activity.name}</td>

            <td>${activity.rfid}</td>

            <td>${activity.status}</td>

            <td>
                <span class="${statusClass}">
                    ${activity.verification}
                </span>
            </td>

            <td>${activity.time}</td>

        `;


        activityTable.appendChild(row);

    });
}


    /* ================= DISPLAY RECORDED VOTERS ================= */

/* ================= DISPLAY RECORDED VOTERS ================= */

function displayRecordedVoters() {

    const recordedVoters = voters.filter(
        voter => voter.status === "Voted"
    );


    /* Update count */

    recordedCount.textContent =
        `${recordedVoters.length} Voter${recordedVoters.length !== 1 ? "s" : ""}`;


    /* No recorded voters */

    if (recordedVoters.length === 0) {

        recordedVotersTable.innerHTML = `
            <div class="no-recorded">
                No votes recorded yet.
            </div>
        `;

        return;
    }


    /* Clear old list */

    recordedVotersTable.innerHTML = "";


    /* Display only RFID numbers */

    recordedVoters.forEach(voter => {

        const item = document.createElement("div");

        item.className = "recorded-rfid";

        item.textContent = voter.rfid;

        recordedVotersTable.appendChild(item);

    });
}

/* ================= VERIFY VOTER ================= */

function verifyVoter() {

    const input = voterInput.value.trim().toUpperCase();


    /* Empty input */

    if (input === "") {

        verificationMessage.textContent =
            "Please enter an RFID or Voter ID.";

        verificationMessage.style.color = "#d97706";

        return;
    }


    /* Find voter */

    const voter = voters.find(

        item =>
            item.rfid.toUpperCase() === input ||
            item.voterId.toUpperCase() === input

    );


    /* ================= NOT REGISTERED ================= */

    if (!voter) {

        verificationMessage.textContent =
            "❌ Voter is not registered.";

        verificationMessage.style.color = "#d64545";


        addActivity(
            "N/A",
            "Unknown Voter",
            input,
            "Rejected",
            "Not Registered"
        );


        voterInput.value = "";

        return;
    }


    /* ================= DUPLICATE VOTING ================= */

    if (voter.status === "Voted") {

        fraudAttempts++;

        verificationMessage.textContent =
            "🚨 Duplicate Voting Detected!";

        verificationMessage.style.color = "#d64545";


        addActivity(
            voter.voterId,
            voter.name,
            voter.rfid,
            voter.status,
            "Duplicate"
        );


        saveData();

        updateDashboard();

        voterInput.value = "";

        return;
    }


    /* ================= VALID VOTER ================= */

    voter.status = "Voted";


    verificationMessage.textContent =
        "✅ Voter Verified Successfully.";

    verificationMessage.style.color = "#1c9964";


    addActivity(
        voter.voterId,
        voter.name,
        voter.rfid,
        voter.status,
        "Valid"
    );


    saveData();

    updateDashboard();


    voterInput.value = "";
}


/* ================= VERIFY BUTTON ================= */

verifyBtn.addEventListener(
    "click",
    verifyVoter
);


/* ================= ENTER KEY ================= */

voterInput.addEventListener(
    "keypress",
    function(event) {

        if (event.key === "Enter") {

            verifyVoter();

        }

    }
);


/* ================= RESET DEMO ================= */

resetBtn.addEventListener(
    "click",
    function() {

        const confirmReset =
            confirm(
                "Reset Vote-Guard demo data?"
            );


        if (!confirmReset) {
            return;
        }


        voters = JSON.parse(
            JSON.stringify(defaultVoters)
        );


        fraudAttempts = 0;

        activities = [];


        saveData();

        updateDashboard();

        displayActivities();


        verificationMessage.textContent =
            "Demo data has been reset.";

        verificationMessage.style.color =
            "#2361a8";

    }
);


/* ================= INITIAL LOAD ================= */

updateDashboard();

displayActivities();