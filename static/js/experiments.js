// =========================
// ADD MODAL
// =========================
function openModal() {
    const modal = document.getElementById("addModal");
    if (modal) modal.style.display = "flex";
}

function closeModal() {
    const modal = document.getElementById("addModal");
    if (modal) modal.style.display = "none";
}



// =========================
// CLOSE ON OUTSIDE CLICK
// =========================
window.onclick = function(event) {
    const addModal = document.getElementById("addModal");
    const editModal = document.getElementById("editModal");

    if (event.target === addModal) {
        closeModal();
    }

    if (event.target === editModal) {
        closeEditModal();
    }
};

// =========================
// FORMAT CHEMICAL FORMULAS
// =========================
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