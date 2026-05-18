// =======================
// Wait DOM ready
// =======================
document.addEventListener("DOMContentLoaded", () => {


// =======================
// عناصر الصفحة
// =======================
const usernameInput = document.getElementById("username");
const usernameMsg = document.getElementById("username-msg");

const emailInput = document.getElementById("email");
const emailMsg = document.getElementById("email-msg");

const passwordInput = document.getElementById("password");
const passwordMsg = document.getElementById("password-msg");

const firstNameInput = document.getElementById("first_name");
const firstNameMsg = document.getElementById("first-name-msg");

const institutionInput = document.getElementById("institution");
const institutionMsg = document.getElementById("institution-msg");


// =======================
// Username validation
// =======================
if (usernameInput && usernameMsg) {
    usernameInput.addEventListener("input", () => {

        const username = usernameInput.value.trim();

        if (!username) {
            usernameMsg.textContent = "";
            return;
        }

        if (!/^[\x00-\x7F]*$/.test(username)) {
            usernameMsg.textContent = "Username must contain only Latin letters.";
            usernameMsg.style.color = "red";
            return;
        }

        if (!/^[A-Za-z0-9_]{4,8}$/.test(username)) {
            usernameMsg.textContent = "4-8 chars (letters, numbers, _)";
            usernameMsg.style.color = "red";
            return;
        }

        fetch("/check-username", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                usernameMsg.textContent = "Username already exists";
                usernameMsg.style.color = "red";
            } else {
                usernameMsg.textContent = "Available ✔";
                usernameMsg.style.color = "green";
            }
        });
    });
}


// =======================
// Email validation
// =======================
if (emailInput && emailMsg) {
    emailInput.addEventListener("input", () => {

        const email = emailInput.value.trim();

        if (!email) {
            emailMsg.textContent = "";
            return;
        }

        const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;

        if (!emailRegex.test(email)) {
            emailMsg.textContent = "Invalid email format";
            emailMsg.style.color = "red";
            return;
        }

        fetch("/check-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                emailMsg.textContent = "Email already used";
                emailMsg.style.color = "red";
            } else {
                emailMsg.textContent = "Available ✔";
                emailMsg.style.color = "green";
            }
        });
    });
}


// =======================
// Password validation
// =======================
if (passwordInput && passwordMsg) {
    passwordInput.addEventListener("input", () => {

        const password = passwordInput.value.trim();

        if (!password) {
            passwordMsg.textContent = "";
            return;
        }

        if (password.length < 6) {
            passwordMsg.textContent = "Min 6 characters";
            passwordMsg.style.color = "red";
            return;
        }

        if (!/^[A-Za-z0-9]+$/.test(password)) {
            passwordMsg.textContent = "Letters & numbers only";
            passwordMsg.style.color = "red";
            return;
        }

        passwordMsg.textContent = "Valid ✔";
        passwordMsg.style.color = "green";
    });
}


// =======================
// First Name validation
// =======================
if (firstNameInput && firstNameMsg) {

    firstNameInput.addEventListener("input", () => {

        const value = firstNameInput.value.trim();

        const regex = /^[A-Za-z]{3,9}$/;

        if (!value) {
            firstNameMsg.textContent = "First name required";
            firstNameMsg.style.color = "red";
        }

        else if (!regex.test(value)) {
            firstNameMsg.textContent = "Only letters (3-9 chars)";
            firstNameMsg.style.color = "red";
        }

        else {
            firstNameMsg.textContent = "Valid ✔";
            firstNameMsg.style.color = "green";
        }
    });
}



// =======================
// Password Modal
// =======================
window.openPasswordModal = function () {
    document.getElementById("passwordModal").style.display = "flex";
};

window.closePasswordModal = function () {
    document.getElementById("passwordModal").style.display = "none";
    document.getElementById("changePasswordForm")?.reset();
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
};


// =======================
// Close modal outside click
// =======================
window.onclick = function (event) {
    const modal = document.getElementById("passwordModal");
    if (event.target === modal) {
        closePasswordModal();
    }
};


// =======================
// Change password validation
// =======================
const changePasswordForm = document.getElementById("changePasswordForm");

if (changePasswordForm) {
    changePasswordForm.addEventListener("submit", function (event) {

        let isValid = true;

        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');

        const currentPassword = document.getElementById("current_password")?.value;
        const newPassword = document.getElementById("new_password")?.value;
        const confirmPassword = document.getElementById("confirm_password")?.value;

        if (!currentPassword) {
            document.getElementById("current-password-msg").textContent = "Required";
            isValid = false;
        }

        if (newPassword.length < 6) {
            document.getElementById("new-password-msg").textContent = "Min 6 chars";
            isValid = false;
        }

        const passwordRegex = /^[A-Za-z0-9]+$/;
        if (newPassword && !passwordRegex.test(newPassword)) {
            document.getElementById("new-password-msg").textContent = "Letters/numbers only";
            isValid = false;
        }

        if (newPassword !== confirmPassword) {
            document.getElementById("confirm-password-msg").textContent = "Not matching";
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}


if (institutionInput) {
    institutionInput.addEventListener("input", () => {

        const value = institutionInput.value.trim();

        if (!value) {
            institutionMsg.textContent = "";
            return;
        }

        // فقط حروف + فراغات + أرقام
        if (!/^[A-Za-z0-9\s]+$/.test(value)) {
            institutionMsg.textContent = "Only letters, spaces, and numbers allowed";
            institutionMsg.style.color = "red";
            return;
        }

        // استخراج الكلمات
        const words = value.split(/\s+/).filter(w => w.length > 0);

        if (words.length < 3 || words.length > 6) {
            institutionMsg.textContent = "Must be between 3 and 6 words";
            institutionMsg.style.color = "red";
            return;
        }

        // التحقق من الأرقام: لازم تكون فقط 4 أرقام (سنة مثل 2024)
        const numbers = value.match(/\d+/g);

        if (numbers) {
            for (let num of numbers) {
                if (!/^\d{4}$/.test(num)) {
                    institutionMsg.textContent = "Only 4-digit numbers allowed (e.g. 2024)";
                    institutionMsg.style.color = "red";
                    return;
                }
            }
        }

        institutionMsg.textContent = "Valid institution ✔";
        institutionMsg.style.color = "green";
    });
}


// =======================
// Toggle password visibility
// =======================
window.togglePassword = function (inputId, icon) {
    const input = document.getElementById(inputId);

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bx-show");
        icon.classList.add("bx-hide");
    } else {
        input.type = "password";
        icon.classList.remove("bx-hide");
        icon.classList.add("bx-show");
    }
};


// =======================
// Notification system
// =======================
window.showNotification = function (message, type) {

    let notification = document.createElement("div");
    notification.className = `notification notification-${type}`;

    notification.innerHTML = `
        <i class='bx ${type === "success" ? "bx-check-circle" : "bx-error-circle"}'></i>
        <span>${message}</span>
    `;

    document.body.appendChild(notification);

    setTimeout(() => notification.classList.add("show"), 100);

    setTimeout(() => {
        notification.classList.remove("show");
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};


});