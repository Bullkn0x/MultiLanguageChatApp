

var $serverIconsList = $('#serverIcons')
// var focusedMessageContent;
// var focusedServer;
// contextMenu templates
var serverListTemplate = {
    items: {
        "button1": {
            name: "Invite People",
            styles: {
                "color": "#6279ff",
                "font-weight": "bold"
            },
            icon: {
                position: "iconLeft",
                iconCode: "fas fa-user-friends"
            }
        },
        "folder1": {
            foldername: { name: "Quick Invite" },
            items: {
                "button1": { name: "Qi" },
                "button2": { name: "Anychat" },
            }
        },
        "divider1": {},
        "button2": { name: "Server Settings" },
        "button3": { name: "Privacy Settings" },
        "button4": { name: "Change Nickname" },
        "folder2": {
            foldername: { name: "Custom Server Color", class: "colorPickerMenu" },

            items: {
                "button1": {
                    type: "color",
                    name: "Red",
                    class: "redBtn"
                },
                "button2": {
                    type: "color",
                    name: "Blue",
                    class: "blueBtn"
                },
                "button3": {
                    type: "color",
                    name: "Green",
                    class: "greenBtn"
                },
                "button4": {
                    type: "color",
                    name: "Yellow",
                    class: "yellowBtn"
                },
                "button5": {
                    type: "color",
                    name: "Pink",
                    class: "pinkBtn"
                },

            }
        },

        "divider2": {},

        "button7": {
            name: "Leave Server",
            styles: {
                "color": "#f02929"
            },
            class: "leaveServer"
        },
    }
}

var chatAreaTemplate = {
    items: {
        "button1": { name: "Edit Message" },

        "button2": {
            name: "Copy Message",
            class: "msgCopy"
        },
        "button3": {
            name: "Link to Message",
            class: "msgCopy"
        },

        "divider2": {},

        "button4": {
            name: "Delete Message",
            class: "msgDelete",
            styles: {
                "color": "#f02929"
            }
        },
    }
}


function makeContext(parent, structure) {

    function makeItem(details) {
        var $itemDiv = $('<li/>').addClass('contextItem')
            .addClass(details.class)
            .append(
                $('<a/>')
                    .append(details.name))

        // add css if details.styles exists supplied with style object 
        let icon = details.icon
        if (icon) {
            let iconLoc;
            iconLoc = details.icon.position
            $itemDiv.addClass(iconLoc)
            if (iconLoc == 'iconLeft') {
                $itemDiv.prepend($('<i/>').addClass(icon.iconCode))
            }
        }

        if (details.type == 'color') {
            $itemDiv.append($('<i/>').addClass(details.type).css('background-color', details.color))
        }
        if (details.styles) {
            $itemDiv.css(details.styles)
        }
        return $itemDiv
    }

    function makeFolder(details) {
        var $folderDiv = makeItem(details.foldername).addClass('folder');
        var $subMenu = $('<ul/>').addClass('context submenu').addClass(details.class)
        var $subMenuTotal = makeContext($subMenu, details)
        return $folderDiv.append($('<i/>').addClass('fas fa-angle-right'), $subMenu);


    }


    $.each(structure.items, function (type, details) {
        if (~type.indexOf("button")) {
            var $itemDiv = makeItem(details);
            parent.append($itemDiv);
        }
        else if (~type.indexOf("folder")) {

            var $folderDiv = makeFolder(details);
            parent.append($folderDiv)
        }
        else if (~type.indexOf("divider")) {
            parent.append($('<li/>').addClass('contextDivider'))
        }

    })
    return parent

}

// Create ContextDivs
var $contextDiv = $('<ul/>').addClass('context');
var $serverContextMenu = makeContext($contextDiv, serverListTemplate)
var $chatContextDiv = $('<ul/>').addClass('context');
var $chatContextMenu = makeContext($chatContextDiv, chatAreaTemplate)



$(function () {

    var $doc = $(window),
        // original context menu
        $context = $(".context:not(.submenu)");

    function ditchWindow(menu) {
        menu.children().removeClass('contextItem--active');
        menu.remove();
    };

    function openContextMenu(menuSelector, e) {
        $('body').append(menuSelector);

        var $window = $(window),
            $sub = menuSelector.find(".submenu");


        $sub.removeClass("oppositeX oppositeY");

        e.preventDefault();

        var w = menuSelector.width();
        var h = menuSelector.height();
        var x = e.clientX;
        var y = e.clientY;
        var ww = $window.width();
        var wh = $window.height();
        var padx = 30;
        var pady = 20;
        var fx = x;
        var fy = y;
        var hitsRight = (x + w >= ww - padx);
        var hitsBottom = (y + h >= wh - pady);

        if (hitsRight) {
            fx = ww - w - padx;
        }

        if (hitsBottom) {
            fy = wh - h - pady;
        }

        menuSelector
            .css({
                left: fx - 1,
                top: fy - 1
            });

        if (($sub).length) {
            var sw = $sub.width();
            var sh = $sub.height();
            var sx = $sub.offset().left;
            var sy = $sub.offset().top;
            var subHitsRight = (sx + sw - padx >= ww - padx);
            var subHitsBottom = (sy + sh - pady >= wh - pady);
        }
        if (subHitsRight) {
            $sub.addClass("oppositeX");
        }

        if (subHitsBottom) {
            $sub.addClass("oppositeY");
        }

        menuSelector.addClass("is-visible");


        // menu Clicks!!!!

        // copy Message
        menuSelector.on('click', '.msgCopy', function () {
            copyToClipboard(focusedMessageContent.children('.messageBody'));
            ditchWindow(menuSelector);
        });


        // Delete Message
        menuSelector.on('click', '.msgDelete', function () {
            let message_id = focusedMessageContent.attr('message_id')
            socket.emit('message update', {
                operation: 'delete',
                message_id: parseInt(message_id)
            });
            ditchWindow(menuSelector);

        });


        // Server Change Color 
        menuSelector.on('click', '.colorPickerMenu li', function () {
            console.log($(this).children('i').css('background-color'));
            var setServerColor = $(this).children('i').css('background-color')
            focusedServer.children('img').css('border-color', setServerColor);
            let room_id = parseInt(focusedServer.attr('room_id'));
            socket.emit('server update', {
                operation: 'update_color',
                room_id: room_id,
                color: setServerColor
            });
        });

        // Leave Server (Open Double check confirm Modal)
        menuSelector.on('click', '.leaveServer', function () {
            
            let room_id = focusedServer.attr('room_id');
            let leave_room_name = focusedServer.attr('room_name');
            $('#leaveServerName').text(leave_room_name);
            $leaveModal.css('display', 'flex');
            ditchWindow(menuSelector)
        });


        // Click off of the menu, cya bro
        $doc.on("mousedown", function (e) {

            var $tar = $(e.target);
            if (!$tar.is(menuSelector) && !$tar.closest(".context").length) {
                ditchWindow(menuSelector);
                // menuSelector.removeClass("is-visible").children().removeClass('contextItem--active');
                $doc.off(e);

            }

        });


    }

    $(document).on("mousedown touchstart", ".contextItem:not(.contextItem--nope)", function (e) {
        let $tar = e.target;
        if (e.which === 1) {
            var $item = $(this);
            setTimeout(function () {
                $item.addClass("contextItem--active");
            }, 10);
            $(this).removeClass("contextItem--active");


        }

    });

    function copyToClipboard(element) {
        var $temp = $("<input>");
        $("body").append($temp);
        $temp.val($(element).text()).select();
        document.execCommand("copy");
        $temp.remove();
    }



    // Listeners  

    // Message Right Click 
    $('.chatArea').on("contextmenu", ".message", function (e) {
        focusedMessageContent = $(this)
        openContextMenu($chatContextMenu, e);
    });


    // Server Icon Right Click
    $serverIconsList.on("contextmenu", 'a', function (e) {
        focusedServer = $(this);
        openContextMenu($serverContextMenu, e);
    });

    








    // Socket Events
    socket.on('message update', function (data) {
        console.log(data)
        console.log($(".message[message_id=" + data.message_id + "]").length);
        if (data.operation == 'delete') {
            console.log('deleting');
            $(".message[message_id=" + data.message_id + "]").remove();
        }
    })
    socket.on('server update', function (data) {
        console.log(data)
        console.log($(".message[message_id=" + data.message_id + "]").length);
        if (data.operation == 'update_color') {
            $("#serverIcons a[room_id=" + data.room_id + "]")
                .children('img').css('border-color', data.color);
        }
    })
});


















