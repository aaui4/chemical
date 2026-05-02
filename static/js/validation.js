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

// فتح وإغلاق المودال
function openPasswordModal() {
    document.getElementById("passwordModal").style.display = "flex";
}

function closePasswordModal() {
    document.getElementById("passwordModal").style.display = "none";
    // تنظيف النموذج عند الإغلاق
    document.getElementById("changePasswordForm").reset();
    // إخفاء رسائل الخطأ
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
}

// إغلاق المودال عند النقر خارج المحتوى
window.onclick = function(event) {
    let modal = document.getElementById("passwordModal");
    if (event.target == modal) {
        closePasswordModal();
    }
}

// التحقق من صحة كلمة المرور قبل الإرسال
document.getElementById("changePasswordForm").addEventListener("submit", function(event) {
    let isValid = true;
    
    // تنظيف الرسائل السابقة
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    
    const currentPassword = document.getElementById("current_password").value;
    const newPassword = document.getElementById("new_password").value;
    const confirmPassword = document.getElementById("confirm_password").value;
    
    // التحقق من كلمة المرور الحالية
    if (!currentPassword) {
        document.getElementById("current-password-msg").textContent = "{{ _('Current password is required') }}";
        isValid = false;
    }
    
    // التحقق من طول كلمة المرور الجديدة
    if (newPassword.length < 6) {
        document.getElementById("new-password-msg").textContent = "{{ _('Password must be at least 6 characters') }}";
        isValid = false;
    }
    
    // التحقق من أن كلمة المرور تحتوي فقط على حروف وأرقام
    const passwordRegex = /^[A-Za-z0-9]+$/;
    if (newPassword && !passwordRegex.test(newPassword)) {
        document.getElementById("new-password-msg").textContent = "{{ _('Password can only contain letters and numbers') }}";
        isValid = false;
    }
    
    // التحقق من تطابق كلمتي المرور
    if (newPassword !== confirmPassword) {
        document.getElementById("confirm-password-msg").textContent = "{{ _('Passwords do not match') }}";
        isValid = false;
    }
    
    if (!isValid) {
        event.preventDefault();
    }
});

function showNotification(message, type) {
    // إنشاء عنصر الإشعار
    let notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class='bx ${type === 'success' ? 'bx-check-circle' : 'bx-error-circle'}'></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // إظهار الإشعار
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // إخفاء الإشعار بعد 3 ثواني
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function togglePassword(inputId, icon) {
    let input = document.getElementById(inputId);

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bx-show");
        icon.classList.add("bx-hide");
    } else {
        input.type = "password";
        icon.classList.remove("bx-hide");
        icon.classList.add("bx-show");
    }
}