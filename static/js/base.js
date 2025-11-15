$(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        headers: { 'X-CSRFToken': csrftoken }
    });

    $(document).on('click', '.commonFetch', function () {
        var path = $(this).data('path');
        var title = $(this).data('title');
        var text = $(this).data('text');
        $.ajax({
            type: 'POST',
            url: path,
            data: {},
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            beforeSend: function () {
                Swal.fire({
                    title: title,
                    text: text,
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
            },
            success: function (response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: response.message,
                    confirmButtonColor: '#3085d6',
                    confirmButtonText: 'OK'
                });
            },
            error: function (xhr) {
                let msg = 'Failed to fetch stock data.';
                if (xhr.responseJSON && xhr.responseJSON.details) {
                    msg += ' (' + xhr.responseJSON.details + ')';
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: msg
                });
            }
        });
    });

    $(document).on('click', '.commonFetch2', function () {
        var path = $(this).data('path');
        var title = $(this).data('title');
        var text = $(this).data('text');
        $.ajax({
            type: 'POST',
            url: path,
            data: {},
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            beforeSend: function () {
                Swal.fire({
                    title: title,
                    text: text,
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });
            },
            success: function (response) {
                const decoded = atob(response.data);
                const parsed = JSON.parse(decoded);

                const title = parsed.title || "List";
                const label = parsed.label || "name";
                let msg = `<b>${title}:</b><br>`;

                parsed.items.forEach(item => {
                    msg += `• ${item.stockName} (ID: ${item.id})<br>`;
                });

                Swal.fire({
                    title: title,
                    html: msg,
                    icon: 'info'
                });
            },
            error: function (xhr) {
                let msg = 'Failed to fetch stock data.';
                if (xhr.responseJSON && xhr.responseJSON.details) {
                    msg += ' (' + xhr.responseJSON.details + ')';
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: msg
                });
            }
        });
    });

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showFlashMessage(message, type = 'success') {
        // type can be 'success', 'danger', 'warning', 'info'
        const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
        $("#flashMessage").html(alertHtml);

        // Optional: auto-hide after 3 seconds
        setTimeout(() => {
            $(".alert").alert('close');
        }, 3000);
    }


    $(document).on('click', ".open-form-btn", function () {
        var url = $(this).data("path");
        var btnText = $(this).text();

        // Load form HTML via AJAX
        $.get(url, function (data) {
            $("#modalBody").html(data);
            $("#modalTitle").text(btnText);
            var modal = new bootstrap.Modal($("#formModal")[0]);
            modal.show();

            // Handle submit button
            $("#modalSubmit").off("click").on("click", function () {
                var form = $("#modalForm")[0]; // the form inside modal
                var formData = new FormData(form);

                $.ajax({
                    url: url,
                    method: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function (response) {
                        if (response.status === "success") {
                            modal.hide();
                            showFlashMessage("Item saved successfully!", "success");
                            location.reload();
                        } else {
                            showFlashMessage("Error!", "danger");
                            $("#modalBody").html(response);
                        }
                    },
                    error: function (xhr, status, error) {
                        showFlashMessage(error, "danger");
                    }
                });
            });
        });
    });
    $(document).on('click', '.common-get', function () {
        var url = $(this).data('path');
        $.get(url, function (data) {
            if (data.status == 'success') {
                showFlashMessage(data.message, 'success');
                location.reload();
            } else if (data.status == 'error') {
                showFlashMessage(data.message, 'danger');
            }
        });
    })
})

