const usernameInput = document.getElementById("username");
const usernameMsg = document.getElementById("username-msg");

if (usernameInput) {
    usernameInput.addEventListener("input", () => {
        const username = usernameInput.value.trim();

        if (!username) {
            usernameMsg.textContent = "";
            return;
        }

        fetch("/check-username", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username: username })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                usernameMsg.textContent = "اسم المستخدم مستخدم بالفعل";
                usernameMsg.style.color = "red";
            } else {
                usernameMsg.textContent = "اسم المستخدم متاح";
                usernameMsg.style.color = "green";
            }
        })
        .catch(err => console.log(err));
    });
}
const emailInput = document.getElementById("email");
const emailMsg = document.getElementById("email-msg");

if (emailInput) {
    emailInput.addEventListener("input", () => {
        const email = emailInput.value.trim();

        if (!email) {
            emailMsg.textContent = "";
            return;
        }

        fetch("/check-email", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                emailMsg.textContent = "هذا البريد مستخدم بالفعل";
                emailMsg.style.color = "red";
            } else {
                emailMsg.textContent = "البريد متاح";
                emailMsg.style.color = "green";
            }
        })
        .catch(err => console.log(err));
    });
}
