

// غلق عند الضغط خارج المودال
window.onclick = function(event) {
    let modal = document.getElementById("modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

// ===== ADD MODAL =====
function openModal() {
    document.getElementById("modal").style.display = "flex";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

// ===== EDIT MODAL =====
function openEditModal(id, equation) {
    document.getElementById("editModal").style.display = "flex";

    // حط القيمة داخل input
    document.getElementById("editEquation").value = equation;

    // عدل action تاع الفورم
    document.getElementById("editForm").action = "/admin/reaction/edit/" + id;
}

function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}

function formatChemicalFormulas() {
    const elements = document.querySelectorAll('.equation-text');

    elements.forEach(el => {
        let text = el.textContent;

        text = text.replace(/\\ce\{|\}/g, '');
        text = text.replace(/\\rightarrow/g, '→');

        text = text.replace(/([A-Za-z])(\d+)/g, '$1<sub>$2</sub>');

        text = text.replace(/\(([^)]+)\)(\d+)/g, '($1)<sub>$2</sub>');

        text = text.replace(/AgCl/g, 'AgCl↓');

        el.innerHTML = text;
    });
}

document.addEventListener("DOMContentLoaded", function () {
    formatChemicalFormulas();
});
