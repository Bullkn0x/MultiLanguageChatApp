

var $serverIconsList = $('#serverIcons')
var focusedMessageContent;
// contextMenu templates
var serverListTemplate = {
    items: {
        "button1": {
            name: "Invite People",
            styles: {
                "color": "#6279ff",
                "font-weight": "bold"
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
        "button4": { name: "Custom Server Color" },
        
        "divider2": {},
        
        "button7": { 
            name: "Leave Server" ,
            styles: {
                "color": "#f02929"
            },
            class : "leaveServer"
        },
    }
}

var chatAreaTemplate = {
    items: {
        "button1": { name: "Edit Message"},
       
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
            name: "Delete Message" ,
            styles: {
                "color": "#f02929"
            }
        },
    }
}


function makeContext(parent, structure) {

    function makeItem(details) {
        
        var $itemDiv = $('<li/>').addClass('contextItem').addClass(details.class)
            .append(
                $('<a/>')
                    .append(details.name))
        
        // add css if details.styles exists supplied with style object 
        if (details.styles) {
            $itemDiv.css(details.styles)
        }
        return $itemDiv
    }

    function makeFolder(details) {
        var $folderDiv = makeItem(details.foldername);
        var $subMenu = $('<ul/>').addClass('context submenu')
        var $subMenuTotal = makeContext($subMenu, details)
        return $folderDiv.append($subMenu);


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
var $chatContextDiv =$('<ul/>').addClass('context');
var $chatContextMenu = makeContext($chatContextDiv, chatAreaTemplate)



$(function () {

    var $doc = $(window),
        // original context menu
        $context = $(".context:not(.submenu)");

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
        
        if (($sub).length){
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

        $doc.on("mousedown", function (e) {

            var $tar = $(e.target);
            $tar.addClass('asdlfjasdhfilasndkihgasdfiuaklsdhgasifiuasgfia')
            if (!$tar.is(menuSelector) && !$tar.closest(".context").length) {
                menuSelector.removeClass("is-visible").children().removeClass('contextItem--active');
                $doc.off(e);

            }

        });


    }

   $(document).on("mousedown touchstart", ".contextItem:not(.contextItem--nope)", function (e) {
        console.log(focusedMessageContent.text());
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
    $serverIconsList.on("contextmenu", 'a', function (e) {
        
        // console.log('rightclicked on server with room_i', $(this).attr('room_id'));
        openContextMenu($serverContextMenu, e);
    });

    $('.chatArea').on("contextmenu", ".message", function (e) {
        focusedMessageContent = $(this)
        openContextMenu($chatContextMenu, e);
    });

    $(document).on('click', '.msgCopy', function() {
        copyToClipboard(focusedMessageContent.children('.messageBody'));
    })
});


















