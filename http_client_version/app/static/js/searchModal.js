$(document).ready(function () {



    // mode of form elements changes on input
    $("#search-input").on('input', function () {
        if (isEmpty($("#search-input").val())) {
            inputInactive();
        } else {
            inputActive();
            console.log('typing');
        }
    });


    // main search functionality
    $("#search-btn").on("click", function (e) {
        e.preventDefault();
        clearCurrentCards();
        searchServers($("#search-input").val());
        $("#search-clear").focus();
    });

    // bind input cancel functionality to click
    $("#search-clear").on("click", function () {
        cancelInput();
    });

    // go back to main modal page on back click 
    $("#back-btn").on("click", function () {
        showViewInitial();
        $('#search-container').addClass('flex-column');
        $('.search-options').show();
        $('#back-btn').hide();

    });

    // bind input cancel functionality to escape key press
    $("#search-form").keyup(function (e) {
        if (e.keyCode == 27) {
            cancelInput();
            $('#search-container').addClass('flex-column');
            $('.search-options').show();
            $('#back-btn').hide();

        }
    });


});



// initialise site view
function cancelInput() {
    clearInputField();
    showViewInitial();
    inputInactive();
    $("#search-input").focus();
}

function isEmpty(value) {
    return 0 === value.length;
}

function inputInactive() {
    $("#search-form").removeClass("hasInput");
}

function inputActive() {
    $("#search-form").addClass("hasInput");
}

function clearCurrentCards() {
    $("#cards").empty();
}

function clearInputField() {
    $("#search-input").val('');
}

function showViewInitial() {
    $("#container").removeClass("view-results");
    $("#container").addClass("view-initial");
}

function showViewResults() {
    $("#container").removeClass("view-initial");
    $("#container").addClass("view-results");
}


$('#searchTopServers').on('click', function () {
    socket.emit('query servers');
    $('#back-btn').show();
    $('#search-container').removeClass('flex-column');
    $('.search-options').hide();
    showViewResults();
})

function searchServers(searchTerm) {
    if (isEmpty(searchTerm)) {
        console.log('DO SOMETHING WHEN EMPTY');
    } else {
        getSearchResults(searchTerm);
        $('#back-btn').show();
        $('#search-container').removeClass('flex-column');
        $('.search-options').hide();
        showViewResults();
    }
}



// Query servers with search term through socket
function getSearchResults(searchTerm) {
    socket.emit('query servers', searchTerm);


}

// Populate the modal on Click
socket.on('query servers', function (search_data) {
    $("#cards").html('');
    var servers = search_data.servers;
    if (servers.length) {
        servers.forEach(function (server) {
            $("#cards").append(makeServerCard(server));

        });
        // manually set height of card images, since the width is already known
    } else {
        $("#cards").append(encapsulate("No results found", "p", ""));
    }


    // When user clicks server card submit button 

    $(".button-wrapperSub").on('click', function (e) {
        if ($(this).not(".checked")) {
            $(this).addClass("checked");
            setTimeout(function () {
                var $card = $(e.target).closest('.card')
                $card.addClass('animated fadeOut');
                setTimeout(function () {
                    $card.remove()
                }, 2000);
                $(this).removeClass("checked");
            }, 5000);
        }

    });
    $(".card").hover(function () {
        console.log($(this).children('.button-wrapperSub').addClass('animated slideInRight fastest').show());
    }, function () {
        if (!$(this).children('.button-wrapperSub').hasClass("checked")) {
            $(this).children('.button-wrapperSub').hide();
        }
    });




});
// Build cards elements from 'search results' array
function makeServerCard(server) {
    var buttonDiv = '<div class="button-wrapperSub">' +
        '<a class="submit" href="#">Join</a>' +
        '<div class="loader-wrapper">' +
        '<span class="loader yellow"></span>' +
        '<span class="loader pink"></span></div>' +
        '<span class="loader orange"></span>' +
        '<div class="check-wrapper">' +
        '<svg version="1.1" width="65px" height="38px" viewBox="0 0 64.5 37.4">' +
        '<polyline class="check" points="5,13 21.8,32.4 59.5,5 " /></svg></div></div>'

    var $serverCard = $('<div/>').addClass('flex-col card hvr-glow').attr('room_id', server.room_id).append(
        $('<div/>').addClass('card-image').append(
            $('<img/>').attr({
                'src': server.room_logo_url || 'http://d1cpyz6yyb1kha.cloudfront.net/59c06463b972775e7c31ebc446d11919.png?size=128',
                'alt': 'Server image for' + server.room_name
            })
        ),
        $('<div/>').addClass('flex card-title').append(
            $('<h2/>').text(server.room_name)
        ),
        $('<div/>').addClass('flex card-actions').append(
            $('<a/>').text('More Info')
        ),
        buttonDiv
    );
    return $serverCard
}





// Socket Events
// when a user clicks on a server card 

$('#cards').on('click', 'div.card', function () {
    console.log('this is working');
    var server_id = $(this).attr('room_id');
    socket.emit('add server', { server_id: server_id });
    
    
    // refresh the server list with the new server
    var $serverList = $('.serverList');
    var server_name = $(this).children('.card-title').children('h2').text();
    var server_img = $(this).children('.card-image').children().attr('src');
    var $imgDiv = $('<img />').attr("src", server_img).css({
        "max-height": "133%",
        "border-radius": "16%",
        "margin-right": "10px",
    });

    // add to serverlist
    var $serverNameDiv = $('<span class="menu-collapsed"/>')
        .text(server_name);
    var $tableCellDiv = $('<a href="#" class="list-group-item list-group-item-action bg-dark text-white">').append(
        $imgDiv).append($serverNameDiv);
    $serverList.append($tableCellDiv.attr('room_id', server_id));

});



