
$(document).on('blur', '.editable-cell', function () {
    const cell = $(this);
    const value = cell.text().trim();
    const date = cell.data('date');
    const item = cell.data('item');
    const month = cell.data('month');
    const year = cell.data('year');
    const path = cell.data('path');
    const valueType = cell.data('valuetype');
    $.ajax({
        url: path,  // your Django URL
        type: 'POST',
        data: {
            value: value,
            date: date,
            item: item,
            month: month,
            year: year,
            valueType: valueType
        },
        success: function (resp) {
            cell.css('border', '2px solid #28a745');  // green border
            setTimeout(() => cell.css('border', ''), 1000);
            location.reload();  
        },
        error: function () {
            cell.css('border', '2px solid #dc3545');  // red border
        }
    });
});

