
    function filterTable() {
        const input = document.getElementById('searchInput');
        const typeFilter = document.getElementById('typeFilter');
        const filter = input.value.toLowerCase();
        const type = typeFilter.value.toLowerCase();
        const table = document.getElementById('historyTable');
        const tr = table.getElementsByTagName('tr');
        
        // للتأكد من عمل البحث (يمكنك مشاهدتها في Console)
        console.log("🔍 Searching for:", filter);
        console.log("📋 Filter type:", type);
        
        let visibleCount = 0;
        
        for (let i = 1; i < tr.length; i++) {
            // نتأكد أن هذا الصف ليس صف "No data"
            if (tr[i].classList.contains('no-data')) continue;
            
            const tdEquation = tr[i].getElementsByTagName('td')[2];
            const tdColor = tr[i].getElementsByTagName('td')[4];
            const tdType = tr[i].getElementsByTagName('td')[5];
            
            if (tdEquation && tdColor && tdType) {
                const equationText = tdEquation.textContent || tdEquation.innerText;
                const colorText = tdColor.textContent || tdColor.innerText;
                const typeText = tdType.textContent || tdType.innerText;
                
                const matchesSearch = equationText.toLowerCase().includes(filter) || 
                                     colorText.toLowerCase().includes(filter);
                const matchesType = type === 'all' || typeText.toLowerCase().includes(type);
                
                if (matchesSearch && matchesType) {
                    tr[i].style.display = '';
                    visibleCount++;
                } else {
                    tr[i].style.display = 'none';
                }
            }
        }
        
        console.log(" Visible rows:", visibleCount);
    }
    
    function clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('typeFilter').value = 'all';
        filterTable();
        console.log(" Filters cleared");
    }
    
    function viewSimulation(id) {
        window.location.href = `/simulation/view/${id}`;
    }
    
    function deleteSimulation(id) {
        if (confirm('Are you sure you want to delete this simulation?')) {
            fetch(`/simulation/delete/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error deleting simulation');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error deleting simulation');
            });
        }
    }
    
    function exportToCSV() {
        const table = document.getElementById('historyTable');
        const rows = table.querySelectorAll('tr');
        let csv = [];
        
        for (let i = 0; i < rows.length; i++) {
            const row = [], cols = rows[i].querySelectorAll('td, th');
            
            for (let j = 0; j < cols.length - 1; j++) {
                let data = cols[j].innerText.replace(/,/g, ';');
                row.push('"' + data + '"');
            }
            
            csv.push(row.join(','));
        }
        
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulation_history.csv';
        a.click();
    }
    
    function exportToJSON() {
        const table = document.getElementById('historyTable');
        const rows = table.querySelectorAll('tbody tr');
        const data = [];
        
        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].querySelectorAll('td');
            if (cells.length > 0 && !cells[0].classList.contains('no-data')) {
                data.push({
                    id: cells[0].innerText.replace('#', ''),
                    date: cells[1].innerText,
                    equation: cells[2].innerText,
                    temperature: cells[3].innerText,
                    color: cells[4].innerText.trim(),
                    type: cells[5].innerText,
                    products: cells[6].innerText
                });
            }
        }
        
        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulation_history.json';
        a.click();
    }
    
    function printTable() {
        const table = document.getElementById('historyTable');
        const newWindow = window.open('', '_blank');
        newWindow.document.write(`
            <html>
                <head>
                    <title>Simulation History</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        table { border-collapse: collapse; width: 100%; }
                        th { background: #34495e; color: white; padding: 10px; }
                        td { padding: 8px; border-bottom: 1px solid #ddd; }
                        .color-dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-left: 5px; }
                    </style>
                </head>
                <body>
                    <h1>Simulation History</h1>
                    ${table.outerHTML}
                </body>
            </html>
        `);
        newWindow.document.close();
        newWindow.print();
    }

    // تشغيل البحث عند تحميل الصفحة (للتأكد)
    window.onload = function() {
        console.log(" History page loaded, search is ready");
    };
