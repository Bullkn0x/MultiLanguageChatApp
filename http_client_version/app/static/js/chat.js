var socket = io.connect('http://localhost:8000', {
    port: 5000,
    rememberTransport: false,
});

$(function () {
    var FADE_TIME = 150; // ms
    var TYPING_TIMER_LENGTH = 400; // ms
    var COLORS = [
        '#e21400', '#91580f', '#f8a700', '#f78b00',
        '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
        '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
    ];



    // Initialize varibles
    var $window = $(window);
    var $usernameInput = $('.usernameInput'); // Input for username
    var $messages = $('.messages'); // Messages area
    var $privateMessages = $('.chats__messages');
    var $inputMessage = $('.inputMessage'); // Input message input box

    var $loginPage = $('.login.page'); // The login page
    var $chatPage = $('.chat.page'); // The chatroom page
    var $navBar = $('.navcontainer');
    var $onlineNumber = $('.online span');
    var $languagePref = $('#language');
    var $serverList = $('.serverList');
    var $serverIconList = $('#serverIcons');
    var $usersList = $('.sidebar-content');
    var $addServerModal = $('#addServer');
    var $uploadModal = $('.uploadModalContainer')
    var $modalServerList = $('.joinServerList');
    



    $('.chats__back').on('click', function () {
        recipient_id = null;
        pm_opened = false;
        socket.emit('pm status', { active_pm_id: null});

        console.log(pm_opened)
        console.log('chat closed');
    });
    
    $('input').on('click', function () {
        $inputMessage = $(this);
        console.log($inputMessage);
        if ($inputMessage.hasClass('direct-message')) {
            directMessage = true;
            recipient_id = $inputMessage.closest('.chats.active').attr('user_id');
            console.log(recipient_id);

        } else {
            directMessage = false;
        }
        console.log(directMessage);
    });


    function updateOnline(data) {
        $('#onlineUsers').append('<li>' + data.username + '</li>');
        $onlineNumber.text(data.numUsers);
    }



    // DROPDOWN TOGGLE
    $('.dropdown-menu a').on('click', function () {
        $('.dropdown-toggle').html($(this).html());
        changeLanguage();
    })
    function changeLanguage() {
        var language = $languagePref.text().toLowerCase().trim();
        socket.emit('change language', language);
    }

 


    $usersList.on('click', 'div', function () {
        pm_opened = true;
        recipient_id = $(this).attr('user_id');
        socket.emit('pm status', { active_pm_id: recipient_id });

    });
    // Sends a chat message
    function sendMessage() {
        var message = $inputMessage.val();

        var roomid = $messages.attr('room_id');
        console.log(roomid);
        // Prevent markup from being injected into the message
        message = cleanInput(message);
        console.log(message);
        // if there is a non-empty message and a socket connection
        if (message && connected) {
            $inputMessage.val('');

            if (directMessage) {
                var $pmMsgBody = $('<div class="chats__message mine" />').text(message);
                var $pmMsgDiv = $('<div class="chats__msgRow" />').append($pmMsgBody);
                $privateMessages.append($pmMsgDiv);
                $privateMessages[0].scrollTop = $privateMessages[0].scrollHeight;
                socket.emit('private message', {
                    room_id: roomid,
                    recipient_id: recipient_id,
                    message: message
                });


              
            } else {
                addChatMessage({
                    username: username,
                    message: message
                });
                // tell server to execute 'new message' and send along one parameter
                socket.emit('new message', {
                    message: message,
                    room_id: roomid
                });
            }
        }
    }

    // Log a message
    function log(message, options) {
        var $el = $('<li>').addClass('log').text(message);
        addMessageElement($el, options);

    }

    // Adds the visual chat message to the message list
    function addChatMessage(data, options) {
        // Don't fade the message in if there is an 'X was typing'
        var $typingMessages = getTypingMessages(data);
        options = options || {};
        if ($typingMessages.length !== 0) {
            options.fade = false;
            $typingMessages.remove();
        }
        var $usernameDiv = $('<span class="username"/>')
            .text(data.username)
            .css('color', '#1DB6EF');
        //getUsernameColor(data.username)
        var $messageBodyDiv = $('<span class="messageBody">')
            .html(linkify(data.message || ' '));


        if (options.file) {
            var fileDiv = '<div class="fileBox"><p>' + data.filename + '</p>' +
                '<div class="downloadContainer">' +
                '<a href="' + data.file_url + '" class="downloadButton dark-single">' +
                '<div><svg viewBox="0 0 24 24"></svg></div></a></div></div>'
        }
        var typingClass = data.typing ? 'typing' : '';
        var $messageDiv = $('<li class="message"/>')
            .data('username', data.username)
            .addClass(typingClass)
            .append($usernameDiv, $messageBodyDiv, fileDiv || null);

        addMessageElement($messageDiv, options);

        if (options.file) {
            listenDownload();
        }
    }
    function linkify(inputText) {
        var replacedText, replacePattern1, replacePattern2, replacePattern3;

        //URLs starting with http://, https://, or ftp://
        replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
        replacedText = inputText.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

        //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
        replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
        replacedText = replacedText.replace(replacePattern2, '$1<a id="link" href="http://$2" target="_blank">$2</a>');

        //Change email addresses to mailto:: links.
        replacePattern3 = /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
        replacedText = replacedText.replace(replacePattern3, '<a href="mailto:$1">$1</a>');

        return replacedText;
    }
    // Adds the visual chat typing message
    function addChatTyping(data) {
        data.typing = true;
        data.message = 'is typing';
        addChatMessage(data);
    }

    // Removes the visual chat typing message
    function removeChatTyping(data) {
        getTypingMessages(data).fadeOut(function () {
            $(this).remove();
        });
    }

    function listenDownload() {
        document.querySelectorAll('.downloadButton').forEach(button => {
            let duration = 3000,
                svg = button.querySelector('svg'),
                svgPath = new Proxy({
                    y: null,
                    smoothing: null
                }, {
                    set(target, key, value) {
                        target[key] = value;
                        if (target.y !== null && target.smoothing !== null) {
                            svg.innerHTML = getPath(target.y, target.smoothing, null);
                        }
                        return true;
                    },
                    get(target, key) {
                        return target[key];
                    }
                });

            button.style.setProperty('--duration', duration);

            svgPath.y = 20;
            svgPath.smoothing = 0;

            button.addEventListener('click', e => {
                e.preventDefault();
                if (!button.classList.contains('loading')) {

                    button.classList.add('loading');

                    gsap.to(svgPath, {
                        smoothing: .3,
                        duration: duration * .065 / 1000
                    });

                    gsap.to(svgPath, {
                        y: 12,
                        duration: duration * .265 / 1000,
                        delay: duration * .065 / 1000,
                        ease: Elastic.easeOut.config(1.12, .4)
                    });

                    setTimeout(() => {
                        svg.innerHTML = getPath(0, 0, [
                            [3, 14],
                            [8, 19],
                            [21, 6]
                        ]);



                    }, duration / 2);
                    setTimeout(() => {

                        location.href = button.href;
                    }, duration);


                }

            });

        });

        function getPoint(point, i, a, smoothing) {
            let cp = (current, previous, next, reverse) => {
                let p = previous || current,
                    n = next || current,
                    o = {
                        length: Math.sqrt(Math.pow(n[0] - p[0], 2) + Math.pow(n[1] - p[1], 2)),
                        angle: Math.atan2(n[1] - p[1], n[0] - p[0])
                    },
                    angle = o.angle + (reverse ? Math.PI : 0),
                    length = o.length * smoothing;
                return [current[0] + Math.cos(angle) * length, current[1] + Math.sin(angle) * length];
            },
                cps = cp(a[i - 1], a[i - 2], point, false),
                cpe = cp(point, a[i - 1], a[i + 1], true);
            return `C ${cps[0]},${cps[1]} ${cpe[0]},${cpe[1]} ${point[0]},${point[1]}`;
        }

        function getPath(update, smoothing, pointsNew) {
            let points = pointsNew ? pointsNew : [
                [4, 12],
                [12, update],
                [20, 12]
            ],
                d = points.reduce((acc, point, i, a) => i === 0 ? `M ${point[0]},${point[1]}` : `${acc} ${getPoint(point, i, a, smoothing)}`, '');
            return `<path d="${d}" />`;
        }

    }


    // Adds a message element to the messages and scrolls to the bottom
    // el - The element to add as a message
    // options.fade - If the element should fade-in (default = true)
    // options.prepend - If the element should prepend
    //   all other messages (default = false)
    function addMessageElement(el, options) {
        var $el = $(el);

        // Setup default options
        if (!options) {
            options = {};
        }
        if (typeof options.fade === 'undefined') {
            options.fade = true;
        }
        if (typeof options.prepend === 'undefined') {
            options.prepend = false;
        }

        // Apply options
        if (options.fade) {
            $el.hide().fadeIn(FADE_TIME);
        }
        if (options.prepend) {
            if ($messages.children('.log').length > 0) {
                $messages.children('.log').html($el);
            } else {
                $messages.prepend($el);
            }
        }

        else {
            $messages.append($el);
        }
        $messages[0].scrollTop = $messages[0].scrollHeight;
    }

    // Prevents input from having injected markup
    function cleanInput(input) {
        return $('<div/>').text(input).text();
    }

    // Updates the typing event
    function updateTyping() {
        if (connected) {
            if (!typing) {
                typing = true;
                socket.emit('typing');
            }
            lastTypingTime = (new Date()).getTime();

            setTimeout(function () {
                var typingTimer = (new Date()).getTime();
                var timeDiff = typingTimer - lastTypingTime;
                if (timeDiff >= TYPING_TIMER_LENGTH && typing) {
                    socket.emit('stop typing');
                    typing = false;
                }
            }, TYPING_TIMER_LENGTH);
        }
    }

    // Gets the 'X is typing' messages of a user
    function getTypingMessages(data) {
        return $('.typing.message').filter(function (i) {
            return $(this).data('username') === data.username;
        });
    }

    // Gets the color of a username through our hash function
    // function getUsernameColor(username) {
    //     // Compute hash code
    //     var hash = 7;
    //     for (var i = 0; i < username.length; i++) {
    //         hash = username.charCodeAt(i) + (hash << 5) - hash;
    //     }
    //     // Calculate color
    //     var index = Math.abs(hash % COLORS.length);
    //     return COLORS[index];
    // }

    // Keyboard events

    $window.keydown(function (event) {
        // console.log(event.target.className);
        // When the client hits ENTER on their keyboard, 13 is Enter

        if (event.which === 13) {
            if (username) {
                if (event.target.id == 'search-input') {
                    console.log('searc babyyy');
                } else if (event.target.id =='serverName') {
                    console.log('Your Social Security Number is being tracked!');
                } else {
                    sendMessage();
                    socket.emit('stop typing');
                    typing = false;
                }
            }
        }
    });

    $inputMessage.on('input', function () {
        updateTyping();
    });

    //  FILE TRANSFER 
    const chunk_size = 64 * 1024;
    var files = [];
    var dropzone = document.getElementById('dropzone');

    var lastTarget = null;

    function isFile(evt) {
        var dt = evt.dataTransfer;

        for (var i = 0; i < dt.types.length; i++) {
            if (dt.types[i] === "Files") {
                return true;
            }
        }
        return false;
    }
    window.addEventListener("dragenter", function (e) {
        if (isFile(e)) {
            lastTarget = e.target;
            document.querySelector("#textnode").src = "https://anychatio.s3.amazonaws.com/helloFile.svg";
            document.querySelector("#dropzone").style.visibility = "";
            document.querySelector("#dropzone").style.opacity = 1;
        }
    });
    dropzone.ondragover = function (e) {
        e.preventDefault();
    }

    window.addEventListener("dragleave", function (e) {
        e.preventDefault();

        if (e.target === lastTarget || e.target === document) {
            document.querySelector("#textnode").src = null;
            document.querySelector("#dropzone").style.visibility = "hidden";
            document.querySelector("#dropzone").style.opacity = 0;
        }
    });

    dropzone.ondrop = function (e) {
        $('#textnode').hide();

        $uploadModal.addClass('animated fadeIn').show();

        // document.querySelector("#textnode").src = null;
        //     document.querySelector("#dropzone").style.visibility = "hidden";
        //     document.querySelector("#dropzone").style.opacity = 0;
        e.preventDefault();
        for (var i = 0; i < e.dataTransfer.files.length; i++) {
            filediv = document.createElement('div');
            filename = document.createElement('div');
            filename.classList.add('filename');
            filename.innerHTML = e.dataTransfer.files[i].name;
            progress = document.createElement('div');
            progress.classList.add('file-progress');
            progress.classList.add('in-progress');
            filediv.appendChild(filename);
            filediv.appendChild(progress);
            document.getElementById('filelist').appendChild(filediv);
            files.push({
                file: e.dataTransfer.files[i],
                progress: progress,
                done: false
            });
        }
    }
    function readFileChunk(file, offset, length, success, error) {
        end_offset = offset + length;
        if (end_offset > file.size)
            end_offset = file.size;
        var r = new FileReader();
        r.onload = function (file, offset, length, e) {
            if (e.target.error != null)
                error(file, offset, length, e.target.error);
            else
                success(file, offset, length, e.target.result);
        }.bind(r, file, offset, length);
        r.readAsArrayBuffer(file.slice(offset, end_offset));
    }

    // read success callback
    function onReadSuccess(file, offset, length, data) {
        if (this.done)
            return;
        if (!socket.connected) {
            // the WebSocket connection was lost, wait until it comes back
            setTimeout(onReadSuccess.bind(this, file, offset, length, data), 5000);
            return;
        }
        socket.emit('write-chunk', this.server_filename, offset, data, function (offset, ack) {
            if (!ack)
                onReadError(this.file, offset, 0, 'Transfer aborted by server')
        }.bind(this, offset));
        end_offset = offset + length;
        this.progress.style.width = parseInt(300 * end_offset / file.size) + "px";
        if (end_offset < file.size)
            readFileChunk(file, end_offset, chunk_size,
                onReadSuccess.bind(this),
                onReadError.bind(this));
        else {
            this.progress.classList.add('complete');
            this.progress.classList.remove('in-progress');
            this.done = true;
            socket.emit('upload', { server_filename: this.server_filename, file_title: this.file.name })
        }
    }

    // read error callback
    function onReadError(file, offset, length, error) {
        console.log('Upload error for ' + file.name + ': ' + error);
        this.progress.classList.add('error');
        this.progress.classList.remove('in-progress');
        this.done = true;
    }

    // upload button
    var upload = document.getElementById('upload');
    upload.onclick = function () {
        if (files.length == 0)
            alert('Drop some files above first!');
        for (var i = 0; i < files.length; i++) {
            socket.emit('start-transfer', files[i].file.name, files[i].file.size, function (filename) {
                if (!filename) {
                    // the server rejected the transfer
                    onReadError.call(this, this.file, 0, 0, 'Upload rejected by server')
                }
                else {
                    // the server allowed the transfer with the given filename
                    this.server_filename = filename;
                    readFileChunk(this.file, 0, chunk_size,
                        onReadSuccess.bind(this),
                        onReadError.bind(this));
                }
            }.bind(files[i]));
        }
        files = [];
    }



















    // Click events




    // Socket events
    function setUser(data) {
        username = data.username;
    }



    // SERVER EVENTS 

    // Whenever the server emits 'connect', log the connect message
    socket.on('login', function (data) {
        connected = true;
        username = data.username
        // Display the welcome message
        var message = "Welcome to AnyChat :) ";
        log(message, {
            prepend: true
        });
        updateOnline(data);
    });

    // Whenever the server emits 'new message', update the chat body
    socket.on('new message', function (data) {
        console.log(data);
        addChatMessage(data);
    });


    socket.on('pm log', function (data) {
        $privateMessages.html('');
        data.forEach(function (userMessage) {
            if (userMessage.mymsg) {
                var $pmMsgBody = $('<div class="chats__message mine" />').text(userMessage.message);
                var $pmMsgDiv = $('<div class="chats__msgRow" />').append($pmMsgBody);
                $privateMessages.append($pmMsgDiv);

            } else {
                var $pmMsgBody = $('<div class="chats__message notMine" />').text(userMessage.message);
                var $pmMsgDiv = $('<div class="chats__msgRow" />').append($pmMsgBody);
                $privateMessages.append($pmMsgDiv);

            }
        });

    });
    socket.on('new private message', function (data) {
        sender_id = data.sender_id.toString();
        console.log(recipient_id == sender_id);
        // user has the private chat from sender open
        if (pm_opened && recipient_id == sender_id) {
            var $pmMsgBody = $('<div class="chats__message notMine" />').text(data.message);
            var $pmMsgDiv = $('<div class="chats__msgRow" />').append($pmMsgBody);
            $privateMessages.append($pmMsgDiv);
            $privateMessages[0].scrollTop = $privateMessages[0].scrollHeight;


            console.log(data);
        }
    });

    // Whenever the server emits 'user joined', log it in the chat body
    socket.on('user joined', function (data) {
        log(data.username + ' joined');
        updateOnline(data);
    });

    // Whenever the server emits 'chat log' Append chat log to message box
    socket.on('join server', function (data) {
        $messages.html('');
        $usersList.html('');
        messages = data.chat_log;
        var room_id = data.server_id;
        var room_name = data.server_name;
        $messages.attr('room_id', room_id)
        messages.forEach(function (data) {

            addChatMessage(data)
        });
        var join_room_message = "You have joined " + room_name;
        log(join_room_message, {
            prepend: true
        });
        data.server_users.forEach(function (user) {
            var $userImg = $('<img />', { "class": "contact__photo" }).attr("src", 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/142996/elastic-man.png');
            var $username = $('<span/>', { "class": "contact__name" }).text(user.username);
            var $userStatus = $('<span/>', { "class": "contact__status" }).addClass(user.status);
            var $userDiv = $(' <div/>', { "class": "contact" }).attr('user_id', user.user_id).append($userImg).append($username).append($userStatus);
            if (user.status == 'offline') $userDiv.css('opacity', 0.2);
            $usersList.append($userDiv);
        });
    });

    // Whenever the server emits 'stop typing', kill the typing message
    socket.on('server info', function (data) {
        // console.log(serverList)
        $usersList.html('');
        
        data.server_users.forEach(function (user) {
            var $userImg = $('<img />', { "class": "contact__photo" }).attr("src", 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/142996/elastic-man.png');
            var $username = $('<span/>', { "class": "contact__name" }).text(user.username);
            var $userStatus = $('<span/>', { "class": "contact__status" }).addClass(user.status);

            var $userDiv = $(' <div/>', { "class": "contact" }).attr('user_id', user.user_id).append($userImg).append($username).append($userStatus);
            if (user.status == 'offline') $userDiv.css('opacity', 0.2);
            $usersList.append($userDiv);
        });
    });



    // Whenever the server emits 'user left', log it in the chat body
    socket.on('user left', function (data) {
        console.log(data);
        log(data.username + ' left');
        updateOnline(data);
        removeChatTyping(data);
    });

    // Whenever the server emits 'typing', show the typing message
    socket.on('typing', function (data) {
        addChatTyping(data);
    });

    // Whenever the server emits 'stop typing', kill the typing message
    socket.on('stop typing', function (data) {
        removeChatTyping(data);
    });
    socket.on('file link', function (data) {
        console.log(data.file_url);
        addChatMessage(data, { file: true });
    });



    // Server Modal Actions

  

});





