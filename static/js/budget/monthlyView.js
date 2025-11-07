
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
        },
        error: function () {
            cell.css('border', '2px solid #dc3545');  // red border
        }
    });
});

let currentCell = null;
let currentModal = null;

$(document).on('click', '.show-stock-name', function () {
    currentCell = $(this);
    var url = $(this).data("stockurl");
    var btnText = $(this).text();

    $.get(url, function (data) {
        $("#modalBody").html(data);
        $("#modalTitle").text(btnText);

        // create and store the modal instance once so we can hide it later
        currentModal = new bootstrap.Modal($('#formModal')[0]);
        currentModal.show();

        $("#modalBody .select-stock").select2({
            width: '100%',
            dropdownParent: $('#formModal')
        });
    });
});

$(document).on('change', '.select-stock', function () {
    var value = $(this).val();

    if (currentCell) {
        currentCell.text(value);
        currentCell.trigger('blur');

        if (currentModal) {
            currentModal.hide(); // hides the modal instance we created earlier
            currentModal = null;
        }
    }
});

