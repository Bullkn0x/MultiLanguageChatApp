//CREATE MODAL
var $createSubmit = $("#createServerSubmit");
var $serverName = $("#serverName");


// var $discoverModal = $("#discoverModal");
// var $createModal = $("#newServerModal");
// var $leaveModal = $("#leaveConfirmModal");
var $serverOptionModal = $("serverOptionModal");
$createBtn.on('click', function () {
    $createModal.css('display', "flex");
});


//As Soon as user click submit, exit the modal and submit.
$createSubmit.click(function () {
    if ($serverName.val()) {
        // $createModal.hide();
        // $serverName.clear();
        var room_name = $serverName.val();
        var public = $('#_checkbox').is(":not(:checked)")
        socket.emit('create server', {
            room_name: room_name,
            public: public
        });
        $createModal.hide();
    }

});

$serverName.keypress(function (e) {
    if (e.which == 13) {
        $createSubmit.click();
    }
});

// SEARCH MODAL
var $options = $('.search-options');



// When the user clicks off the modal, close it
$(".modal").click(function (e) {
    if (e.target == e.currentTarget) {
        $(this).hide();
    }
});

$leaveModal.on('click', '#confirmLeave', function () {
    let room_id = focusedServer.attr('room_id')
    focusedServer.remove();
    $('.serverList').children('[room_id=' +room_id + ']').remove();
    socket.emit('user update', {
        operation: 'leave_server',
        room_id: parseInt(room_id)
    })
});
