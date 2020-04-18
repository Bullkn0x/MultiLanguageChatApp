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

    // bind window resize to manually adjust card image height, in order to maintain required aspect ratio of card images
    $(window).resize(function () {
        setCardImgHeight();
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


$('#searchTopServers').on('click', function() {
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

        $("#cards").append(makeServerCard(servers));
        // manually set height of card images, since the width is already known
    } else {
        $("#cards").append(encapsulate("No results found", "p", ""));
    }
    
     

});

// Build cards elements from 'search results' array
function makeServerCard(search_results) {
    var html = "";
    search_results.forEach(function (server) {
        var imgSrc = server.room_logo_url || "https://placehold.it/200x150/e6e6e6?text=Image+unavailable"
        // build elements to be appended to #cards
        var image = encapsulate(false, "img", "src='" + imgSrc + "' alt='Server image for " + server.room_name + "'");
        var imageDiv = encapsulate(image, "div", "class='card-image'");
        var title = encapsulate(server.room_name, "h2", "");
        var titleDiv = encapsulate(title, "div", "class='flex card-title'");
        var action = encapsulate("More Info", "a", "room_id=" + server.room_id);
        var actionDiv = encapsulate(action, "div", "class='flex card-actions'");
        html = html + encapsulate(imageDiv + titleDiv + actionDiv, "div", "class='flex-col card'");
    });

    return html;
}

// wrap content in given html tags, with given attributes
function encapsulate(content, tag, attr) {
    if (false === content) {
        return "<" + tag + " " + attr + " />";
    } else {
        return '<' + tag + " " + attr + '>' + content + '</' + tag + '>';
    }
}



