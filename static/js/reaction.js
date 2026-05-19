document.addEventListener("DOMContentLoaded", function () {

    const submitBtn = document.getElementById("submitBtn");

    const fields = [
        document.getElementById("equation"),
        document.getElementById("description"),
        document.getElementById("temperature"),
        document.getElementById("pressure"),
        document.getElementById("result_color"),
        document.getElementById("result_color_text")
    ];

    function checkForm() {
        let allFilled = true;

        fields.forEach(f => {
            if (f && f.value.trim() === "") {
                allFilled = false;
            }
        });

        submitBtn.disabled = !allFilled;
    }

    fields.forEach(f => {
        if (f) {
            f.addEventListener("input", checkForm);
            f.addEventListener("change", checkForm);
        }
    });

    
    checkForm();

});