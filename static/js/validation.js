// ====== عناصر الصفحة ======
const usernameInput = document.getElementById("username");
const usernameMsg = document.getElementById("username-msg");

const emailInput = document.getElementById("email");
const emailMsg = document.getElementById("email-msg");

const passwordInput = document.getElementById("password");
const passwordMsg = document.getElementById("password-msg");

// ====== تحقق اسم المستخدم ======
if (usernameInput) {
    usernameInput.addEventListener("input", () => {
        const username = usernameInput.value.trim();

        if (!username) {
            usernameMsg.textContent = "";
            return;
        }

        // منع الحروف العربية
        if (!/^[\x00-\x7F]*$/.test(username)) {
            usernameMsg.textContent ="Username must contain only Latin letters.";
            usernameMsg.style.color = "red";
            return;
        }

        // الطول والصيغة
        if (!/^[A-Za-z0-9_]{4,8}$/.test(username)) {
            usernameMsg.textContent = "Between 4 and 8 characters (a..z/A..z,1..9,_)";
            usernameMsg.style.color = "red";
            return;
        }

        // إذا الصيغة صحيحة → تحقق التوفر عبر AJAX
        fetch("/check-username", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                usernameMsg.textContent = "Username is already in use";
                usernameMsg.style.color = "red";
            } else {
                usernameMsg.textContent = " Username is available ✔";
                usernameMsg.style.color = "green";
            }
        })
        .catch(err => console.log(err));
    });
}


// ====== تحقق البريد الإلكتروني ======
if (emailInput) {
    emailInput.addEventListener("input", () => {
        const email = emailInput.value.trim();

        if (!email) {
            emailMsg.textContent = "";
            return;
        }

        // تحقق صيغة البريد الإلكتروني
        const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
        if (!emailRegex.test(email)) {
            emailMsg.textContent = "The email format is invalid";
            emailMsg.style.color = "red";
            return;
        }

        // التوفر عبر AJAX
        fetch("/check-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        })
        .then(res => res.json())
        .then(data => {
            if (data.exists) {
                emailMsg.textContent = "This email is already in use";
                emailMsg.style.color = "red";
            } else {
                emailMsg.textContent = "Email is available ✔";
                emailMsg.style.color = "green";
            }
        })
        .catch(err => console.log(err));
    });
}

// ====== تحقق كلمة المرور ======
if (passwordInput) {
    passwordInput.addEventListener("input", () => {
        const password = passwordInput.value.trim();

        if (!password) {
            passwordMsg.textContent = "";
            return;
        }

        // الطول: أكثر من 5 أحرف/أرقام
        if (password.length < 6) {
            passwordMsg.textContent = "Password must be at least 6 characters long";
            passwordMsg.style.color = "red";
            return;
        }

        // فقط أحرف وأرقام
        if (!/^[A-Za-z0-9]+$/.test(password)) {
            passwordMsg.textContent = "Password can contain only letters and numbers.";
            passwordMsg.style.color = "red";
            return;
        }

        passwordMsg.textContent = " Password is valid ✔";
        passwordMsg.style.color = "green";
    });
}
