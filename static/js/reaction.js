 // تعيين ألوان الخلفية لكل مربع لون
    document.addEventListener('DOMContentLoaded', function() {
        var rows = document.querySelectorAll('.pending-table tbody tr');
        rows.forEach(function(row, index) {
            var color = row.getAttribute('data-color');
            var colorPreview = document.getElementById('color-' + (index + 1));
            if (colorPreview && color) {
                colorPreview.style.backgroundColor = color;
            }
        });
    });