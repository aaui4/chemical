
// Edit Modal
function openEditElementModal(id, name, symbol, state, color) {
    document.getElementById("editElementModal").style.display = "flex";

    document.getElementById("editName").value = name;
    document.getElementById("editSymbol").value = symbol;
    document.getElementById("editState").value = state;
    document.getElementById("editColor").value = color;

    // تحديث رابط النموذج
    const form = document.getElementById("editElementForm");
    form.action = "/admin/elements/" + id;
    
    // تخزين ID العنصر الحالي
    form.dataset.elementId = id;
}

function closeEditElementModal() {
    document.getElementById("editElementModal").style.display = "none";
}

// تنفيذ التحديث بدون reload
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editElementForm");

    if (form) {
        form.addEventListener("submit", async function(e) {
            e.preventDefault();

            const url = form.action;
            const formData = new FormData(form);

            // إظهار رسالة جاري التحميل
            const updateBtn = form.querySelector('button[type="submit"]');
            const originalText = updateBtn.textContent;
            updateBtn.textContent = "Updating...";
            updateBtn.disabled = true;

            try {
                const response = await fetch(url, {
                    method: "POST",
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                // قراءة الاستجابة كنص أولاً للتأكد
                const responseText = await response.text();
                console.log("Response:", responseText);
                
                // محاولة تحويلها إلى JSON
                let data;
                try {
                    data = JSON.parse(responseText);
                } catch (e) {
                    console.error("Not JSON response:", responseText);
                    throw new Error("Server returned invalid response");
                }
                
                if (data.success) {
                    // البحث عن الصف بواسطة data-id
                    const elementId = form.dataset.elementId;
                    const row = document.querySelector(`tr[data-id='${elementId}']`);
                    
                    if (row) {
                        // تحديث الخلايا
                        const nameCell = row.querySelector('.name');
                        const symbolCell = row.querySelector('.element-symbol');
                        const stateCell = row.querySelector('.state');
                        const colorCell = row.querySelector('.color');
                        
                        if (nameCell) nameCell.textContent = data.name;
                        if (stateCell) stateCell.textContent = data.state;
                        if (colorCell) colorCell.textContent = data.color;
                        
                        if (symbolCell) {
                            symbolCell.innerHTML = data.symbol.replace(/(\d+)/g, "<sub>$1</sub>");
                        }
                        
                        // إظهار رسالة نجاح
                        alert("Element updated successfully!");
                        closeEditElementModal();
                    } else {
                        console.error("Row not found for id:", elementId);
                        alert("Element updated but couldn't find row to update. Please refresh the page.");
                        location.reload(); // إعادة تحميل الصفحة كحل بديل
                    }
                } else {
                    alert("Error: " + (data.error || "Unknown error"));
                }
            } catch (err) {
                console.error("Error:", err);
                alert("An error occurred: " + err.message + "\nPlease check the console for details.");
            } finally {
                updateBtn.textContent = originalText;
                updateBtn.disabled = false;
            }
        });
    }
});

function formatChemicalFormulas() {
    const elements = document.querySelectorAll('.element-symbol');

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

function openElementModal() {
    document.getElementById("elementModal").style.display = "flex";
}

function closeElementModal() {
    document.getElementById("elementModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    formatChemicalFormulas();
});
