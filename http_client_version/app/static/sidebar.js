var $serverList = $('.serverList');
// Hide submenus
$('#body-row .collapse').collapse('hide');

// Collapse/Expand icon
$('#collapse-icon').addClass('fa-angle-double-left');

// Collapse click
$('[data-toggle=sidebar-colapse]').click(function () {
    SidebarCollapse();
});




// $allserver.mouseover(function () {
//     $(this).mousedown(function (e) {
//         if (e.which == 3) {
//             alert($(this).text());
//             alert($(this).attr('room_id'));
//         }
//     });
// });


function SidebarCollapse() {
    $('.menu-collapsed').toggleClass('d-none');
    $('.sidebar-submenu').toggleClass('d-none');
    $('.submenu-icon').toggleClass('d-none');
    $('#sidebar-container').toggleClass('sidebar-expanded sidebar-collapsed');

    // Treating d-flex/d-none on separators with title
    var SeparatorTitle = $('.sidebar-separator-title');
    if (SeparatorTitle.hasClass('d-flex')) {
        SeparatorTitle.removeClass('d-flex');
    } else {
        SeparatorTitle.addClass('d-flex');
    }

    // Collapse/Expand icon
    $('#collapse-icon').toggleClass('fa-angle-double-left fa-angle-double-right');
}

socket.on('new server', function (server) {

    var $imgDiv = $('<img />').attr("src", server.room_logo_url).css({
        "max-height": "133%",
        "border-radius": "16%",
        "margin-right": "10px",
    });

    var $serverNameDiv = $('<span class="menu-collapsed"/>')
        .text(server.room_name);
    var $tableCellDiv = $('<a href="#" class="list-group-item list-group-item-action bg-dark">').attr('room_id', server.room_id).append($imgDiv).append($serverNameDiv);
    $serverList.append($tableCellDiv);
    $tableCellDiv.click();

});