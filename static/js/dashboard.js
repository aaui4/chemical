window.addEventListener("load", function () {
    const ctx = document.getElementById('reactionsChart').getContext('2d');

    new Chart(ctx, {
    type: 'line',
    data: {
        labels: window.chartLabels,
        datasets: [{
            label: 'Number of Experiments',
            data: window.chartData
        }]
    },
    options: {
        scales: {
            x: {
                ticks: {
                    color: '#ffffff' // لون التواريخ
                }
            },
            y: {
                ticks: {
                    color: '#ffffff' // (اختياري) أرقام المحور Y
                }
            }
        }
    }
});
});

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
