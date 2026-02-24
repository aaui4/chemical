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
            usernameMsg.textContent = "اسم المستخدم يجب أن يحتوي على حروف لاتينية فقط";
            usernameMsg.style.color = "red";
            return;
        }

        // الطول والصيغة
        if (!/^[A-Za-z0-9_]{4,8}$/.test(username)) {
            usernameMsg.textContent = "بين 4 و 8 أحرف (حروف/أرقام/_) فقط";
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
                usernameMsg.textContent = "اسم المستخدم مستخدم بالفعل";
                usernameMsg.style.color = "red";
            } else {
                usernameMsg.textContent = "اسم المستخدم متاح ✔";
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
            emailMsg.textContent = "صيغة البريد الإلكتروني غير صحيحة";
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
                emailMsg.textContent = "هذا البريد مستخدم بالفعل";
                emailMsg.style.color = "red";
            } else {
                emailMsg.textContent = "البريد متاح ✔";
                emailMsg.style.color = "green";
            }
        })
        .catch(err => console.log(err));
    });
}

// ====== تحقق كلمة المرور ======
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
            passwordMsg.textContent = "كلمة المرور يجب أن تكون 6 أحرف على الأقل";
            passwordMsg.style.color = "red";
            return;
        }

        // فقط أحرف وأرقام
        if (!/^[A-Za-z0-9]+$/.test(password)) {
            passwordMsg.textContent = "كلمة المرور يمكن أن تحتوي على أحرف وأرقام فقط";
            passwordMsg.style.color = "red";
            return;
        }

        passwordMsg.textContent = "كلمة المرور صالحة ✔";
        passwordMsg.style.color = "green";
    });
}
