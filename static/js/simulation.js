
function formatChemicalFormulas() {
    const equationElement = document.querySelector('.equation-text');
    if (!equationElement) return;

    let text = equationElement.textContent;

    // إزالة أي LaTeX أو رموز
    text = text.replace(/\\ce\{|\}/g, '');
    text = text.replace(/\\rightarrow/g, '→');

    // تحويل الأرقام إلى sub فقط إذا كانت بعد حرف
    text = text.replace(/([A-Za-z])(\d+)/g, '$1<sub>$2</sub>');

    // تحويل (OH)2 أو أي مجموعة بين قوسين
    text = text.replace(/\(([^)]+)\)(\d+)/g, '($1)<sub>$2</sub>');

    // إضافة سهم الترسيب (↓) إذا لم يكن موجود
    text = text.replace(/AgCl/g, 'AgCl↓');

    equationElement.innerHTML = text;
}

// تنفيذ الحل البديل بعد تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {

  setTimeout(function() {
        const hasSubscript = document.querySelector('.equation-text sub');
        if (!hasSubscript) {
            formatChemicalFormulas();
        }
    }, 500);
});

