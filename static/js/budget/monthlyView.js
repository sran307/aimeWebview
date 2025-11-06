
$(document).on('blur', '.editable-cell', function() {
    const cell = $(this);
    const value = cell.text().trim();
    const date = cell.data('date');
    const item = cell.data('item');
    const month = cell.data('month');
    const year = cell.data('year');
    const path = cell.data('path');
    $.ajax({
        url: path,  // your Django URL
        type: 'POST',
        data: {
            value: value,
            date: date,
            item: item,
            month: month,
            year: year
        },
        success: function(resp) {
            cell.css('border', '#28a745'); // green on success
            setTimeout(() => cell.css('border', ''), 1000);
        },
        error: function() {
            cell.css('border', '#dc3545'); // red on error
        }
    });
});

