$(function () {

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
                // Decode the base64 encoded data
                const decoded = atob(response.data);
                const parsedData = JSON.parse(decoded);

                // Now you have: parsedData.sectors = [{sector: 'IT'}, {sector: 'Finance'}, ...]

                let msg = '<b>Trending Sectors:</b><br>';
                parsedData.sectors.forEach(s => {
                    msg += `• ${s.sector}<br>`;
                });

                Swal.fire({
                    title: 'Sectors List',
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


})