window.addEventListener("load", function () {
    const ctx = document.getElementById('statsChart').getContext('2d');

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