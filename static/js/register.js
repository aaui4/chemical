let emailTimer = null;

emailInput.addEventListener("input", () => {
  clearTimeout(emailTimer);

  emailTimer = setTimeout(() => {
    checkEmailExists();
  }, 500); // ننتظر المستخدم يكمل الكتابة
});

function checkEmailExists() {
  const email = emailInput.value.trim();

  if (email === "" || !validateEmailFormat(email)) return;

  fetch("/check-email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: email }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.exists) {
        emailError.textContent = "هذا البريد الإلكتروني مستعمل";
      } else {
        emailError.textContent = "";
      }
    });
}
