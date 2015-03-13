/**
 * Created by alex on 13/03/15.
 */
$(document).ready(function () {
    $('#btn_show_sync').click(function (e) {
        e.preventDefault();
        $.ajax({
            url: Urls.remotesync(),
            beforeSend: function () {
                $.isLoading({
                    text: "Sincronizando dados"
                });
            },
            success: function (data) {
                $.isLoading("hide");
                var sync_box_error = $('#sync_box_error');
                sync_box_error.hide();
                $('#sync_box').bPopup({
                    closeClass: 'sync_box_btn_close',
                    onOpen: function () {
                        var sync_box_state = $('#sync_box_state');
                        var sync_box_total = $('#sync_box_total');
                        if (data.status == true) {
                            sync_box_state.text('sucesso');
                            sync_box_total.text(data.total);
                            sync_box_error.hide();
                        } else {
                            sync_box_state.text('error');
                            sync_box_total.text(0);
                            $('#sync_box_error_message').text(data.error);
                            sync_box_error.show();
                        }
                    }
                });
            },
            error: function () {
                $.isLoading("hide");
            }
        })
    })
});
