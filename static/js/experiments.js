

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


    function openModal() {
        var modal = document.getElementById('modal');
        if (modal) modal.style.display = 'flex';
    }

    function closeModal() {
        var modal = document.getElementById('modal');
        if (modal) modal.style.display = 'none';
    }

    function openEditModal(id, equation) {
        var modal = document.getElementById('editModal');
        var editEquation = document.getElementById('editEquation');
        var editForm = document.getElementById('editForm');
        
        if (modal && editEquation && editForm) {
            editEquation.value = equation;
            editForm.action = '/admin/update_reaction/' + id;
            modal.style.display = 'flex';
        }
    }

    function closeEditModal() {
        var modal = document.getElementById('editModal');
        if (modal) modal.style.display = 'none';
    }

    window.onclick = function(event) {
        var addModal = document.getElementById('modal');
        var editModal = document.getElementById('editModal');
        if (event.target == addModal) closeModal();
        if (event.target == editModal) closeEditModal();
    }